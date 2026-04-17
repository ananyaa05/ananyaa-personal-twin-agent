# ananyaa-personal-twin-agent
A Personal Twin agent built for LPI Developer Kit Level 3. This repository contains a Lifestyle Balance Agent designed to help a Computer Science student manage heavy academic workloads (C++, ML, Cloud) while prioritizing mental well-being through creative hobbies like baking and poetry.

## Key Features
  1. Context-Aware Reasoning: Analyzes real-time energy levels, mood, and pending tasks to suggest the best activity.
  2. Explainable AI (XAI): Provides a full "Trace Report" showing exactly which data points were used to make a recommendation.
  3. Local Execution: Powered by Ollama (TinyLlama) to ensure data privacy and zero-cost offline processing.

## LPI Tools Integrated
  The agent queries the following LPI tools to build context:
  * `log_energy_level`: Monitors cognitive bandwidth.
  * `log_mood_state`: Tracks emotional readiness.
  * `get_pending_tasks`: Analyzes CSE academic workload.
  * `get_creative_log`: Monitors creative engagement (Baking/Poetry).
  * `get_exercise_log`: Tracks physical well-being.

## Tech Stack
  1. Language: Python 3.x
  2. Brain: TinyLlama (via Ollama)
  3. Architecture: Tool-augmented generation (simulating LPI Tool interaction)

## How It Works (Explainable AI)
The agent follows a strict 4-step logical flow:
  1. Analyzes user input keywords to decide which LPI tools to query.
  2. Gathers data from tools like log_energy_level and get_pending_tasks.
  3. Passes the tool context + user mood to the local SLM (Small Language Model).
  4. Outputs a human-readable trace log so the user knows why the decision was made.

## How to Run Locally
  1. Install Ollama on your system.
  2. Pull the model using command "ollama pull tinyllama" on your terminal.
  3. Run the agent.py file and give your input.
