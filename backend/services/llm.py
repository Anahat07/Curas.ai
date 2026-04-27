import re
import json
from typing import TypeVar, Type
from pydantic import BaseModel
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from config import settings

T = TypeVar("T", bound=BaseModel)

_model: Model | None = None


def _extract_json_objects(text: str) -> list[str]:
    """Return all top-level {...} substrings from text using brace counting."""
    results = []
    depth = 0
    start = -1
    in_string = False
    escape = False
    for i, ch in enumerate(text):
        if escape:
            escape = False
            continue
        if ch == "\\" and in_string:
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start != -1:
                results.append(text[start : i + 1])
                start = -1
    return results


def _get_model() -> Model:
    credentials = {
        "url": settings.watsonx_url,
        "apikey": settings.watsonx_api_key,
    }
    return Model(
        model_id=settings.granite_model_id,
        credentials=credentials,
        project_id=settings.watsonx_project_id,
        params={
            GenParams.MAX_NEW_TOKENS: 1024,
            GenParams.TEMPERATURE: 0.1,
        },
    )


async def generate(
    prompt: str,
    system: str = "",
    response_model: Type[T] | None = None,
    max_tokens: int = 1024,
) -> T | str:
    global _model
    if _model is None:
        try:
            _model = _get_model()
        except Exception as e:
            raise LLMError(f"Failed to initialise watsonx model: {e}") from e

    if response_model is not None:
        schema = json.dumps(response_model.model_json_schema(), indent=2)
        system = (
            system
            + f"\n\nReturn ONLY a valid JSON object matching this schema. "
            f"No markdown fences, no prose, no explanation.\nSchema:\n{schema}"
        )

    messages = []
    if system:
        prompt = f"{system}\n\n{prompt}"

    try:
        response = _model.generate_text(
            prompt=prompt,
            params={GenParams.MAX_NEW_TOKENS: max_tokens},
        )
    except Exception as e:
        raise LLMError(f"watsonx call failed: {e}") from e

    if isinstance(response, str):
        raw = response.strip()
    else:
        raw = response["results"][0]["generated_text"].strip()

    if response_model is None:
        return raw

    # Strip markdown fences first
    clean = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()

    # Extract all top-level {...} blocks by brace-counting, try each against the model.
    # The model sometimes emits the schema block followed by the actual answer, so we
    # try every candidate and return the last one that validates.
    candidates = _extract_json_objects(clean)
    last_err: Exception | None = None
    for candidate in reversed(candidates):
        try:
            return response_model.model_validate_json(candidate)
        except Exception as e:
            last_err = e

    raise LLMError(
        f"Failed to parse Granite response into {response_model.__name__}: {last_err}\nRaw: {raw}"
    ) from last_err


class LLMError(Exception):
    """Raised on non-2xx watsonx response or unparseable JSON output."""
    ...
