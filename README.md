# Agentic AI: A2A & MCP Training

Materials for the one-day training on Agentic AI, the Model Context Protocol (MCP), and the Agent-to-Agent (A2A) Protocol, run by the GATES Data Lakehouse Component at DOST-ASTI.

**Full training site (lecture decks, exercise write-ups, and worked solutions):**
https://gates-dost-asti.github.io/A2A-MCP_Training/

## What's in this repository

- `Workshop Materials/` — the hands-on notebooks for each track (Agentic AI, MCP, A2A) plus sample data.
- `Presentations/` — lecture deck PDFs.
- `Program - A2A & MCP Training.pdf` — the official schedule and facilitator list.
- `requirements.txt` — Python package list for all notebooks.

## Setup

1. **Python 3.11–3.13** (the A2A track's `beeai-framework` requires <3.14; MCP and A2A SDKs require 3.10+).
2. Clone this repo and create a virtual environment:

   ```bash
   git clone https://github.com/gates-dost-asti/A2A-MCP_Training.git
   cd A2A-MCP_Training
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Register the environment with Jupyter:

   ```bash
   python -m ipykernel install --user --name a2a-mcp-training
   ```

5. During the workshop, connect to the training VPN to reach the LLM gateway the notebooks call. To run notebooks outside the training room, edit `BASE_URL` in the relevant track's `gates_openai.py` to point at your own OpenAI-compatible endpoint.

For the full setup guide with troubleshooting, see the [Setup page](https://gates-dost-asti.github.io/A2A-MCP_Training/setup.html) on the training site.
