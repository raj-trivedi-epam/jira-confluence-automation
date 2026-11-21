import json
import unittest

from tools.mcp_text_stats_server import handle, text_statistics


class TextStatsServerTests(unittest.TestCase):
    def test_counts_characters_words_and_lines(self):
        self.assertEqual(
            {"character_count": 14, "word_count": 3, "line_count": 2},
            text_statistics("MCP tools\nhelp"),
        )

    def test_tool_call_returns_statistics_as_json_text(self):
        result = handle(
            {
                "jsonrpc": "2.0",
                "id": 7,
                "method": "tools/call",
                "params": {
                    "name": "text_stats",
                    "arguments": {"text": "Weekly status: 3 tasks done."},
                },
            }
        )
        self.assertEqual(
            {"jsonrpc": "2.0", "id": 7},
            {key: result[key] for key in ("jsonrpc", "id")},
        )
        self.assertEqual(
            {
                "character_count": 28,
                "line_count": 1,
                "word_count": 5,
            },
            json.loads(result["result"]["content"][0]["text"]),
        )

    def test_rejects_non_string_text(self):
        result = handle(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "text_stats", "arguments": {"text": 42}},
            }
        )
        self.assertTrue(result["result"]["isError"])


if __name__ == "__main__":
    unittest.main()
