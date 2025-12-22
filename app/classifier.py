from openai import OpenAI
import json
import time
from app.config import get_settings
from pydantic import BaseModel

settings = get_settings()
client = OpenAI(api_key=settings.OPENAI_API_KEY)

default_model = "gpt-5-mini"
classifier_model = "gpt-5-nano"
final_max_tokens = settings.RESPONSE_MAX_TOKENS

# Level up model in case of low confidence
confidence_threshold = 0.0

model_mapping = {
    "low": "gpt-5-nano",
    "medium": "gpt-5-mini",
    "high": "gpt-5"
}

class Classification(BaseModel):
    complexity: str
    confidence: float

CLASSIFIER_SYSTEM_PROMPT = """You are a prompt complexity classifier. Analyze the user's prompt and classify it into one of three complexity levels: low, medium, or high.

Classification criteria:
- "low": Simple queries, basic questions, casual requests with minimal stakes
- "medium": Moderate complexity tasks, general information requests, standard analysis
- "high": Complex reasoning, critical decision-making, high-stakes situations where errors are costly, creative/strategic work, code generation, medical/legal advice, financial decisions

Return ONLY valid JSON with this exact format:
{
    "complexity": "low" | "medium" | "high",
    "confidence": <float between 0.0 and 1.0>
}"""

def execute_prompt(prompt: str, model: str = default_model) -> str:
    response = client.responses.create(
        model=model,
        input=prompt
        )
    return response.output_text

def classify_prompt(prompt: str) -> dict:
    """Classify prompt using gpt-5-nano and select appropriate model."""
    
    # Start timing the classification request
    classification_start = time.time()
    
    classification_response = client.responses.parse(
        model=classifier_model,
        input=[
            {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": prompt,
            },
        ],
        text_format=Classification,
    )

    classification = classification_response.output_parsed
    
    # Calculate classification latency
    classification_latency = time.time() - classification_start
    
    # Check result
    try:
        classification = json.loads(classification_response.output_text)
        complexity = classification["complexity"]
        confidence = classification["confidence"]
    # Fallback
    except (json.JSONDecodeError, KeyError):
        print("Classification JSON structured incorrectly, using defaults.")
        complexity = "medium"
        confidence = 0.5
    
    selected_model = model_mapping.get(complexity, default_model)
    
    if confidence < confidence_threshold:
        if complexity == "low":
            selected_model = model_mapping["medium"]
        elif complexity == "medium":
            selected_model = model_mapping["high"]
    
    # Debug prints
    print(f"Complexity: {complexity}")
    print(f"Confidence: {confidence:.2f}")
    print(f"Selected model: {selected_model}")
    print(f"Extra latency: {classification_latency:.3f}s")

    output = execute_prompt(prompt, model=selected_model)
    
    print(output)

    return {
        "output": output,
        "model": selected_model,
        "complexity": complexity,
        "confidence": confidence
    }