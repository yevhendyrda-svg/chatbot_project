import argparse
from src.chatbot.client import ChatClient


def interactive(mock: bool, verbose: bool = False):
    """
    Args:
        mock: If True, use mock mode (no network, no DB).
        verbose: If True, show function calls and raw responses.
    """
    client = ChatClient(mock=mock)
    
    if mock:
        messages = [{"role": "system", "content": "You are a helpful assistant."}]
    else:
        messages = []
    
    print("Start chatting.")
    if verbose:
        print("[Verbose mode enabled - function calls will be shown]")

    try:
        while True:
            user = input("User: ").strip()
            if not user:
                continue
            messages.append({"role": "user", "content": user})
            
            if verbose:
                print("[Sending to LLM...]")
            
            try:
                resp = client.send(messages)
                
                messages.append({"role": "assistant", "content": resp["content"]})
                print("Assistant:", resp["content"])
            except Exception as e:
                # Handle API errors, timeouts, network issues, etc.
                error_msg = str(e)
                if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                    print("Error: Request timed out. The DIAL endpoint may be unreachable or slow.")
                    print("       Check your network connection and endpoint URL.")
                    print("       To test locally without network, use: python -m src.chatbot.cli --mock")
                elif "api" in error_msg.lower() or "unauthorized" in error_msg.lower():
                    print("Error: API authentication failed. Check your AZURE_OPENAI_API_KEY in .env")
                elif "connection" in error_msg.lower():
                    print("Error: Connection failed. Check your network and endpoint URL.")
                else:
                    print(f"Error: {error_msg}")
                print("       Continuing...\n")
                
    except (EOFError, KeyboardInterrupt):
        print("\nBye.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chatbot CLI with database access via function calling")
    parser.add_argument("--mock", action="store_true", help="Use mock mode (no network calls, no DB access)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show verbose output including function calls")
    args = parser.parse_args()
    interactive(args.mock, args.verbose)
