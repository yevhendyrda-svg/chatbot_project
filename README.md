Simple Chatbot (AzureOpenAI)

Overview
- Small Python project demonstrating a simple chatbot client that can use the AzureOpenAI endpoint or run in a local mock mode for testing.

Files
- src/chatbot/client.py - Chat client wrapper (real and mock modes)
- src/chatbot/cli.py - Small interactive CLI
- 	ests/ - Unit tests
- 
equirements.txt - Python dependencies
- .env.example - Example env variables

Quick start (mock mode)
1. Create and enter a virtual environment (optional but recommended).

PowerShell:
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt

2. Run the CLI in mock mode (no API key required):

python -m src.chatbot.cli --mock

Quick start (real AzureOpenAI)
1. Install dependencies (see above).
2. Copy .env.example to .env and set your values:

AZURE_OPENAI_API_KEY=dial-...
AZURE_OPENAI_ENDPOINT=
DEPLOYMENT_MODEL=gpt-4o

3. Run the CLI (without --mock):

python -m src.chatbot.cli

Notes
- The project supports a --mock flag that avoids calling the network so tests and demos can run offline.
- This scaffold is intentionally small. Adjust models, error handling, and tests as needed for the course task.


