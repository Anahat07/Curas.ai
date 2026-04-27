from pydantic import BaseModel
from models.soap_note import SOAPContent, BillingCode
from services import llm

SOAP_SYSTEM_PROMPT = """
You are a medical scribe. Given the current SOAP note and a new transcript segment
from a physician-patient encounter, return an updated SOAP note.
Rules:
- Update only — do not remove prior content unless directly contradicted.
- Return a JSON object with keys: soap (SOAPContent) and billing_codes (array of BillingCode).
- SOAPContent keys: subjective, objective, assessment, plan (all strings).
- BillingCode keys: code, description, confidence (float 0.0-1.0).
- Return only the JSON object, no prose.
"""


class SOAPUpdateResult(BaseModel):
    soap: SOAPContent
    billing_codes: list[BillingCode]


async def update_soap(
    current_soap: SOAPContent,
    new_segment: str,
    full_transcript: str,
) -> tuple[SOAPContent, list[BillingCode]]:
    prompt = f"Current SOAP:\n{current_soap.model_dump_json()}\n\n"
    if full_transcript:
        prompt += f"Full transcript so far:\n{full_transcript}\n\n"
    prompt += f"New transcript segment:\n{new_segment}"

    result = await llm.generate(
        prompt=prompt,
        system=SOAP_SYSTEM_PROMPT,
        response_model=SOAPUpdateResult,
    )
    return result.soap, result.billing_codes
