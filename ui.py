import streamlit as st
import requests

st.set_page_config(page_title="Smart Model Selection API", page_icon="🤖", layout="wide")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "model_counts" not in st.session_state:
    st.session_state.model_counts = {"gpt-5-nano": 0, "gpt-5-mini": 0, "gpt-5": 0}
if "token_counts" not in st.session_state:
    st.session_state.token_counts = {
        "gpt-5-nano": {"input": 0, "output": 0},
        "gpt-5-mini": {"input": 0, "output": 0},
        "gpt-5": {"input": 0, "output": 0},
        "classifier": {"input": 0}  # Only track input for classifier (gpt-5-nano)
    }

# Model pricing (per 1M tokens)
model_pricing = {
    "gpt-5-nano": {"input": 0.05, "output": 0.40},
    "gpt-5-mini": {"input": 0.25, "output": 0.60},
    "gpt-5": {"input": 1.25, "output": 10.00}
}

# Sidebar with model statistics (left side)
with st.sidebar:
    st.header("📊 Current Models")
    for model, count in st.session_state.model_counts.items():
        pricing = model_pricing[model]
        tokens = st.session_state.token_counts[model]
        st.metric(
            model,
            count,
            f"${pricing['input']:.2f} / ${pricing['output']:.2f}"
        )
        st.markdown(f"<p style='font-size: 15px; color: #888;'>In: {tokens['input']:,} | Out: {tokens['output']:,} tokens</p>", unsafe_allow_html=True)
    
    st.markdown("<p style='font-size: 14px; color: #888;'>Count | Input/Output cost per 1M tokens</p>", unsafe_allow_html=True)
    
    if st.button("Clear History"):
        st.session_state.messages = []
        st.session_state.model_counts = {"gpt-5-nano": 0, "gpt-5-mini": 0, "gpt-5": 0}
        st.session_state.token_counts = {
            "gpt-5-nano": {"input": 0, "output": 0},
            "gpt-5-mini": {"input": 0, "output": 0},
            "gpt-5": {"input": 0, "output": 0},
            "classifier": {"input": 0}
        }
        st.rerun()

# Main content area with chat and savings sidebar
main_col, savings_col = st.columns([3, 1])

with main_col:
    # Main chat interface
    st.title("🤖 Smart Model Selection API")
    st.caption("Classifies prompts based on complexity and selects cheapest adequate model to save on API costs")

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message("user"):
            st.write(msg["prompt"])
        with st.chat_message("assistant"):
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            col1.markdown(f"<p style='font-size: 14px; color: #888;'>🔹 {msg['model']}</p>", unsafe_allow_html=True)
            col2.markdown(f"<p style='font-size: 14px; color: #888;'>Complexity: {msg['complexity']}</p>", unsafe_allow_html=True)
            col3.markdown(f"<p style='font-size: 14px; color: #888;'>Confidence ✓ {msg['confidence']:.0%}</p>", unsafe_allow_html=True)
            col4.markdown(f"<p style='font-size: 14px; color: #888;'>⏱️ Extra latency {msg['classification_latency']:.3f}s</p>", unsafe_allow_html=True)
            st.write(msg["output"])

    # Chat input
    if prompt := st.chat_input("What would you like to ask?"):
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(
                        "http://localhost:8000/api/select-model",
                        json={"prompt": prompt}
                    )
                    result = response.json()
                    
                    # Display model info
                    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
                    col1.markdown(f"<p style='font-size: 14px; color: #888;'>🔹 {result['model']}</p>", unsafe_allow_html=True)
                    col2.markdown(f"<p style='font-size: 14px; color: #888;'>📊 {result['complexity']}</p>", unsafe_allow_html=True)
                    col3.markdown(f"<p style='font-size: 14px; color: #888;'>✓ {result['confidence']:.0%}</p>", unsafe_allow_html=True)
                    col4.markdown(f"<p style='font-size: 14px; color: #888;'>⏱️ {result['classification_latency']:.3f}s</p>", unsafe_allow_html=True)
                    
                    # Display response
                    st.write(result["output"])
                    
                    # Estimate token counts (characters / 4)
                    input_tokens = len(prompt) // 4
                    output_tokens = len(result["output"]) // 4
                    
                    # Update history and counts
                    st.session_state.messages.append({
                        "prompt": prompt,
                        "output": result["output"],
                        "model": result["model"],
                        "complexity": result["complexity"],
                        "confidence": result["confidence"],
                        "classification_latency": result["classification_latency"]
                    })
                    st.session_state.model_counts[result["model"]] += 1
                    
                    # Update token counts
                    st.session_state.token_counts[result["model"]]["input"] += input_tokens
                    st.session_state.token_counts[result["model"]]["output"] += output_tokens
                    st.session_state.token_counts["classifier"]["input"] += input_tokens  # Classifier also processes the prompt
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")

