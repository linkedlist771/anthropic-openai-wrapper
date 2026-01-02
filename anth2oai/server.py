from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import StreamingResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from traceback import format_exc
import uuid
from copy import deepcopy
from loguru import logger
from anth2oai.client import AsyncAnth2OAI
from anth2oai.authen import validate_api_key
from anth2oai.database import init_db, close_db, sync_configs_to_env
from anth2oai.admin_routes import router as admin_router
import json
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

# Get the directory where this module is located
MODULE_DIR = Path(__file__).parent.parent
STATIC_DIR = MODULE_DIR / "front" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await init_db()
    await sync_configs_to_env()
    logger.info("Application started")
    yield
    # Shutdown
    await close_db()
    logger.info("Application shutdown")


app = FastAPI(docs_url=None, redoc_url=None, lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include admin routes
app.include_router(admin_router)

DEFAULT_MAX_TOKENS = 40 * 1024


def process_payload(payload: dict) -> dict:
    if "max_tokens" not in payload:
        payload["max_tokens"] = DEFAULT_MAX_TOKENS
    return payload


@app.get("/")
async def _():
    # redirect to login
    return RedirectResponse(url="/admin")


@app.post("/v1/chat/completions")
async def chat_completions(request: Request, api_key: str = Depends(validate_api_key)):
    body = await request.json()
    body = process_payload(body)
    is_stream = body.get("stream", False)

    try:
        openai_client: AsyncAnth2OAI = AsyncAnth2OAI(
            api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
            base_url=os.environ.get(
                "ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1"
            ),
        )

        if is_stream:
            streaming = await openai_client.chat.completions.create(**body)

            async def stream_response():
                try:
                    async for chunk in streaming:
                        if hasattr(chunk, "model_dump"):
                            chunk_dict = chunk.model_dump()
                        else:
                            chunk_dict = chunk
                        yield f"data: {json.dumps(chunk_dict)}\n\n"

                    yield "data: [DONE]\n\n"

                except HTTPException as e:
                    error_chunk = {
                        "error": {
                            "type": e.detail.get("type", "error")
                            if isinstance(e.detail, dict)
                            else "error",
                            "message": e.detail.get("message", str(e.detail))
                            if isinstance(e.detail, dict)
                            else str(e.detail),
                        }
                    }
                    yield f"data: {json.dumps(error_chunk)}\n\n"
                    yield "data: [DONE]\n\n"
                except Exception as e:
                    logger.error(f"Error in stream_response: {e}")
                    logger.error(format_exc())
                    error_chunk = {"error": {"type": "stream_error", "message": str(e)}}
                    yield f"data: {json.dumps(error_chunk)}\n\n"
                    yield "data: [DONE]\n\n"

            return StreamingResponse(
                stream_response(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                },
            )
        else:
            response = await openai_client.chat.completions.create(**body)

            if hasattr(response, "model_dump"):
                response_dict = response.model_dump()
            else:
                response_dict = response

            return response_dict

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        logger.error(format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# Serve static files from Vue dist if it exists
if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/favicon.ico")
    async def favicon():
        favicon_path = STATIC_DIR / "favicon.ico"
        if favicon_path.exists():
            return FileResponse(favicon_path)
        raise HTTPException(status_code=404)

    @app.get("/admin")
    @app.get("/admin/{full_path:path}")
    async def serve_admin(full_path: str = ""):
        """Serve the Vue admin SPA for all admin routes."""
        return FileResponse(STATIC_DIR / "index.html")


def init_app() -> FastAPI:
    return app
