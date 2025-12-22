from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.schemas import PromptRequest, PromptResponse
from app.classifier import classify_prompt
from app.config import get_settings

settings = get_settings()
limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.post("/select-model")
@limiter.limit(settings.RATE_LIMIT)
async def select_model(request: Request, data: PromptRequest) -> PromptResponse:
    prompt = data.prompt
    if not prompt.strip():
        raise HTTPException(status_code=400, detail="Empty prompt.")
    if len(prompt) > settings.MAX_PROMPT_LENGTH:
        raise HTTPException(status_code=400, detail="Prompt too long.")
    
    classification = classify_prompt(prompt)
    response = PromptResponse(
        output = classification["output"],
        model=classification["model"],
        complexity=classification["complexity"],
        confidence=classification["confidence"],
        classification_latency=classification["classification_latency"]
    )
    return response