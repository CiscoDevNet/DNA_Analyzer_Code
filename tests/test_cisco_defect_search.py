import importlib.util
import os
from pathlib import Path
import unittest

try:
    from unittest import mock
except ImportError:  # pragma: no cover - Python 2 compatibility
    import mock

MODULE_PATH = Path(__file__).parents[1] / "dna_analyzer/search/Cisco_Defect_search.py"
SPEC = importlib.util.spec_from_file_location("Cisco_Defect_search", str(MODULE_PATH))
Cisco_Defect_search = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(Cisco_Defect_search)


class GetTokenTest(unittest.TestCase):
    def test_requires_runtime_credentials(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError) as context:
                Cisco_Defect_search.get_token()

        message = str(context.exception)
        self.assertIn("CISCO_API_CLIENT_ID", message)
        self.assertIn("CISCO_API_CLIENT_SECRET", message)

    def test_uses_runtime_credentials(self):
        credentials = {
            "CISCO_API_CLIENT_ID": "test-client",
            "CISCO_API_CLIENT_SECRET": "test-secret",
        }

        with mock.patch.object(Cisco_Defect_search.requests, "post") as post:
            response = post.return_value
            response.json.return_value = {"access_token": "test-access-token"}
            with mock.patch.dict(os.environ, credentials, clear=True):
                token = Cisco_Defect_search.get_token()

        self.assertEqual(token, "test-access-token")
        args, kwargs = post.call_args
        self.assertEqual(args[0], Cisco_Defect_search.TOKEN_URL)
        self.assertEqual(kwargs["auth"].username, "test-client")
        self.assertEqual(kwargs["auth"].password, "test-secret")
        self.assertEqual(kwargs["data"], {"grant_type": "client_credentials"})


if __name__ == "__main__":
    unittest.main()
