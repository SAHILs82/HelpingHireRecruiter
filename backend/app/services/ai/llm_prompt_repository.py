from sqlalchemy.orm import Session
from app.db.models.dynamic_llm_prompts import DynamicLLMPrompt

def load_active_prompt_map(db_session: Session, use_case: str) -> dict:
    """
    Loads active prompt variants for a specific use case from the database.
    """
    records = db_session.query(DynamicLLMPrompt).filter(
        DynamicLLMPrompt.use_case == use_case,
        DynamicLLMPrompt.is_active == True
    ).all()
    
    return {record.variant_key: record.prompt_body for record in records}

def resolve_full_prompt(prompt_map: dict, variant_key: str, default_text: str) -> str:
    """
    Attempts to find the prompt for the given variant key in the database overrides,
    and falls back to default_text if not found.
    """
    return prompt_map.get(variant_key, default_text)
