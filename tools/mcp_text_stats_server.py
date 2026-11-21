import json
import sys


TOOL = {
    "name": "text_stats",
    "description": "Count characters, words, and lines in supplied text.",
    "inputSchema": {
        "type": "object",
        "properties": {"text": {"type": "string"}},
        "required": ["text"],
    },
}


def response(request_id, result):
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def text_statistics(text):
    return {
        "character_count": len(text),
        "word_count": len(text.split()),
        "line_count": len(text.splitlines()),
    }


def handle(request):
    method = request.get("method")
    request_id = request.get("id")

    if method == "initialize":
        return response(
            request_id,
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "text-stats", "version": "1.0.0"},
            },
        )
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return response(request_id, {"tools": [TOOL]})
    if method == "tools/call":
        params = request.get("params", {})
        name = params.get("name")
        arguments = params.get("arguments", {})
        if name != "text_stats":
            message = f"Unknown tool: {name}"
            return response(
                request_id,
                {"content": [{"type": "text", "text": message}], "isError": True},
            )
        text = arguments.get("text")
        if not isinstance(text, str):
            return response(
                request_id,
                {
                    "content": [{"type": "text", "text": "text must be a string"}],
                    "isError": True,
                },
            )
        return response(
            request_id,
            {
                "content": [
                    {"type": "text", "text": json.dumps(text_statistics(text), sort_keys=True)}
                ]
            },
        )
    if request_id is not None:
        return response(request_id, {})
    return None


for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    output = handle(json.loads(line))
    if output is not None:
        sys.stdout.write(json.dumps(output) + "\n")
        sys.stdout.flush()