with savings_col:
    # Calculate total savings
    total_input_tokens = sum(st.session_state.token_counts[m]["input"] for m in ["gpt-5-nano", "gpt-5-mini", "gpt-5"])
    total_output_tokens = sum(st.session_state.token_counts[m]["output"] for m in ["gpt-5-nano", "gpt-5-mini", "gpt-5"])
    classifier_input_tokens = st.session_state.token_counts["classifier"]["input"]
    
    # Add classifier overhead (using gpt-5-nano pricing for input)
    total_input_tokens += classifier_input_tokens
    
    if total_input_tokens + total_output_tokens > 0:
        # Calculate actual cost with smart selection
        actual_cost = 0
        for model in ["gpt-5-nano", "gpt-5-mini", "gpt-5"]:
            tokens = st.session_state.token_counts[model]
            pricing = model_pricing[model]
            actual_cost += (tokens["input"] / 1_000_000) * pricing["input"]
            actual_cost += (tokens["output"] / 1_000_000) * pricing["output"]
        
        # Add classifier cost (gpt-5-nano input only)
        actual_cost += (classifier_input_tokens / 1_000_000) * model_pricing["gpt-5-nano"]["input"]
        
        # Calculate cost if we used only gpt-5
        gpt5_cost = (total_input_tokens / 1_000_000) * model_pricing["gpt-5"]["input"]
        gpt5_cost += (total_output_tokens / 1_000_000) * model_pricing["gpt-5"]["output"]
        
        # Scale to per 1M tokens
        total_tokens = total_input_tokens + total_output_tokens
        actual_cost_per_1m = (actual_cost / total_tokens) * 1_000_000
        gpt5_cost_per_1m = (gpt5_cost / total_tokens) * 1_000_000
        
        savings_per_1m = gpt5_cost_per_1m - actual_cost_per_1m
        savings_percent = (savings_per_1m / gpt5_cost_per_1m) * 100 if gpt5_cost_per_1m > 0 else 0
        
        # Use container with fixed position styling
        st.markdown(f"""
        <div style='position: sticky; top: 20px;'>
            <h3 style='margin-bottom: 20px;'>💰 Cost Savings</h3>
            <div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;'>
                <p style='font-size: 60px; font-weight: bold; color: #00C851; margin: 0;'>{savings_percent:.1f}%</p>
                <p style='font-size: 16px; color: #888; margin: 0;'>vs GPT-5</p>
            </div>
            <p style='font-size: 18px; text-align: center; margin-top: 20px; font-weight: bold;'>Save ${savings_per_1m:.2f}</p>
            <p style='font-size: 14px; text-align: center; color: #888; margin-top: -10px;'>per 1M tokens</p>
            <hr style='margin: 20px 0;'>
            <p style='font-size: 16px; text-align: center;'><b>Smart Total</b><br/><span style='font-size: 20px; color: #00C851;'>${actual_cost_per_1m:.2f}</span></p>
            <p style='font-size: 16px; text-align: center;'><b>GPT-5 Only</b><br/><span style='font-size: 20px; color: #888;'>${gpt5_cost_per_1m:.2f}</span></p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='position: sticky; top: 20px;'>
            <h3>💰 Cost Savings</h3>
            <div style='padding: 20px; background-color: #e8f4f8; border-radius: 10px; text-align: center;'>
                <p style='color: #888;'>Start chatting to see savings!</p>
            </div>
        </div>
        """, unsafe_allow_html=True)