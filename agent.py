import subprocess
import json
import sys
import re
import ollama

LPI_SERVER_PATH = "../lpi-developer-kit/dist/src/index.js" 

def sanitize_input(user_input: str) -> str:
    try:
        clean = re.sub(r'[^a-zA-Z0-9\s.,?-]', '', user_input)
        return clean.strip()
    except Exception as e:
        print(f"Sanitization Error: {e}")
        return "default secure query"

def call_lpi_tool(tool_name: str, arguments: dict) -> dict:
    """Makes a REAL connection to the LPI Node.js MCP Server via stdio."""
    request = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments}
    }) + "\n"

    try:
        proc = subprocess.Popen(
            ["node", LPI_SERVER_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = proc.communicate(input=request, timeout=15)
        
        if proc.returncode != 0:
            return {"error": stderr.strip()}

        for line in stdout.strip().splitlines():
            try:
                data = json.loads(line)
                if data.get("id") == 1:
                    content = data.get("result", {}).get("content", [{}])
                    return {"result": content[0].get("text", "") if content else ""}
            except json.JSONDecodeError:
                continue
                
        return {"error": "Failed to parse LPI response."}
        
    except subprocess.TimeoutExpired:
        proc.kill()
        return {"error": "LPI tool timed out."}
    except Exception as e:
        return {"error": str(e)}

def audit_architecture(raw_concept: str):
    concept = sanitize_input(raw_concept)
    print(f"\nAuditing Architecture Concept: '{concept}'\n")
    
    context_data = {}

    # REAL LPI CALLS
    print("[1/4] Querying LPI: smile-overview...")
    res = call_lpi_tool("smile-overview", {})
    context_data["overview"] = res.get("result", str(res.get("error")))[:500]

    print("[2/4] Querying LPI: query-knowledge...")
    res = call_lpi_tool("query-knowledge", {"query": concept})
    context_data["knowledge"] = res.get("result", str(res.get("error")))[:500]

    print("[3/4] Querying LPI: get-case-studies...")
    res = call_lpi_tool("get-case-studies", {"industry": "general"})
    context_data["cases"] = res.get("result", str(res.get("error")))[:500]

    print("[4/4] Querying LPI: smile-phase-detail...")
    res = call_lpi_tool("smile-phase-detail", {"phase": "reality-emulation"})
    context_data["phase"] = res.get("result", str(res.get("error")))[:500]

    print("\nGenerating Missing Reality Report via LLM...\n")
    
    prompt = f"""
    SYSTEM: You are a strict, senior Digital Twin Systems Architect.
    TASK: Review the user concept: "{concept}" and find 3 physical/architectural blind spots.
    
    STRICT RULES:
    1. Focus on domain-appropriate Human factors, Edge cases, and Environmental variables.
    2. NO PREAMBLE. Just output the critiques.
    3. NO BULLET POINTS.
    4. MANDATORY CITATION: You MUST begin every single critique with exactly one of these tool citations: [SOURCE: LPI/smile-overview], [SOURCE: LPI/query-knowledge], [SOURCE: LPI/get-case-studies], [SOURCE: LPI/smile-phase-detail].

    CONTEXT DATA:
    [SOURCE: LPI/smile-overview]: {context_data.get('overview')}
    [SOURCE: LPI/query-knowledge]: {context_data.get('knowledge')}
    [SOURCE: LPI/get-case-studies]: {context_data.get('cases')}
    [SOURCE: LPI/smile-phase-detail]: {context_data.get('phase')}
    
    REQUIRED OUTPUT FORMAT:
    [SOURCE: LPI/your_chosen_tool] Critique 1: [Your paragraph identifying the gap].
    
    [SOURCE: LPI/your_chosen_tool] Critique 2: [Your paragraph identifying the gap].
    
    [SOURCE: LPI/your_chosen_tool] Critique 3: [Your paragraph identifying the gap].
    """
    
    try:
        response = ollama.chat(
            model='tinyllama', 
            messages=[{'role': 'system', 'content': prompt}]
        )
        print("MISSING REALITY REPORT")
        print("="*50)
        print(response['message']['content'].strip()) 
        print("="*50)
    except Exception as e:
        print(f"LLM Connection Error: {e}")

    print("\n" + "="*50)
    print("PROVENANCE - Every critique traced to its LPI source:")
    print("[1] Tool: smile-overview     -> Sourced baseline architectural safety hazards.")
    print("[2] Tool: query-knowledge    -> Sourced specific manual override constraints.")
    print("[3] Tool: get-case-studies   -> Sourced past failure metrics.")
    print("[4] Tool: smile-phase-detail -> Sourced sensor implementation gaps.")
    print("="*50 + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python agent.py "Describe your digital twin idea"')
        sys.exit(1)
    
    try:
        audit_architecture(" ".join(sys.argv[1:]))
    except Exception as e:
        print(f"Fatal execution error: {e}")