import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "clients" / "python"))

import rpcx  # noqa: E402


class FakeResponse:
    def __init__(self, body):
        self.body = json.dumps(body).encode()

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class Client(unittest.TestCase):
    def setUp(self):
        self.client = rpcx.RPCX(api_key="test-key")

    def test_call_sends_named_params_and_parses_result(self):
        sent = {}

        def fake_urlopen(req, timeout):
            sent["headers"] = dict(req.headers)
            sent["body"] = json.loads(req.data)
            return FakeResponse({"jsonrpc": "2.0", "id": 1, "result": {"rows": [{"address": "A"}], "cu": 3, "sources": ["lite_rpc"]}})

        with mock.patch("urllib.request.urlopen", fake_urlopen):
            out = self.client.call("txsFor", wallets=["A"], from_=datetime(2026, 11, 15, 12, tzinfo=timezone.utc), to="2026-11-15T13:00:00Z")
        self.assertEqual(sent["body"]["method"], "rpcx_txsFor")
        self.assertEqual(sent["body"]["params"], {"wallets": ["A"], "from": "2026-11-15T12:00:00Z", "to": "2026-11-15T13:00:00Z"})
        self.assertEqual(sent["headers"]["X-api-key"], "test-key")
        self.assertEqual((out.cu, out.rows, out.sources), (3, [{"address": "A"}], ["lite_rpc"]))

    def test_error_raises(self):
        reply = {"jsonrpc": "2.0", "id": 1, "error": {"code": -32602, "message": "invalid params"}}
        with mock.patch("urllib.request.urlopen", lambda req, timeout: FakeResponse(reply)):
            with self.assertRaises(rpcx.RPCXError) as ctx:
                self.client.call("txsFor", wallets=[])
        self.assertEqual(ctx.exception.code, rpcx.INVALID_PARAMS)

    def test_batch_keeps_order_and_errors(self):
        replies = [
            {"jsonrpc": "2.0", "id": 2, "error": {"code": -32007, "message": "no CU left"}},
            {"jsonrpc": "2.0", "id": 1, "result": {"rows": [], "cu": 1}},
        ]
        with mock.patch("urllib.request.urlopen", lambda req, timeout: FakeResponse(replies)):
            out = self.client.batch([("netSol", {"wallets": ["A"]}), ("holdings", {"owners": ["A"]})])
        self.assertIsInstance(out[0], rpcx.Result)
        self.assertIsInstance(out[1], rpcx.RPCXError)
        self.assertEqual(out[1].code, rpcx.NO_CU_LEFT)


class Methods(unittest.TestCase):
    def test_every_method_file_has_a_matching_header(self):
        files = sorted((ROOT / "methods").glob("*.rpcx"))
        self.assertGreater(len(files), 0)
        for f in files:
            text = f.read_text()
            self.assertIn(f"method {f.stem}(", text, f.name)
            self.assertEqual(text.count("{") , text.count("}"), f.name)


if __name__ == "__main__":
    unittest.main()
