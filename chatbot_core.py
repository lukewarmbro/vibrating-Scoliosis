import requests
from bs4 import BeautifulSoup
import sympy
"""
chatbot_core.py
Core logic for the modular Python chatbot.
Handles context, responses, and command parsing.
"""

class ChatBot:
    def __init__(self):
        self.history = []  # Stores last 3 (user, bot) message pairs
        self.last_topic = None

    def get_bot_response(self, user_input):
        user_input = user_input.strip().lower()
        if not user_input:
            return "Please enter a message."
        # Add to history
        self.history.append(("user", user_input))
        self.history = self.history[-6:]  # 3 pairs

        # Greetings
        if any(greet in user_input for greet in ["hello", "hi", "hey"]):
            response = "Hello! How can I help you learn Python today?"
            self._add_bot_history(response)
            return response

        # Wikipedia or Python docs search
        if user_input.startswith("search wikipedia for "):
            topic = user_input.replace("search wikipedia for ", "").strip()
            response = self._search_wikipedia(topic)
            self._add_bot_history(response)
            return response
        if user_input.startswith("search python docs for "):
            topic = user_input.replace("search python docs for ", "").strip()
            response = self._search_python_docs(topic)
            self._add_bot_history(response)
            return response

        # More Python help topics/examples
        topics = {
            "variable": "A variable stores data. Example: x = 5",
            "loop": "A loop repeats code. Example: for i in range(5): print(i)",
            "function": "A function is a block of code. Example: def greet(): print('Hi')",
            "list": "A list holds items. Example: fruits = ['apple', 'banana']",
            "tuple": "A tuple is like a list but unchangeable. Example: coords = (1, 2)",
            "dictionary": "A dictionary stores key-value pairs. Example: ages = {'Alice': 30, 'Bob': 25}",
            "set": "A set is a collection of unique items. Example: nums = {1, 2, 3}",
            "comprehension": "A list comprehension is a concise way to create lists. Example: squares = [x*x for x in range(5)]",
            "exception": "Exceptions handle errors. Example: try: ... except Exception as e: ...",
            "import": "Use import to include modules. Example: import math",
            "class": "A class defines a blueprint for objects. Example: class Dog: pass"
        }
        for key, val in topics.items():
            if key in user_input:
                self.last_topic = key
                self._add_bot_history(val)
                return val

        # Code execution or math solving
        if user_input.startswith("run code:"):
            code = user_input.replace("run code:", "").strip()
            response = self._run_code(code)
            self._add_bot_history(response)
            return response
        if user_input.startswith("solve:"):
            expr = user_input.replace("solve:", "").strip()
            response = self._solve_math(expr)
            self._add_bot_history(response)
            return response

        # Contextual follow-up
        if "explain again" in user_input and self.last_topic:
            if self.last_topic in topics:
                response = topics[self.last_topic]
            else:
                response = f"Here's what I last explained: {self.last_topic}"
            self._add_bot_history(response)
            return response

        # Fallback
        response = "I'm not sure about that. Try asking about Python basics, request a code example, or search Wikipedia/Python docs."
        self._add_bot_history(response)
        return response

    def _search_wikipedia(self, topic):
        if not topic:
            return "Please provide a topic to search on Wikipedia."
        url = f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                p = soup.find('p')
                if p:
                    return f"Wikipedia: {p.text.strip()[:400]}..."
                return "No summary found on Wikipedia."
            return "Couldn't find that on Wikipedia."
        except Exception as e:
            return f"Error searching Wikipedia: {e}"

    def _search_python_docs(self, topic):
        if not topic:
            return "Please provide a topic to search in Python docs."
        url = f"https://docs.python.org/3/search.html?q={topic.replace(' ', '+')}"
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                results = soup.find_all('li', class_='search-hit')
                if results:
                    first = results[0].get_text(strip=True)
                    return f"Python Docs: {first[:400]}..."
                return "No results found in Python docs."
            return "Couldn't search Python docs."
        except Exception as e:
            return f"Error searching Python docs: {e}"

    def _run_code(self, code):
        try:
            # Only allow safe built-ins
            allowed_builtins = {'print': print, 'range': range, 'len': len, 'str': str, 'int': int, 'float': float, 'list': list, 'dict': dict, 'set': set, 'tuple': tuple}
            local_vars = {}
            exec(code, {'__builtins__': allowed_builtins}, local_vars)
            return f"Code executed. Locals: {local_vars}"
        except Exception as e:
            return f"Error running code: {e}"

    def _solve_math(self, expr):
        try:
            result = sympy.sympify(expr)
            return f"Math result: {result}"
        except Exception as e:
            return f"Error solving math: {e}"

    def _add_bot_history(self, response):
        self.history.append(("bot", response))
        self.history = self.history[-6:]
