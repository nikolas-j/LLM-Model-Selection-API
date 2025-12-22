from pydantic import BaseModel

class PromptRequest(BaseModel):
    prompt: str

class PromptResponse(BaseModel):
    output: str
    model: str
    complexity: str
    confidence: float
    classification_latency: float