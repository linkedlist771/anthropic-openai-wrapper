import os
from contextlib import asynccontextmanager
from pathlib import Path
from traceback import format_exc
# from typing import AwaitableGenerator

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger

from anth2oai.admin_routes import router as admin_router
from anth2oai.authen import validate_api_key
from anth2oai.configs import ConfigManager
from anth2oai.database import close_db, init_db
from anth2oai.server.claude import claude_streaming
from anth2oai.server.codex import codex_streaming

# Load .env file for initial values (before DB initialization)
load_dotenv()

# Get the directory where this module is located
MODULE_DIR = Path(__file__).parent.parent
STATIC_DIR = MODULE_DIR / "front" / "dist"
if not STATIC_DIR.exists():
    # not in dev model
    STATIC_DIR = os.environ.get("STATIC_DIR", "")
    assert STATIC_DIR, "STATIC_DIR is not set in env"
    STATIC_DIR = Path(STATIC_DIR)
    STATIC_DIR.mkdir(exist_ok=True, parents=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await init_db()
    await ConfigManager.initialize()
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


async def process_payload(payload: dict) -> dict:
    """Process request payload, setting defaults from database config."""
    if "max_tokens" not in payload:
        default_max_tokens = await ConfigManager.get_int("DEFAULT_MAX_TOKENS", 40960)
        payload["max_tokens"] = default_max_tokens
    return payload


async def dispatch_request(api_key: str, body: dict):
    model = body.get("model", "").lower()
    request_cls = None
    if "claude" in model:
        request_cls = claude_streaming
    elif "codex" in model or "gpt" in model:
        request_cls = codex_streaming
    else:
        raise HTTPException(f"Model {model} is not supported!")
    response = await request_cls(api_key, body)
    return response


@app.get("/")
async def _():
    # redirect to login
    return RedirectResponse(url="/admin")


@app.post("/v1/chat/completions")
async def chat_completions(request: Request, api_key: str = Depends(validate_api_key)):
    body = await request.json()
    body = await process_payload(body)
    is_stream = body.get("stream", False)
    try:
        if is_stream:
            return await dispatch_request(api_key, body)

        else:
            raise HTTPException(f"No streaming is unsupported!")

            # response = await openai_client.chat.completions.create(**body)

            # if hasattr(response, "model_dump"):
            #     response_dict = response.model_dump()
            # else:
            #     response_dict = response

            # return response_dict

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
