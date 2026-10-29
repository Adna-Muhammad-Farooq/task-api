
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import httpx
from openai import InternalServerError

# Add the main project folder to Python's import path.
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from triage_service import call_model


def test_retry_after_server_error():
    """Test that the AI request retries after a 503 error."""

    # Create a fake HTTP request.
    request = httpx.Request(
        "POST",
        "https://openrouter.ai/api/v1/chat/completions",
    )

    # Simulate a temporary server error.
    error_response = httpx.Response(
        status_code=503,
        request=request,
    )

    server_error = InternalServerError(
        "Temporary server error",
        response=error_response,
        body=None,
    )

    # Create a fake successful AI response.
    successful_response = Mock()
    successful_response.usage.prompt_tokens = 20
    successful_response.usage.completion_tokens = 10
    successful_response.choices = [Mock()]
    successful_response.choices[0].message.content = (
    '{"category":"billing",'
    '"urgency":"normal",'
    '"confidence":0.9,'
    '"reason":"Duplicate charge."}'
)

    # First call fails; second call succeeds.
    client = Mock()

    client.chat.completions.create.side_effect = [
        server_error,
        successful_response,
    ]

    # Avoid real waiting during the test.
    with patch("triage_service.time.sleep") as mock_sleep:
        result = call_model(
            client,
            [
                {
                    "role": "user",
                    "content": "I was charged twice.",
                }
            ],
            repair_count=0,
        )

    # Verify the retry behavior.
    assert client.chat.completions.create.call_count == 2
    assert mock_sleep.call_count == 1
    assert '"billing"' in result

    print(
        "Model calls:",
        client.chat.completions.create.call_count,
    )
    print("Retry waits:", mock_sleep.call_count)
    print("RETRY TEST PASSED")


if __name__ == "__main__":
    test_retry_after_server_error()
