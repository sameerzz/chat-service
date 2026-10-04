"""Basic checks against an already deployed staging or production service.

Run: python scripts/check_release.py https://YOUR_SERVICE_URL
Add --live-chat to make one real, billable model request.
These manual checks do not automatically gate or roll back Cloud Deploy.
"""
import argparse
import json
import unittest
import urllib.error
import urllib.request


class ReleaseTests(unittest.TestCase):
    base_url = ""
    live_chat = False

    def request(self, path, body=None):
        """Call the deployed API; return status and JSON, including HTTP errors."""
        request = urllib.request.Request(
            self.base_url + path,
            data=None if body is None else json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
        )
        try:
            response = urllib.request.urlopen(request, timeout=30)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            return response.code, json.load(response)

    def test_existing_book(self):
        # The deployed service should return its seeded book.
        status, book = self.request("/books/101")
        self.assertEqual(status, 200)
        self.assertEqual(book["id"], 101)
        self.assertEqual(book["title"], "Atomic Habits")

    def test_missing_book(self):
        # A missing book should produce a useful 404, not a server error.
        status, body = self.request("/books/-1")
        self.assertEqual(status, 404)
        self.assertEqual(body["detail"], "Book not found")

    def test_chat_requires_message(self):
        # Invalid input must be rejected before calling the model.
        status, _ = self.request("/chat", {})
        self.assertEqual(status, 422)

    def test_live_chat(self):
        if not self.live_chat:
            self.skipTest("Use --live-chat to check the real API key and model")
        status, body = self.request("/chat", {"message": "Recommend one book about habits."})
        self.assertEqual(status, 200)
        self.assertIsInstance(body.get("response"), str)
        self.assertTrue(body["response"].strip())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Staging or production HTTPS service URL")
    parser.add_argument("--live-chat", action="store_true")
    args = parser.parse_args()
    if not args.url.startswith("https://"):
        parser.error("Provide the HTTPS Cloud Run service URL")
    ReleaseTests.base_url = args.url.rstrip("/")
    ReleaseTests.live_chat = args.live_chat
    unittest.main(argv=["check_release"], verbosity=2)
