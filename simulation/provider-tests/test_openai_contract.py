"""Offline transport test using the official OpenAI SDK."""
import json
import os
import unittest
from unittest.mock import patch

import httpx

from archon.cycle import DEFAULTS
from archon.provider import Offline, OpenAIProvider


class ResponsesContractTest(unittest.TestCase):
    def test_sdk_uses_structured_responses_without_tools_or_storage(self):
        calls = []
        output = Offline().decide({"period": 0}, DEFAULTS).output

        def endpoint(request):
            self.assertEqual("https://api.openai.com/v1/responses", str(request.url))
            body = json.loads(request.content)
            calls.append(body)
            return httpx.Response(200, json={
                "id": "resp_fixture", "object": "response", "model": "fixture-provider-revision",
                "status": "completed",
                "usage": {"input_tokens": 100, "output_tokens": 30, "total_tokens": 130},
                "output": [{"type": "message", "id": "msg_fixture", "role": "assistant", "status": "completed",
                            "content": [{"type": "output_text", "text": output, "annotations": []}]}],
            })

        transport = httpx.MockTransport(endpoint)
        class TransportClient(httpx.Client):
            def __init__(self, **kwargs):
                super().__init__(transport=transport, **kwargs)
        with patch.dict(os.environ, {"OPENAI_API_KEY": "fixture-only-not-a-real-key"}):
            with patch("httpx.Client", TransportClient):
                provider = OpenAIProvider("fixture-requested-model", 3)
                reply = provider.decide({"period": 0}, DEFAULTS)
        self.assertEqual(1, len(calls))
        self.assertIs(calls[0]["store"], False)
        self.assertNotIn("tools", calls[0])
        self.assertEqual("fixture-requested-model", calls[0]["model"])
        self.assertEqual("json_schema", calls[0]["text"]["format"]["type"])
        self.assertEqual((output, 100, 30, "fixture-provider-revision"),
                         (reply.output, reply.input_tokens, reply.output_tokens, reply.model))
