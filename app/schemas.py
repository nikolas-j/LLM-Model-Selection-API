from pydantic import BaseModel

class PromptResponse(BaseModel):
    model: str
    complexity: str
    confidence: float