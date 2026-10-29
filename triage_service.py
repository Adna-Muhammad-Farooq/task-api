
import json
import logging
import os
import random
import re
import time

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from openai import (
    APIStatusError,
    APITimeoutError,
    OpenAI,
    RateLimitError,
)
from pydantic import ValidationError

from triage_client import (
    get_triage_client,
    load_triage_prompt,
    MODEL_NAME,
    PROMPT_VERSION,
)
from triage_models import (
    TriageCategory,
    TriageResult,
    TriageUrgency,
)


logger = logging.getLogger("triage")
MAX_ATTEMPTS = 3


def fallback_result() -> TriageResult:
    """Return a safe result without calling the AI."""
    return TriageResult(
        category=TriageCategory.OTHER,
        urgency=TriageUrgency.NORMAL,
        confidence=0.0,
        reason=(
            "Automatic classification is unavailable; "
            "manual review is needed."
        ),
    )


def parse_result(raw_text: str) -> TriageResult:
    """Extract JSON and validate all output fields."""
    text = raw_text.strip()

    # Remove Markdown code fences if present.
    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\s*```$", "", text)

    # Extract the JSON object.
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)

    if not match:
        raise ValueError("No JSON object found in model output")

    return TriageResult.model_validate_json(match.group(0))


def call_model(
    client: OpenAI,
    messages: list[dict[str, str]],
    repair_count: int,
) -> str:
    """Retry only timeouts, HTTP 429, and HTTP 5xx responses."""

    for attempt in range(MAX_ATTEMPTS):
        started = time.perf_counter()

        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=0.1,
            )

            duration_ms = round(
                (time.perf_counter() - started) * 1000
            )

            usage = response.usage

            logger.info(
                json.dumps({
                    "event": "llm_usage",
                    "prompt_version": PROMPT_VERSION,
                    "model": MODEL_NAME,
                    "input_tokens": (
                        usage.prompt_tokens if usage else None
                    ),
                    "output_tokens": (
                        usage.completion_tokens if usage else None
                    ),
                    "duration_ms": duration_ms,
                    "repair_count": repair_count,
                })
            )

            content = response.choices[0].message.content

            if not content:
                raise ValueError("Model returned empty content")

            return content

        except (
            APITimeoutError,
            RateLimitError,
            APIStatusError,
        ) as exc:

            retryable = (
                isinstance(
                    exc,
                    (APITimeoutError, RateLimitError),
                )
                or (
                    isinstance(exc, APIStatusError)
                    and exc.status_code >= 500
                )
            )

            duration_ms = round(
                (time.perf_counter() - started) * 1000
            )

            logger.warning(
                json.dumps({
                    "event": "llm_request_error",
                    "prompt_version": PROMPT_VERSION,
                    "model": MODEL_NAME,
                    "status_code": getattr(
                        exc,
                        "status_code",
                        None,
                    ),
                    "attempt": attempt + 1,
                    "duration_ms": duration_ms,
                    "repair_count": repair_count,
                })
            )

            # Do not retry 400, 401, or 403 errors.
            if not retryable or attempt == MAX_ATTEMPTS - 1:
                raise

            # Read Retry-After header if available.
            retry_after = None

            response_obj = getattr(
                exc,
                "response",
                None,
            )

            if response_obj is not None:
                retry_after = response_obj.headers.get(
                    "Retry-After"
                )

            delay = None

            # Retry-After may be seconds or an HTTP date.
            if retry_after:
                try:
                    delay = max(
                        0.0,
                        float(retry_after),
                    )

                except (TypeError, ValueError):
                    try:
                        retry_date = parsedate_to_datetime(
                            retry_after
                        )

                        if retry_date.tzinfo is None:
                            retry_date = retry_date.replace(
                                tzinfo=timezone.utc
                            )

                        delay = max(
                            0.0,
                            (
                                retry_date
                                - datetime.now(timezone.utc)
                            ).total_seconds(),
                        )

                    except (
                        TypeError,
                        ValueError,
                        OverflowError,
                    ):
                        delay = None

            # Use exponential backoff with jitter.
            if delay is None:
                delay = (
                    min(2 ** attempt, 8)
                    + random.uniform(0, 0.5)
                )

            # Maximum waiting time between attempts.
            time.sleep(min(delay, 30))

    raise RuntimeError(
        "Model request attempts exhausted"
    )


def classify_message(message_text: str) -> TriageResult:
    """Classify a message, validate output, and repair once."""

    # Local stub mode: no OpenRouter request.
    if os.getenv("LLM_STUB", "0") == "1":
        return TriageResult(
            category=TriageCategory.OTHER,
            urgency=TriageUrgency.NORMAL,
            confidence=0.5,
            reason=(
                "Stub mode is enabled; "
                "this is a test response."
            ),
        )

    # Kill switch: disable AI requests.
    if os.getenv(
        "LLM_ENABLED",
        "true",
    ).lower() != "true":
        return fallback_result()

    client = get_triage_client()
    system_prompt = load_triage_prompt()

    # Keep user input separate from system instructions.
    user_message = json.dumps(
        {"text": message_text},
        ensure_ascii=False,
    )

    messages: list[dict[str, str]] = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": user_message,
        },
    ]

    repair_count = 0

    # One original response and one repair attempt.
    for validation_attempt in range(2):

        raw_text = call_model(
            client,
            messages,
            repair_count,
        )

        try:
            result = parse_result(raw_text)
            return result

        except (
            ValidationError,
            ValueError,
            json.JSONDecodeError,
        ) as exc:

            # If the repair also fails, quarantine the output.
            if validation_attempt == 1:
                logger.error(
                    json.dumps({
                        "event": "llm_quarantine",
                        "prompt_version": PROMPT_VERSION,
                        "model": MODEL_NAME,
                        "repair_count": repair_count,
                        "reason": str(exc),
                        "raw_output": raw_text[:1000],
                    })
                )

                raise

            # Ask the AI to correct its invalid response.
            repair_count = 1

            messages.extend([
                {
                    "role": "assistant",
                    "content": raw_text,
                },
                {
                    "role": "user",
                    "content": (
                        "Your previous response failed "
                        "JSON/schema validation. "
                        "Correct it using the original "
                        "system instructions. "
                        "Return only one valid JSON object "
                        "with exactly these fields: "
                        "category, urgency, confidence, reason. "
                        "Validation error: "
                        f"{str(exc)[:500]}"
                    ),
                },
            ])

    raise RuntimeError("Classification failed")
