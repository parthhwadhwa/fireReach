"""
FireReach – Pydantic schemas for request/response validation.
"""

from typing import List

from pydantic import BaseModel, Field


# ── Request ──────────────────────────────────────────────────────────────────

class AgentRequest(BaseModel):
    """Payload accepted by the /run-agent endpoint."""

    icp: str = Field(
        ...,
        description="Ideal Customer Profile – describes the target persona",
        examples=["Series-A B2B SaaS founders scaling from 1M to 5M ARR"],
    )
    company: str = Field(
        ...,
        description="Target company name to research",
        examples=["Acme Corp"],
    )
    email: str = Field(
        ...,
        description="Recipient email address for the outreach",
        examples=["founder@acme.com"],
    )


# ── Response ─────────────────────────────────────────────────────────────────

class AgentResponse(BaseModel):
    """Final response returned to the caller matching exactly what the instructions ask for."""

    signals: List[str] = Field(default_factory=list)
    account_brief: str = ""
    email_content: str = ""
