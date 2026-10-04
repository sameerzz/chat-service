import os
# unittest is Python's built-in test runner and assertion library.
import unittest
# patch temporarily replaces a real object with a fake (a "mock").
from unittest.mock import patch

from langchain_core.chat_history import InMemoryChatMessageHistory

# chat_service creates its API client when imported, so it needs a key even
# though this test will never call the real API. Supply a dummy key temporarily.
# Mock load_dotenv so our real .env isn't read. Mock Path.exists so the app
# doesn't try to read Cloud Run's /secrets files on this computer.
# These patches are undone after the with block; the imported module remains.
with patch.dict(os.environ, {"OPENAI_API_KEY": "test-only-not-a-real-key"}), \
     patch("dotenv.load_dotenv"), \
     patch("pathlib.Path.exists", return_value=False):
    import chat_service


# Inherit TestCase to get helpers such as self.assertEqual(...).
class ChatServiceTests(unittest.TestCase):
    # unittest automatically runs methods whose names start with "test_".
    def test_chat_returns_reply_and_saves_conversation(self):
        # ARRANGE: prepare an empty conversation for this test.
        history = InMemoryChatMessageHistory()

        # Replace the real chain with a mock and give the app our empty history.
        # This tests our chat logic, not the external model's response quality.
        with patch.object(chat_service, "chain") as model, \
             patch.object(chat_service, "chat_history", history):
            model.invoke.return_value = "Try Atomic Habits!"
            # ACT: run the real chat() function. Its chain.invoke() call is fake.
            reply = chat_service.chat("Recommend a book")

        # ASSERT: check the observed results against what we expect.
        # A failed assertion marks this test as FAIL.
        self.assertEqual(reply, "Try Atomic Habits!")
        # Ensure the model was called exactly once, not skipped or called twice.
        model.invoke.assert_called_once()
        # call_args records the arguments sent to the mock. Check that our
        # user's message actually reached the model.
        self.assertEqual(
            model.invoke.call_args.args[0]["messages"][0].content,
            "Recommend a book",
        )
        # The history should contain the user's message followed by the reply.
        self.assertEqual(len(history.messages), 2)
        self.assertEqual(history.messages[0].content, "Recommend a book")
        self.assertEqual(history.messages[1].content, "Try Atomic Habits!")


if __name__ == "__main__":
    # Starts the runner when this module is executed directly.
    # Test discovery also runs this test without entering this block.
    unittest.main()
