import tkinter as tk
import customtkinter as ctk
from chatbot_core import ChatBot

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Learning Chatbot")
        self.root.geometry("500x650")
        self.bot = ChatBot()

        # Main frame
        main_frame = ctk.CTkFrame(root, corner_radius=15)
        main_frame.pack(padx=12, pady=12, fill=ctk.BOTH, expand=True)

        # Chat area
        self.chat_canvas = tk.Canvas(main_frame, bg="#23272f", highlightthickness=0)
        self.chat_scrollbar = ctk.CTkScrollbar(main_frame, command=self.chat_canvas.yview)
        self.chat_bubble_frame = tk.Frame(self.chat_canvas, bg="#23272f")
        self.chat_bubble_frame.bind(
            "<Configure>", lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        )
        self.chat_canvas.create_window((0, 0), window=self.chat_bubble_frame, anchor="nw")
        self.chat_canvas.configure(yscrollcommand=self.chat_scrollbar.set)
        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Input area
        input_frame = ctk.CTkFrame(root, corner_radius=10)
        input_frame.pack(padx=12, pady=(0,12), fill=ctk.X, side=tk.BOTTOM)
        self.user_entry = ctk.CTkEntry(
            input_frame, placeholder_text='Type your message...', font=("Segoe UI", 15),
            border_width=0, corner_radius=10
        )
        self.user_entry.pack(side=ctk.LEFT, padx=(8,8), pady=10, fill=ctk.X, expand=True)
        self.user_entry.focus()
        send_button = ctk.CTkButton(
            input_frame, text='Send', command=self.send_message,
            font=("Segoe UI", 13), corner_radius=10, width=80
        )
        send_button.pack(side=ctk.RIGHT, padx=(0,8), pady=10)
        self.user_entry.bind('<Return>', lambda event: self.send_message())

        # Welcome message
        self.add_chat_bubble('Hello! Ask me about Python basics or request a code example.', sender="bot")

    def add_chat_bubble(self, text, sender="bot"):
        bubble_color = "#3a3f4b" if sender == "bot" else "#1976d2"
        text_color = "#eeeeee" if sender == "bot" else "#ffffff"
        anchor = "w" if sender == "bot" else "e"
        padx = (12, 60) if sender == "bot" else (60, 12)
        bubble = tk.Label(
            self.chat_bubble_frame, text=text, bg=bubble_color, fg=text_color,
            font=("Segoe UI", 13), wraplength=340,
            justify=tk.LEFT if sender == "bot" else tk.RIGHT,
            padx=12, pady=8, bd=0, relief=tk.FLAT, anchor=anchor
        )
        bubble.pack(anchor=anchor, padx=padx, pady=4, fill=None)
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def send_message(self):
        user_msg = self.user_entry.get()
        if not user_msg.strip():
            return
        if len(user_msg) > 200:
            self.add_chat_bubble("Message too long! Keep it under 200 chars.", sender="bot")
            return
        self.add_chat_bubble(user_msg, sender="user")
        bot_response = self.bot.get_bot_response(user_msg)
        self.add_chat_bubble(bot_response, sender="bot")
        self.user_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = ctk.CTk()
    app = ChatApp(root)
    root.mainloop()
