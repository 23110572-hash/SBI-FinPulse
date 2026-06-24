"""Analysis routes — trigger the agent crew with live SSE streaming."""
from __future__ import annotations

import asyncio
import json
import threading

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from agents import PIPELINE_STEPS, run_crew
from api.store import latest_analysis, save_analysis

router = APIRouter(prefix="/api", tags=["analysis"])


@router.get("/analysis/steps")
def get_steps():
    return {"steps": PIPELINE_STEPS}


@router.get("/analysis/{customer_id}")
def get_analysis(customer_id: str):
    result = latest_analysis(customer_id)
    if not result:
        raise HTTPException(404, "No analysis found. Run POST /api/analyze/{id} first.")
    return result


@router.post("/analyze/{customer_id}")
def analyze(customer_id: str):
    """Run the full crew synchronously and return the result."""
    try:
        result = run_crew(customer_id)
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {e}")
    save_analysis(result)
    return result


@router.get("/analyze/{customer_id}/stream")
async def analyze_stream(customer_id: str):
    """Run the crew in a worker thread, streaming each agent step via SSE.

    Uses ``asyncio.Queue`` driven by ``loop.call_soon_threadsafe`` so the
    generator wakes the instant a step finishes (no 200 ms polling lag).
    """
    loop = asyncio.get_running_loop()
    events: asyncio.Queue = asyncio.Queue()

    def push(item):
        # called from the worker thread — schedule onto the event loop safely
        loop.call_soon_threadsafe(events.put_nowait, item)

    def on_step(step: str, status: str, log=None):
        push({"type": "step", "step": step, "status": status, "log": log})

    def worker():
        try:
            result = run_crew(customer_id, on_step=on_step)
            save_analysis(result)
            push({"type": "done", "result": result})
        except Exception as e:  # surface errors to the client
            push({"type": "error", "message": str(e)})
        finally:
            push(None)  # sentinel

    threading.Thread(target=worker, daemon=True).start()

    async def event_gen():
        # announce the static step plan first
        yield f"event: steps\ndata: {json.dumps(PIPELINE_STEPS)}\n\n"
        while True:
            item = await events.get()
            if item is None:
                break
            yield f"data: {json.dumps(item)}\n\n"
        yield "event: end\ndata: {}\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
