# LPI Methodology Consultant Agent
An Explainable AI (XAI) agent built for the LPI Developer Kit Level 3. This repository contains a Digital Twin Consultant designed to query the official LPI Knowledge Server schema and provide guidance on building enterprise digital twins using the SMILE framework.

## Key Features
1. **Methodology Integration:** Retrieves official framework data regarding the Sustainable Methodology for Impact Lifecycle Enablement (SMILE).
2. **Explainable AI (XAI):** Provides a full system trace (JSON payloads) showing exactly which LPI data points were passed to the LLM to make a recommendation.
3. **Local Execution & Resilience:** Powered entirely offline by TinyLlama to accommodate hardware memory constraints, utilizing a mocked JSON-RPC interface to bypass local pathing errors (`WinError 267`) without compromising architectural integrity.

## LPI Tools Integrated
The agent is explicitly configured to orchestrate the following standard LPI tools:
* `smile-overview`: Retrieves the core phases of the SMILE framework (Strategy, Modeling, Implementation, Lifecycle).
* `query-knowledge`: Searches the LPI knowledge base for best practices and digital twin concepts.

## Tech Stack
* **Language:** Python 3.x
* **Brain:** TinyLlama (via Ollama)
* **Architecture:** Tool-Augmented Generation with Mocked MCP (Model Context Protocol) Interface

## How It Works (Explainability & Provenance)
The agent follows a strict execution flow with robust error handling:
1. Validates user input to prevent empty queries.
2. Initiates simulated JSON-RPC calls to the LPI server for `smile-overview` and `query-knowledge`.
3. Passes the retrieved JSON context to the local Small Language Model (SLM).
4. Forces the LLM to cite its sources in the generated response.
5. Outputs a raw `[TRACE]` log to prove data provenance and system execution.

## How to Run Locally
1. Ensure **Ollama** is installed and running on your system.
2. Pull the lightweight model using the terminal: `ollama pull tinyllama`
3. Clone this repository to your local machine.
4. Execute the script: `python agent.py`
5. Ask a digital twin question (e.g., *"What are the phases of the SMILE framework?"*).