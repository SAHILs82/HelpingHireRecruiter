import uuid
from sqlalchemy import Column, String, Text, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class DynamicLLMPrompt(Base):
    __tablename__ = "dynamic_llm_prompts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    use_case = Column(String(50), nullable=False, index=True)
    variant_key = Column(String(50), nullable=False)
    prompt_body = Column(Text, nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)

    __table_args__ = (
        UniqueConstraint("use_case", "variant_key", name="uq_dynamic_prompts_usecase_variant"),
    )
