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

Steps are the same on macOS and Windows except where noted.

1. **Install VS Code** — [code.visualstudio.com](https://code.visualstudio.com/), then add the **Python** and **Jupyter** extensions.
   - macOS: unzip and drag `Visual Studio Code.app` into Applications.
   - Windows: run the `.exe` installer and check "Add to PATH".

2. **Install Miniconda** — [docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html).
   - macOS: run the `.pkg` installer, then open a **new** Terminal window.
   - Windows: run the `.exe` installer, then use the **Anaconda Prompt** (installed alongside it) for the commands below instead of a plain Command Prompt.

3. Clone this repo and create the conda environment (identical commands on both OSes — run in Terminal on macOS, Anaconda Prompt on Windows):

   ```bash
   git clone https://github.com/gates-dost-asti/A2A-MCP_Training.git
   cd A2A-MCP_Training
   conda create -n a2a-mcp-training python=3.12
   conda activate a2a-mcp-training
   pip install -r requirements.txt
   ```

   `requirements.txt` is still being finalized and may change before the workshop — re-run `pip install -r requirements.txt` if you're told it's been updated.

4. Register the environment with Jupyter:

   ```bash
   python -m ipykernel install --user --name a2a-mcp-training
   ```

5. **Install Node.js** — [nodejs.org](https://nodejs.org/) (LTS version: `.pkg` on macOS, `.msi` on Windows), required by some MCP tooling.
6. During the workshop, connect to the training VPN to reach the LLM gateway the notebooks call. To run notebooks outside the training room, edit `BASE_URL` in the relevant track's `gates_openai.py` to point at your own OpenAI-compatible endpoint.

For the full setup guide with troubleshooting, see the [Setup page](https://gates-dost-asti.github.io/A2A-MCP_Training/setup.html) on the training site.
