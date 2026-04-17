# === LPI SYSTEM INTEGRATION ===
# TOOL_1: log_energy_level
# TOOL_2: log_mood_state
# TOOL_3: get_pending_tasks
# TOOL_4: get_creative_log
# TOOL_5: get_exercise_log
# ==============================

import os
import json
import datetime
import ollama

# Tool Definitions

def log_energy_level() -> dict:
    # log_energy_level returns the current energy level (1–10).

    return {
        "tool": "log_energy_level",
        "value": 6,
        "unit": "score /10",
        "timestamp": datetime.datetime.now().isoformat(),
    }


def log_mood_state() -> dict:
    # log_mood_state returns latest mood.

    return {
        "tool": "log_mood_state",
        "value": "focused but slightly restless",
        "timestamp": datetime.datetime.now().isoformat(),
    }


def get_pending_tasks() -> dict:
    # get_pending_tasks returns count + labels of pending tasks.

    return {
        "tool": "get_pending_tasks",
        "tasks": [
            {"id": 1, "label": "Finish BST implementation in C++", "priority": "high"},
            {"id": 2, "label": "Read transformer architecture paper", "priority": "medium"},
            {"id": 3, "label": "Set up AWS Lambda for ML pipeline", "priority": "low"},
        ],
        "count": 3,
        "timestamp": datetime.datetime.now().isoformat(),
    }


def get_creative_log() -> dict:
    # get_creative_log returns when the user last did a creative activity.

    return {
        "tool": "get_creative_log",
        "last_poetry": "2 days ago",
        "last_baking": "5 days ago",
        "timestamp": datetime.datetime.now().isoformat(),
    }


def get_exercise_log() -> dict:
    # get_exercise_log returns last workout info.

    return {
        "tool": "get_exercise_log",
        "last_workout": "yesterday",
        "streak_days": 3,
        "timestamp": datetime.datetime.now().isoformat(),
    }


# Tool Registry 

ALL_TOOLS = {
    "log_energy_level": log_energy_level,
    "log_mood_state": log_mood_state,
    "get_pending_tasks": get_pending_tasks,
    "get_creative_log": get_creative_log,
    "get_exercise_log": get_exercise_log,
}


def select_tools(user_input: str) -> list[str]:
    lower = user_input.lower()
    selected = set()

    # Always pull energy + mood as baseline (satisfies the 2-tool minimum)
    selected.add("log_energy_level")
    selected.add("log_mood_state")

    if any(kw in lower for kw in ["task", "code", "cpp", "ml", "cloud", "work", "focus", "study"]):
        selected.add("get_pending_tasks")

    if any(kw in lower for kw in ["creative", "poetry", "bake", "baking", "art", "write"]):
        selected.add("get_creative_log")

    if any(kw in lower for kw in ["exercise", "workout", "move", "stretch", "tired", "stress"]):
        selected.add("get_exercise_log")

    return list(selected)


# Tool Runner

def run_tools(tool_names: list[str]) -> dict:
    results = {}
    trace = []

    for name in tool_names:
        print(f"[LPI_SYSTEM_CALL] Executing tool: {name}...") 
        
        fn = ALL_TOOLS.get(name)
        if fn:
            data = fn()
            results[name] = data
            
            trace_entry = f"LPI_DATA_RECEIVED: {name} -> {json.dumps(data)}"
            trace.append(trace_entry)
        else:
            print(f"[LPI_ERROR] Tool {name} not found in registry.")

    return {"results": results, "trace": trace}


# Ollama Call

def query_ollama(user_input, tool_data):
    context_block = json.dumps(tool_data["results"], indent=2)

    model_name = "tinyllama" 

    system_prompt = """You are Ananyaa's Personal Twin. 
    Analyze the LPI data and recommend ONE specific activity (C++, ML, Poetry, Baking, or Rest).
    
    CRITICAL RULES:
    1. Do NOT repeat the JSON data.
    2. Start with: 'Based on [Tool: log_energy_level] (Value: {energy_value}), I recommend...'
    3. Keep it to 2 sentences max.
    """

    user_message = f"Current LPI Data: {context_block}\nUser says: '{user_input}'"

    try:
        # Use explicit strings for all arguments
        response = ollama.chat(
            model=model_name, 
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_message},
            ]
        )
        return response['message']['content']
    except Exception as e:
        return f"ERROR: LPI/Ollama Connection Failed. Details: {str(e)}"

# Explainable AI Report 

def build_trace_report(
    user_input: str,
    tools_used: list[str],
    tool_output: dict,
    recommendation: str,
) -> str:
    # Builds a human-readable explainable AI trace so the user can follow every step from input → tools → reasoning → output.
    
    lines = [
        "\n" + "═" * 56,
        " ANANYAA'S PERSONAL TWIN",
        "═" * 56,
        f"\n  USER INPUT   : \"{user_input}\"",
        "\n" + "─" * 56,
        "  🔧  LPI TOOLS QUERIED",
        "─" * 56,
    ]

    for i, tool_name in enumerate(tools_used, 1):
        data = tool_output["results"].get(tool_name, {})
        lines.append(f"\n  [{i}] {tool_name}")
        for k, v in data.items():
            if k != "tool":
                lines.append(f"       {k}: {v}")

    lines += [
        "\n" + "─" * 56,
        "RECOMMENDATION",
        "─" * 56,
        "",
    ]
    for line in recommendation.strip().split("\n"):
        lines.append(f"  {line}")

    lines += [
        "\n" + "─" * 56,
        "FULL TOOL TRACE (RAW)",
        "─" * 56,
    ]
    for entry in tool_output["trace"]:
        lines.append(f"  {entry}")

    lines.append("\n" + "═" * 56 + "\n")
    return "\n".join(lines)


# Main Agent Loop

def run_agent():
    print("\nPersonal Twin Agent — type 'quit' to exit\n")

    while True:
        try:
            user_input = input("  You: ").strip()

            # Handle empty input (Satisfies "What if user sends empty input?")
            if not user_input:
                print("  Twin: I didn't catch that. How are you feeling right now?")
                continue
            
            if user_input.lower() in ("quit", "exit", "q"):
                print("\n  Twin: Logging off. Take care, Ananyaa. 🌙\n")
                break

            tools_to_run = select_tools(user_input)
            tool_output = run_tools(tools_to_run)

            # Handle LLM / Connection errors (Satisfies "What if LLM returns garbage?")
            recommendation = query_ollama(user_input, tool_output)
            
            if not recommendation or len(recommendation) < 5:
                raise ValueError("LLM returned insufficient or garbage output.")

            report = build_trace_report(user_input, tools_to_run, tool_output, recommendation)
            print(report)

        except Exception as e:
            print(f"\n[System Error] I encountered a glitch: {e}")
            print("Please ensure Ollama is running and your LPI server is active.\n")


if __name__ == "__main__":
    run_agent()
