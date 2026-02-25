import os
import json
from typing import List, Dict, Optional

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


# Import the database module for function calling
from src.chatbot.database import execute_sql_query, get_db_schema


class ChatClient:
    """
    Chat client with database function calling support.
    - If mock=True, returns canned responses (no network, no DB access).
    - If real mode: connects to AzureOpenAI and supports function calling to query the database.
    
    The client registers execute_sql_query as a callable tool that the LLM can invoke
    to answer questions about customers and orders.
    """
    
    TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "execute_sql_query",
                "description": "Execute a SELECT query against the customers and orders database. Only SELECT queries are allowed.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sql_query": {
                            "type": "string",
                            "description": "The SQL SELECT query to execute (e.g., 'SELECT * FROM customers WHERE country=?')"
                        }
                    },
                    "required": ["sql_query"]
                }
            }
        }
    ]

    def __init__(self, api_key: Optional[str] = None, endpoint: Optional[str] = None,
                 model: Optional[str] = None, mock: bool = False, enable_db: bool = True):
        self.mock = mock
        self.enable_db = enable_db
        self.deployment_model = None
        self._client = None
        
        if not self.mock:
            api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
            endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
            model = model or os.getenv("DEPLOYMENT_MODEL")
            if not api_key or not endpoint or not model:
                raise RuntimeError(
                    "Missing Azure OpenAI config: set AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT and DEPLOYMENT_MODEL (or run with mock=True)"
                )

            try:
                from openai import AzureOpenAI
                self._client = AzureOpenAI(
                    api_key=api_key,
                    api_version="2025-04-01-preview",
                    azure_endpoint=endpoint,
                )
                self.deployment_model = model
            except Exception as exc:
                raise RuntimeError(
                    "Failed to initialize AzureOpenAI client. Ensure 'openai' is installed and environment variables are set: "
                    f"{exc}"
                ) from exc

    def send(self, messages: List[Dict[str, str]]) -> Dict[str, str]:
        """
        Send a list of messages and get a response from the assistant.
        
        In mock mode: returns a simple echo response.
        In real mode: performs function calling loop:
          1. Send messages + tools to the LLM.
          2. If LLM requests a tool call, execute it and feed result back.
          3. Repeat until LLM provides a final response.
          4. Return the final assistant message.
        """
        if self.mock:
            # Simple deterministic mock: echo the last user message with prefix
            last_user = next((m for m in reversed(messages) if m.get("role") == "user"), {"content": ""})
            return {"role": "assistant", "content": f"[MOCK] Echo: {last_user.get('content', '')}"}

        # Real mode with function calling
        return self._send_with_function_calling(messages)

    def _send_with_function_calling(self, messages: List[Dict[str, str]]) -> Dict[str, str]:
        """
        Implement the function calling loop:
        1. Call LLM with tools.
        2. If it wants to call a tool, execute the tool and add the result to the conversation.
        3. Call LLM again with the new context.
        4. Repeat until we get a final response (no tool call).
        """
        # Make a working copy of messages
        conversation = list(messages)
        
        # Add a system message with DB schema if not already present
        if not any(m.get("role") == "system" for m in conversation):
            db_schema = get_db_schema()
            conversation.insert(0, {
                "role": "system",
                "content": (
                    "You are a helpful database assistant. You can answer questions about customers and orders.\n\n"
                    + db_schema + "\n\n"
                    "When you need to retrieve data, call the execute_sql_query function with an appropriate SELECT query. "
                    "Always use the function to fetch real data before answering."
                )
            })
        
        max_iterations = 5
        for iteration in range(max_iterations):
            response = self._client.chat.completions.create(
                model=self.deployment_model,
                messages=conversation,
                tools=self.TOOLS if self.enable_db else None,
                tool_choice="auto" if self.enable_db else None,
            )
            
            assistant_msg = response.choices[0].message
            
            conversation.append({
                "role": "assistant",
                "content": assistant_msg.content or "",
                "tool_calls": assistant_msg.tool_calls if hasattr(assistant_msg, "tool_calls") else None,
            })
            
            tool_calls = getattr(assistant_msg, "tool_calls", None)
            if not tool_calls:
                return {
                    "role": "assistant",
                    "content": assistant_msg.content or "No response generated."
                }
            
            for tool_call in tool_calls:
                if tool_call.function.name == "execute_sql_query":
                    try:
                        args = json.loads(tool_call.function.arguments)
                        sql_query = args.get("sql_query", "")
                        
                        result = execute_sql_query(sql_query)
                        
                        conversation.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": "execute_sql_query",
                            "content": result,
                        })
                    except json.JSONDecodeError as e:
                        conversation.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": "execute_sql_query",
                            "content": f"Error parsing function arguments: {str(e)}",
                        })
        
        return {
            "role": "assistant",
            "content": "Maximum function calls reached. Unable to complete request."
        }
