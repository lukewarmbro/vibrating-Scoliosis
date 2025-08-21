# --- Hugging Face GPT-2 Setup ---
from transformers import pipeline, set_seed
import torch

# Load GPT-2 model and pipeline (only once, at startup)
try:
    gpt2_pipe = pipeline('text-generation', model='gpt2', device=0 if torch.cuda.is_available() else -1)
except Exception as e:
    gpt2_pipe = None
    print(f"GPT-2 model could not be loaded: {e}")
# --- Simple code example handler ---
def get_code_example(user_input):
    # This is a placeholder. You can expand this with more logic or database queries.
    if "loop" in user_input:
        return "Here's a Python loop example:\nfor i in range(5):\n    print(i)"
    if "function" in user_input:
        return "Here's a Python function example:\ndef greet():\n    print('Hello!')"
    if "list" in user_input:
        return "Here's a Python list example:\nfruits = ['apple', 'banana', 'cherry']"
    return "Sorry, I don't have a code example for that yet. Try asking about a loop, function, or list."


# --- No NLTK: All tokenization and complexity checks removed ---

# --- Imports ---
import requests
import customtkinter as ctk
import sqlite3
import tkinter as tk
import sympy
from tkinter import scrolledtext, Canvas
from bs4 import BeautifulSoup
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


# --- Database setup ---
conn = sqlite3.connect('chatbot.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS facts (key TEXT PRIMARY KEY, value TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS code_examples (id INTEGER PRIMARY KEY, language TEXT, snippet TEXT, explanation TEXT)''')
conn.commit()


# --- Responses dictionary ---
responses = {
    'hello': 'Hello! How can I help you learn Python today?',
    'variable': 'A variable stores data. Example: x = 5',
    'loop': 'A loop repeats code. Example: for i in range(5): print(i)',
    'function': 'A function is a block of code. Example: def greet(): print("Hi")',
    'list': 'A list holds items. Example: fruits = ["apple", "banana"]',
    'tuple': 'A tuple is like a list but unchangeable. Example: coords = (1, 2)',
    'bye': 'Goodbye! Happy coding!'
}


# --- Global state for visual confirmation ---
awaiting_visual_example = False
last_visual_request = None



# --- Bot logic ---
def get_bot_response(user_input, depth=0):
    global awaiting_visual_example, last_visual_request
    user_input = user_input.strip()
    # Handle confirmation for visual example
    if awaiting_visual_example:
        if "yes" in user_input.lower():
            awaiting_visual_example = False
            return generate_visual_example_response(last_visual_request)
        elif "no" in user_input.lower():
            awaiting_visual_example = False
            return "Okay, let me know if you want a visual example later."
        else:
            return "Please answer 'yes' or 'no' if you want a visual example."

    # Python help topics (fallback)
    topics = {
        "variable": "A variable stores data. Example: x = 5",
        "loop": "A loop repeats code. Example: for i in range(5): print(i)",
        "function": "A function is a block of code. Example: def greet(): print('Hi')",
        "list": "A list holds items. Example: fruits = ['apple', 'banana']",
        "tuple": "A tuple is like a list but unchangeable. Example: coords = (1, 2)",
        "dictionary": "A dictionary stores key-value pairs. Example: ages = {'Alice': 30, 'Bob': 25}",
        "set": "A set is a collection of unique items. Example: nums = {1, 2, 3}"
    }
    for key, val in topics.items():
        if key in user_input.lower():
            awaiting_visual_example = True
            last_visual_request = key
            return val + "\nWould you like a visual example? (yes/no)"

    # Wikipedia search
    if "wikipedia" in user_input.lower() or "wiki" in user_input.lower() or user_input.lower().startswith('search'):
        topic = user_input.lower().replace('search', '').replace('wikipedia', '').replace('wiki', '').strip()
        if topic:
            url = f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    summary = soup.find('p').text[:200] + '...'
                    return f"Summary on {topic}: {summary}"
                return "Couldn't find that on Wikipedia."
            except Exception as e:
                return f"Error searching: {str(e)}"
        return "What topic would you like to search on Wikipedia?"

    # Code example request
    if "example" in user_input.lower() or "code" in user_input.lower():
        return get_code_example(user_input)

    # Math evaluation
    if any(op in user_input for op in ["+", "-", "*", "/", "^"]):
        try:
            result = sympy.sympify(user_input)
            return f"Math result: {result}"
        except Exception:
            pass

    # Goodbye
    if any(bye in user_input.lower() for bye in ["bye", "goodbye", "see you"]):
        return "Goodbye! Happy coding!"

    # Query DB for facts
    cursor.execute("SELECT value FROM facts WHERE key LIKE ?", (f"%{user_input}%",))
    db_result = cursor.fetchone()
    if db_result:
        return f"From my database: {db_result[0]}"

    # Query DB for code examples
    cursor.execute("SELECT snippet, explanation FROM code_examples WHERE language LIKE ? OR explanation LIKE ?", (f"%{user_input}%", f"%{user_input}%"))
    code_result = cursor.fetchone()
    if code_result:
        snippet, explanation = code_result
        return f"Code example: {snippet}\nExplanation: {explanation}"

    # --- GPT-2 fallback for general conversation ---
    if gpt2_pipe:
        try:
            gpt2_out = gpt2_pipe(user_input, max_length=60, num_return_sequences=1, pad_token_id=50256)
            return gpt2_out[0]['generated_text'].strip()
        except Exception as e:
            return f"[GPT-2 error: {e}]"

    # Fallback
    return (
        "I'm not sure about that. Try rephrasing, ask about Python basics, or request an example!\n"
        "You can ask about variables, loops, functions, lists, tuples, dictionaries, sets, or request code examples."
    )



