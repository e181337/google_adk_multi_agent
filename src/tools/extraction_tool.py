import json
from typing import Any

from google import genai

from src.config import get_google_settings, get_model_settings
from src.prompts.entity_extraction_prompt import ENTITY_EXTRACTION_TOOL_INSTRUCTION


EXPECTED_KEYS = {
    "customer_name",
    "email",
    "phone",
    "membership_type",
    "vehicle_model",
    "vehicle_identification_number",
    "charging_station",
    "accident_location",
    "accident_type",
}


def _check_type(data: Any, data_name: str, data_type: type) -> None:
    if not isinstance(data, data_type):
        raise TypeError(f"{data_name} is not {data_type}")


def _validate_input(text: str) -> None:
    _check_type(text, "text", str)
    if text.strip() == "":
        raise ValueError("text is empty")


def _build_user_prompt(text: str) -> str:
    return f"""
Extract entities from the following text.

Text:
{text}
"""


def _build_client() -> genai.Client:
    google_settings = get_google_settings()

    if google_settings.genai_use_vertexai:
        return genai.Client(
            vertexai=True,
            project=google_settings.cloud_project,
            location=google_settings.cloud_location,
        )

    return genai.Client()


def entity_extraction_tool(text: str) -> dict[str, Any]:
    _validate_input(text)

    model_settings = get_model_settings()
    client = _build_client()
    user_prompt = _build_user_prompt(text)

    response = client.models.generate_content(
        model=model_settings.extraction_model,
        contents=user_prompt,
        config={
            "system_instruction": ENTITY_EXTRACTION_TOOL_INSTRUCTION,
            "temperature": 0,
            "response_mime_type": "application/json",
        },
    )

    if response.text is None or response.text.strip() == "":
        raise RuntimeError("empty response from entity extraction model")

    try:
        parsed = json.loads(response.text)
    except json.JSONDecodeError as e:
        raise ValueError(f"entity extraction json parse error: {e}")

    _check_type(parsed, "parsed", dict)

    key_set = set(parsed.keys())
    if key_set != EXPECTED_KEYS:
        raise ValueError("unexpected keys in entity extraction output")

    for key, value in parsed.items():
        if value is not None:
            _check_type(value, key, str)

    return parsed
