import json
import sys
from datetime import datetime


TOOLS = [
    {
        "name": "calculate",
        "description": "Perform an arithmetic operation on two numbers.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"},
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                },
            },
            "required": ["a", "b", "operation"],
        },
    },
    {
        "name": "get_time",
        "description": "Return the current local date and time with its timezone.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "echo",
        "description": "Return the supplied text unchanged.",
        "inputSchema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
    {
        "name": "echo_upper",
        "description": "Return the supplied text converted to uppercase.",
        "inputSchema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
    {
        "name": "echo_length",
        "description": "Return the character length of the supplied text.",
        "inputSchema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
]


def response(request_id, result):
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def handle(request):
    method = request.get("method")
    request_id = request.get("id")

    if method == "initialize":
        return response(
            request_id,
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "echo", "version": "1.0.0"},
            },
        )
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return response(request_id, {"tools": TOOLS})
    if method == "tools/call":
        params = request.get("params", {})
        name = params.get("name")
        arguments = params.get("arguments", {})
        if name == "calculate":
            a = arguments.get("a")
            b = arguments.get("b")
            operation = arguments.get("operation")
            if not isinstance(a, (int, float)) or isinstance(a, bool):
                result = "a must be a number"
            elif not isinstance(b, (int, float)) or isinstance(b, bool):
                result = "b must be a number"
            elif operation == "add":
                result = str(a + b)
            elif operation == "subtract":
                result = str(a - b)
            elif operation == "multiply":
                result = str(a * b)
            elif operation == "divide":
                if b == 0:
                    result = "Cannot divide by zero"
                else:
                    result = str(a / b)
            else:
                result = "Unknown operation"
            is_error = result in {
                "a must be a number",
                "b must be a number",
                "Cannot divide by zero",
                "Unknown operation",
            }
            return response(
                request_id,
                {
                    "content": [{"type": "text", "text": result}],
                    "isError": is_error,
                },
            )
        if name == "get_time":
            current_time = datetime.now().astimezone().isoformat(
                sep=" ", timespec="seconds"
            )
            return response(
                request_id,
                {"content": [{"type": "text", "text": current_time}]},
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
        if name == "echo":
            result_text = text
        elif name == "echo_upper":
            result_text = text.upper()
        elif name == "echo_length":
            result_text = str(len(text))
        else:
            return response(
                request_id,
                {
                    "content": [{"type": "text", "text": f"Unknown tool: {name}"}],
                    "isError": True,
                },
            )
        return response(
            request_id,
            {"content": [{"type": "text", "text": result_text}]},
        )
    if request_id is not None:
        return response(request_id, {})
    return None


for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        request = json.loads(line)
        output = handle(request)
        if output is not None:
            sys.stdout.write(json.dumps(output) + "\n")
            sys.stdout.flush()
    except json.JSONDecodeError:
        continue
