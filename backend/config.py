# Spec: CONTRACTS.md §6 config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # IBM Granite / watsonx
    watsonx_api_key: str = ""
    watsonx_project_id: str = ""
    watsonx_url: str = ""
    granite_model_id: str = "ibm/granite-3-8b-instruct"

    # FHIR
    fhir_base_url: str = "https://hapi.fhir.org/baseR4"
    use_fhir_fallback: bool = False

    # Whisper
    whisper_model_size: str = "base.en"

    # Orchestrate
    orchestrate_shared_secret: str = ""

    # Feature flags
    auth_enabled: bool = True
    confidence_threshold: float = 0.75

    # Deployment
    backend_url: str = ""
    frontend_url: str = ""

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

settings = Settings()
