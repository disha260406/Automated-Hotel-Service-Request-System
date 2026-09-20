"""
Hotel service systemHotel - Web Server
Combines FastAPI REST endpoints, Stitch UI Orchestrator, and Gradio AI Studio.
"""

import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import gradio as gr
import uvicorn
import database
import agent_graph
import app as gradio_app_module

fastapi_app = FastAPI(title="The Grand Azure - Hotel AI Orchestrator")

# Enable CORS
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@fastapi_app.get("/", response_class=HTMLResponse)
async def serve_stitch_ui():
    """Serves the pixel-perfect Google Stitch Orchestrator UI."""
    html_path = os.path.join(os.path.dirname(__file__), "stitch_ui.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Stitch UI file not found</h1>", status_code=404)


@fastapi_app.post("/api/chat")
async def api_chat(request: Request):
    """Processes guest input via LangGraph Agentic AI."""
    data = await request.json()
    user_msg = data.get("message", "")
    room = data.get("room", "412")
    
    agent_output = agent_graph.process_guest_message(
        user_message=user_msg,
        active_room=room
    )
    return JSONResponse(agent_output)


@fastapi_app.get("/api/requests")
async def api_get_requests(dept: str = "All", status: str = "All", priority: str = "All", search: str = ""):
    """Fetches all service requests from SQLite."""
    reqs = database.get_all_requests(dept, status, priority, search)
    return JSONResponse({"requests": reqs, "total": len(reqs)})


@fastapi_app.get("/api/stats")
async def api_get_stats():
    """Returns real-time KPI metrics."""
    stats = database.get_kpi_stats()
    return JSONResponse(stats)


@fastapi_app.post("/api/update_status")
async def api_update_status(request: Request):
    """Updates ticket status in SQLite."""
    data = await request.json()
    tid = data.get("ticket_id", "")
    status = data.get("status", "In Progress")
    staff = data.get("assigned_staff")
    notes = data.get("notes")

    success = database.update_request_status(
        ticket_id=tid,
        new_status=status,
        assigned_staff=staff,
        notes=notes,
        actor="Orchestrator UI"
    )
    return JSONResponse({"success": success, "ticket_id": tid, "status": status})


@fastapi_app.post("/api/cancel")
async def api_cancel(request: Request):
    """Cancels a request in SQLite."""
    data = await request.json()
    tid = data.get("ticket_id", "")
    reason = data.get("reason", "Cancelled by guest")
    success, msg = database.cancel_service_request(tid, reason)
    return JSONResponse({"success": success, "message": msg})


@fastapi_app.post("/api/reset_db")
async def api_reset_db():
    """Resets the SQLite database to fresh seed state."""
    database.reset_database()
    return JSONResponse({"success": True, "message": "Database reset to initial seed state."})


@fastapi_app.get("/api/rooms")
async def api_get_rooms():
    """Returns list of all rooms."""
    rooms = database.get_all_rooms()
    return JSONResponse({"rooms": rooms})


# Mount Gradio sub-application at /gradio
gradio_blocks = gradio_app_module.create_app()
app = gr.mount_gradio_app(fastapi_app, gradio_blocks, path="/gradio")


if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=7860, reload=False)
