from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import AgentRequest, AgentResponse
from agent import run_agent

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("firereach")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🔥 FireReach agent is online")
    yield
    logger.info("🔥 FireReach shutting down")


app = FastAPI(
    title="FireReach",
    description="Autonomous outreach engine – research a company, generate a personalised cold email.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "FireReach"}


@app.post("/run-agent", response_model=AgentResponse)
async def run_agent_endpoint(req: AgentRequest):
    logger.info(
        "▶ /run-agent called  |  company=%s  email=%s",
        req.company,
        req.email,
    )
    start = time.perf_counter()

    try:
        result = await run_agent(
            icp=req.icp,
            company=req.company,
            email=req.email,
        )

        elapsed = time.perf_counter() - start
        logger.info(
            "✅ Agent finished in %.1fs  |  signals=%d  brief_len=%d  email_len=%d",
            elapsed,
            len(result.signals),
            len(result.account_brief),
            len(result.email_content),
        )
        return result

    except RuntimeError as exc:
        logger.error("Runtime error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        logger.exception("Unhandled agent error")
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {exc}",
        )
