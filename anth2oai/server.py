from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import StreamingResponse
from traceback import format_exc
import uuid
from copy import deepcopy
from loguru import logger
from anth2oai.client import AsyncAnth2OAI
from anth2oai.authen import validate_api_key
import json
from dotenv import load_dotenv

load_dotenv()
import os

app = FastAPI(docs_url=None, redoc_url=None)

DEFAULT_MAX_TOKENS = 40 * 1024


def process_payload(payload: dict) -> dict:
    if "max_tokens" not in payload:
        payload["max_tokens"] = DEFAULT_MAX_TOKENS
    return payload


@app.post("/v1/chat/completions")
async def chat_completions(request: Request, api_key: str = Depends(validate_api_key)):
    body = await request.json()
    body = process_payload(body)
    is_stream = body.get("stream", False)

    try:
        openai_client: AsyncAnth2OAI = AsyncAnth2OAI(
            api_key=os.environ["ANTHROPIC_API_KEY"],
            base_url=os.environ["ANTHROPIC_BASE_URL"],
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


def init_app() -> FastAPI:
    return app
