import os
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent import create_swf_agent

# Lazy-init agent at startup
_runner: Runner | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _runner
    agent = create_swf_agent()
    session_service = InMemorySessionService()
    _runner = Runner(
        agent=agent,
        app_name="gulf_swf_agent",
        session_service=session_service,
    )
    yield


app = FastAPI(title="Gulf SWF Intelligence Agent API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AgentRequest(BaseModel):
    message: str
    session_id: str = "default"


class AgentResponse(BaseModel):
    response: str
    session_id: str


@app.post("/agent/run", response_model=AgentResponse)
async def run_agent(request: AgentRequest):
    """Send a natural-language message to the agent and get a response."""
    if _runner is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    try:
        content = types.Content(
            role="user",
            parts=[types.Part(text=request.message)],
        )
        response_text = ""
        async for event in _runner.run_async(
            user_id="user",
            session_id=request.session_id,
            new_message=content,
        ):
            if event.is_final_response():
                response_text = event.content.parts[0].text
        return AgentResponse(response=response_text, session_id=request.session_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/filings")
async def get_filings(fund: str | None = None, limit: int = 20):
    """Return stored filings from MongoDB, optionally filtered by fund."""
    from tools.mongodb_tools import get_recent_filings
    return get_recent_filings(limit=limit, fund=fund)


@app.get("/api/intelligence")
async def get_intelligence(limit: int = 5):
    """Return the latest Gemini-generated intelligence briefs."""
    from tools.mongodb_tools import get_recent_briefs
    return get_recent_briefs(limit=limit)


@app.get("/api/funds")
async def get_funds():
    """Return SWF metadata from MongoDB."""
    from tools.mongodb_tools import get_all_funds
    return get_all_funds()


@app.get("/health")
async def health():
    return {"status": "ok", "agent": "gulf_swf_intelligence_agent"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
