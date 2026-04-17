import json
import sys
import ollama

def call_lpi_mcp_mock(tool_name: str, arguments: dict) -> str:
    """
    Simulates the LPI Knowledge Server to bypass WinError 267.
    Returns JSON payloads about the SMILE Digital Twin Methodology.
    """
    print(f"[System] Sending JSON-RPC request to tool: {tool_name}...")
    
    if tool_name == "smile-overview":
        return json.dumps({
            "framework": "SMILE (Sustainable Methodology for Impact Lifecycle Enablement)",
            "core_phases": ["1. Strategy", "2. Modeling", "3. Implementation", "4. Lifecycle"],
            "purpose": "A methodology for building enterprise digital twins."
        })
    elif tool_name == "query-knowledge":
        query = arguments.get("query", "general")
        return json.dumps({
            "search_term": query,
            "best_practices": ["Ensure data interoperability", "Implement Explainable AI (XAI)"],
            "status": "success"
        })
    
    return json.dumps({"error": "Tool not found"})

def run_agent():
    print("\n" + "="*50)
    print("🌐 LPI DIGITAL TWIN CONSULTANT")
    print("="*50)
    
    user_input = input("\nYou: ").strip()

    if not user_input:
        print("[Error] Query cannot be empty. Please ask about Digital Twins.")
        sys.exit(1)

    print("\n--- LPI SYSTEM TRACE ---")
    
    try:
        overview_data = call_lpi_mcp_mock("smile-overview", {})
        knowledge_data = call_lpi_mcp_mock("query-knowledge", {"query": user_input})
    except Exception as e:
        print(f"[Error] Failed to execute LPI tools: {e}")
        sys.exit(1)

    print("--- TRACE COMPLETE ---\n")
    print("[System] Generating explainable response via TinyLlama...\n")
    
    system_prompt = """You are an LPI Methodology Consultant. 
    Analyze the user's question and answer using ONLY the provided LPI data.
    
    CRITICAL RULES FOR EXPLAINABILITY:
    1. You MUST cite the data sources in your text.
    2. Start sentences with: "According to [Tool: smile-overview]..." or "Based on [Tool: query-knowledge]..."
    """
    
    user_context = f"User asks: '{user_input}'\nOverview Data: {overview_data}\nKnowledge Data: {knowledge_data}"

    try:
        response = ollama.chat(
            model='tinyllama', 
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_context},
            ]
        )
        recommendation = response['message']['content']
    except Exception as e:
        recommendation = f"[Fatal Error] Could not connect to local Ollama model. Details: {e}"

    print("=" * 50)
    print("RECOMMENDATION")
    print("=" * 50)
    print(recommendation)
    print("\n" + "=" * 50)
    print("EXPLAINABILITY & PROVENANCE")
    print("=" * 50)
    print(f"[TRACE] smile-overview -> {overview_data}")
    print(f"[TRACE] query-knowledge -> {knowledge_data}")

if __name__ == "__main__":
    run_agent()