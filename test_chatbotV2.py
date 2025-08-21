import unittest
from chatbot_core import ChatBot

class TestChatBot(unittest.TestCase):
    def setUp(self):
        self.bot = ChatBot()

    def test_greeting(self):
        response = self.bot.get_bot_response("hello")
        self.assertIn("hello", response.lower())

    def test_code_example(self):
        response = self.bot.get_bot_response("show me a loop example")
        self.assertIn("loop", response.lower())

    def test_context_awareness(self):
        self.bot.get_bot_response("hello")
        self.bot.get_bot_response("what is a variable?")
        response = self.bot.get_bot_response("explain again")
        self.assertTrue(any(word in response.lower() for word in ["variable", "stores data"]))

if __name__ == "__main__":
    unittest.main()
