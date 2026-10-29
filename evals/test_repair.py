
import sys
from pathlib import Path
from unittest.mock import patch

from pydantic import ValidationError
from fastapi.testclient import TestClient

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from main import app
from triage_service import classify_message

invalid_response = '{"category":"payment","urgency":"normal","confidence":0.9,"reason":"Payment problem."}'

valid_response = '{"category":"billing","urgency":"normal","confidence":0.9,"reason":"Customer reports a billing problem."}'

with patch.dict(
    "os.environ",
    {"LLM_STUB": "0", "LLM_ENABLED": "true"},
):
    with patch("triage_service.get_triage_client", return_value=None):
        with patch(
            "triage_service.call_model",
            side_effect=[invalid_response, valid_response],
        ) as mock_call:
            result = classify_message("I was charged twice.")

            print("Category:", result.category.value)
            print("Urgency:", result.urgency.value)
            print("Model calls:", mock_call.call_count)

            assert result.category.value == "billing"
            assert mock_call.call_count == 2

            print("REPAIR TEST PASSED")




print("\nTesting two invalid AI responses...")

with patch.dict(
    "os.environ",
    {"LLM_STUB": "0", "LLM_ENABLED": "true"},
):
    with patch("triage_service.get_triage_client", return_value=None):
        with patch(
            "triage_service.call_model",
            side_effect=[invalid_response, invalid_response],
        ) as mock_call:
            try:
                classify_message("I was charged twice.")
                print("TEST FAILED: Invalid output was accepted")

            except ValidationError:
                assert mock_call.call_count == 2
                print("Model calls:", mock_call.call_count)
                print("DOUBLE INVALID RESPONSE TEST PASSED")


print("\nTesting API response for invalid AI output...")

client = TestClient(app)

with patch("main.classify_message", side_effect=ValidationError.from_exception_data("TriageResult", [])):
    response = client.post(
        "/triage",
        json={"text": "I was charged twice."},
    )

    print("HTTP status:", response.status_code)
    print("Response:", response.json())

    assert response.status_code == 422
    assert "raw_output" not in response.text

    print("API 422 TEST PASSED")
