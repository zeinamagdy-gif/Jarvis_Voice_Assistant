from . import CONFIG

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