# --- Visual example response helper ---
def generate_visual_example_response(user_input):
    if "function" in user_input:
        return "Here's a visual example of a function:\n[def greet():\n    print('Hi')]\n(Imagine a diagram here!)"
    elif "loop" in user_input:
        return "Here's a visual example of a loop:\n[for i in range(5):\n    print(i)]\n(Imagine a diagram here!)"
    elif "variable" in user_input:
        return "Here's a visual example of a variable:\n[x = 5]\n(Imagine a box labeled 'x' with value 5)"
    else:
        return "Sorry, I don't have a visual for that yet."



# --- Modern Chat UI Setup ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
root = ctk.CTk()
root.title('Python Learning Chatbot')
root.geometry('500x650')

# Main frame for chat and input
main_frame = ctk.CTkFrame(root, corner_radius=15)
main_frame.pack(padx=12, pady=12, fill=ctk.BOTH, expand=True)

# Scrollable chat area (using Canvas for chat bubbles)
chat_canvas = tk.Canvas(main_frame, bg="#23272f", highlightthickness=0)
chat_scrollbar = ctk.CTkScrollbar(main_frame, command=chat_canvas.yview)
chat_bubble_frame = tk.Frame(chat_canvas, bg="#23272f")
chat_bubble_frame.bind(
    "<Configure>", lambda e: chat_canvas.configure(scrollregion=chat_canvas.bbox("all"))
)
chat_canvas.create_window((0, 0), window=chat_bubble_frame, anchor="nw")
chat_canvas.configure(yscrollcommand=chat_scrollbar.set)
chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,0), pady=(0,0))
chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Input area at the bottom
input_frame = ctk.CTkFrame(root, corner_radius=10)
input_frame.pack(padx=12, pady=(0,12), fill=ctk.X, side=tk.BOTTOM)

user_entry = ctk.CTkEntry(
    input_frame,
    placeholder_text='Type your message...',
    font=("Segoe UI", 15),
    border_width=0,
    corner_radius=10
)
user_entry.pack(side=ctk.LEFT, padx=(8,8), pady=10, fill=ctk.X, expand=True)
user_entry.focus()

send_button = ctk.CTkButton(
    input_frame,
    text='Send',
    command=lambda: send_message(),
    font=("Segoe UI", 13),
    corner_radius=10,
    width=80
)
send_button.pack(side=ctk.RIGHT, padx=(0,8), pady=10)

def on_enter(event):
    send_message()
user_entry.bind('<Return>', on_enter)



# --- Chat bubble display logic ---
def add_chat_bubble(text, sender="bot"):
    bubble_color = "#3a3f4b" if sender == "bot" else "#1976d2"
    text_color = "#eeeeee" if sender == "bot" else "#ffffff"
    anchor = "w" if sender == "bot" else "e"
    padx = (12, 60) if sender == "bot" else (60, 12)
    bubble = tk.Label(
        chat_bubble_frame,
        text=text,
        bg=bubble_color,
        fg=text_color,
        font=("Segoe UI", 13),
        wraplength=340,
        justify=tk.LEFT if sender == "bot" else tk.RIGHT,
        padx=12, pady=8,
        bd=0,
        relief=tk.FLAT,
        anchor=anchor
    )
    bubble.pack(anchor=anchor, padx=padx, pady=4, fill=None)
    chat_canvas.update_idletasks()
    chat_canvas.yview_moveto(1.0)

def send_message():
    global awaiting_visual_example, last_visual_request
    try:
        user_msg = user_entry.get()
        if user_msg.strip() == '':
            return
        if len(user_msg) > 200:
            raise ValueError("Message too long! Keep it under 200 chars.")
        add_chat_bubble(user_msg, sender="user")
        bot_response = get_bot_response(user_msg)
        add_chat_bubble(bot_response, sender="bot")
        user_entry.delete(0, tk.END)
    except ValueError as e:
        add_chat_bubble('Error - ' + str(e), sender="bot")


# --- Welcome message ---
add_chat_bubble('Hello! Ask me about Python basics or say "search [topic]" for info.', sender="bot")

root.mainloop()
# --- End of chatbot code ---
