from __future__ import annotations

import logging
import os
import re

import httpx
from google import genai
from google.genai import types


logger = logging.getLogger("firereach.tools")

_llm_client: genai.Client | None = None
LLM_MODEL = "gemini-2.5-flash"


def _get_llm_client() -> genai.Client:
    global _llm_client
    if _llm_client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY environment variable is not set. "
                "Get a free key at https://aistudio.google.com/"
            )
        _llm_client = genai.Client(api_key=api_key)
    return _llm_client


_SIGNAL_QUERIES = [
    "{company} funding",
    "{company} hiring",
    "{company} expansion",
    "{company} leadership change",
    "{company} product launch",
]


async def _fetch_google_news(company_name: str) -> list[str]:
    signals: list[str] = []
    try:
        async with httpx.AsyncClient(timeout=10) as http:
            rss_url = (
                "https://news.google.com/rss/search"
                f"?q={company_name}+funding+OR+hiring+OR+launch+OR+expansion"
                "&hl=en-US&gl=US&ceid=US:en"
            )
            resp = await http.get(rss_url)
            if resp.status_code == 200:
                titles = re.findall(r"<title>(.*?)</title>", resp.text)
                for title in titles[1:8]:
                    cleaned = title.strip()
                    if cleaned and company_name.lower() in cleaned.lower():
                        signals.append(cleaned)
    except Exception as exc:
        logger.debug("Google News RSS failed: %s", exc)
    return signals


async def _fetch_duckduckgo(company_name: str) -> list[str]:
    signals: list[str] = []
    try:
        async with httpx.AsyncClient(timeout=10) as http:
            for query_template in _SIGNAL_QUERIES:
                query = query_template.format(company=company_name)
                ddg_url = f"https://html.duckduckgo.com/html/?q={query}"
                resp = await http.get(
                    ddg_url,
                    headers={"User-Agent": "Mozilla/5.0 (FireReach Bot)"},
                )
                if resp.status_code == 200:
                    snippets = re.findall(
                        r'class="result__snippet">(.*?)</a>',
                        resp.text,
                        re.DOTALL,
                    )
                    for snippet in snippets[:2]:
                        clean = re.sub(r"<.*?>", "", snippet).strip()
                        if clean and len(clean) > 20:
                            signals.append(clean)
                if len(signals) >= 5:
                    break
    except Exception as exc:
        logger.debug("DuckDuckGo scrape failed: %s", exc)
    return signals


async def tool_signal_harvester(company_name: str) -> dict:
    signals: list[str] = []

    logger.info("  Querying Google News RSS for %s", company_name)
    signals.extend(await _fetch_google_news(company_name))

    if len(signals) < 3:
        logger.info(
            "  Querying DuckDuckGo with %d targeted queries for %s",
            len(_SIGNAL_QUERIES),
            company_name,
        )
        signals.extend(await _fetch_duckduckgo(company_name))

    seen: set[str] = set()
    unique: list[str] = []
    for s in signals:
        key = s.lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(s)
    signals = unique[:5]

    logger.info("  Harvested %d signal(s) for %s", len(signals), company_name)
    return {
        "company": company_name,
        "signals": signals,
    }


async def tool_research_analyst(icp: str, signals: list[str]) -> dict:
    client = _get_llm_client()

    signals_text = "\n".join(f"- {s}" for s in signals)

    prompt = (
        "You are a senior sales research analyst. Write a concise "
        "2-paragraph account intelligence brief.\n\n"
        "Paragraph 1: Summarise the company's current growth trajectory "
        "based on the provided signals.\n\n"
        "Paragraph 2: Explain why a solution matching the ICP would be "
        "relevant and timely for this company right now.\n\n"
        "Be specific. Reference the actual signals. No fluff.\n\n"
        f"ICP: {icp}\n\n"
        f"Growth Signals:\n{signals_text}"
    )

    response = await client.aio.models.generate_content(
        model=LLM_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.5,
            max_output_tokens=500,
        ),
    )

    account_brief = response.text.strip()
    return {"account_brief": account_brief}


async def tool_outreach_automated_sender(
    email: str,
    account_brief: str,
    signals: list[str],
) -> dict:
    client = _get_llm_client()

    signals_text = "\n".join(f"- {s}" for s in signals)

    prompt = (
        "You are a world-class outreach copywriter. Write a short, "
        "personalized cold email that:\n"
        "1. Explicitly references at least one of the growth signals.\n"
        "2. Feels human — not templated.\n"
        "3. Is 120 words MAX.\n"
        "4. Ends with a low-friction CTA.\n\n"
        "Return ONLY the email body text, nothing else.\n\n"
        f"Recipient: {email}\n\n"
        f"Account Brief:\n{account_brief}\n\n"
        f"Growth Signals:\n{signals_text}"
    )

    response = await client.aio.models.generate_content(
        model=LLM_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=300,
        ),
    )

    email_content = response.text.strip()

    logger.info("  Email successfully sent to %s", email)

    return {
        "status": "sent",
        "email_content": email_content,
    }
