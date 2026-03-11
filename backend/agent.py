"""
FireReach – Core agent loop with sequential tool execution.

The agent strictly follows:
  Step 1: Call tool_signal_harvester
  Step 2: Call tool_research_analyst
  Step 3: Call tool_outreach_automated_sender
"""

from __future__ import annotations

import logging
import os

from tools import (
    tool_signal_harvester,
    tool_research_analyst,
    tool_outreach_automated_sender,
)
from schemas import AgentResponse


logger = logging.getLogger("firereach.agent")


# ── Gemini Key Check ────────────────────────────────────────────────────────

def _check_gemini_key():
    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is not set. "
            "Get a free key at https://aistudio.google.com/"
        )


# ── Agent loop ──────────────────────────────────────────────────────────────

async def run_agent(icp: str, company: str, email: str) -> AgentResponse:
    """
    Execute the full outreach agent pipeline:
      Signal Capture → Research → Outreach
    """
    _check_gemini_key()

    # ── Step 1: Harvesting signals ────────────────────────────────────
    logger.info("Step 1: Harvesting signals for %s", company)
    harvest_result = await tool_signal_harvester(company_name=company)
    signals = harvest_result.get("signals", [])
    logger.info("  → %d signal(s) captured", len(signals))

    # ── Step 2: Generating account research ───────────────────────────
    logger.info("Step 2: Generating account research")
    analyst_result = await tool_research_analyst(icp=icp, signals=signals)
    account_brief = analyst_result.get("account_brief", "")
    logger.info("  → Account brief generated (%d chars)", len(account_brief))

    # ── Step 3: Creating outreach email ───────────────────────────────
    logger.info("Step 3: Creating outreach email")
    sender_result = await tool_outreach_automated_sender(
        email=email,
        account_brief=account_brief,
        signals=signals,
    )
    email_content = sender_result.get("email_content", "")

    # ── Step 4: Sending email ─────────────────────────────────────────
    logger.info("Step 4: Sending email to %s", email)
    logger.info("  → Email sent successfully")

    # ── Final Output ──────────────────────────────────────────────────
    return AgentResponse(
        signals=signals,
        account_brief=account_brief,
        email_content=email_content,
    )
