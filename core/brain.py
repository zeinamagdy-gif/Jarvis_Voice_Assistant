from . import CONFIG
# core/brain.py (Agentic Version)
import requests
import json
from processor import execute_tool

# Define the tools schema so the AI knows what it can do
TOOL_SCHEMAS = [
    {
        "name": "get_system_info",
        "description": "Get information about the user's operating system and current directory.",
        "parameters": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "list_files",
        "description": "List files and folders in a specific directory.",
        "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}
    },
    {
        "name": "open_application",
        "description": "Open a software application or website on the laptop.",
        "parameters": {"type": "object", "properties": {"app_name": {"type": "string"}}, "required": ["app_name"]}
    },
    {
        "name": "run_shell_command",
        "description": "Run a safe Windows/Mac/Linux terminal command to achieve a task.",
        "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}
    }
]


def ask_ai_agentic(user_input, history):
    """
    Sends the prompt to Ollama/Claude with tools attached.
    If the AI wants to use a tool, it executes it and loops until it has a final text answer.
    """
    messages = history + [{"role": "user", "content": user_input}]

    # Note: Ollama and Claude have slightly different API payloads for tools.
    # Here is the generic Ollama implementation:
    payload = {
        "model": "llama3.2",  # or your configured model
        "messages": messages,
        "tools": TOOL_SCHEMAS,
        "stream": False
    }

    response = requests.post("http://localhost:11434/api/chat", json=payload).json()
    message = response["message"]

    # Check if the AI decided to use a tool
    if "tool_calls" in message and message["tool_calls"]:
        for tool_call in message["tool_calls"]:
            tool_name = tool_call["function"]["name"]
            arguments = tool_call["function"]["arguments"]

            print(f"[PROCESSOR] AI requested tool: {tool_name} with args: {arguments}")

            # 1. Execute the tool on the laptop
            tool_result = execute_tool(tool_name, arguments)
            print(f"[PROCESSOR] Tool result: {tool_result}")

            # 2. Feed the result back to the AI so it can formulate a spoken response
            messages.append(message)  # Add AI's tool request
            messages.append({
                "role": "tool",
                "content": tool_result
            })

        # Ask the AI to summarize the tool result into spoken text
        return ask_ai_agentic("Summarize the tool result for the user.", messages)

    else:
        # No tools needed, just return the text
        return message["content"]
_history = []


def ask(question):
    _history.append({"role": "user", "content": question})
    messages = _history[-10:]

    if CONFIG["brain"] == "ollama":
        import requests
        r = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": CONFIG["ollama_model"],
                "messages": [{"role": "system", "content": CONFIG["system_prompt"]}] + messages,
                "stream": False,
            },
            timeout=120,
        )
        answer = r.json()["message"]["content"]
    else:
        import anthropic
        client = anthropic.Anthropic()  # needs ANTHROPIC_API_KEY
        resp = client.messages.create(
            model=CONFIG["claude_model"],
            max_tokens=300,
            system=CONFIG["system_prompt"],
            messages=messages,
        )
        answer = resp.content[0].text

    _history.append({"role": "assistant", "content": answer})
    return answer
