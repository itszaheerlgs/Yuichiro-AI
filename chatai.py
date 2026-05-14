import customtkinter as ctk
from groq import Groq
import threading
import time
import pyttsx3
import sqlite3
import json
from datetime import datetime
import pyperclip

# --- CORE LOGIC ---
client = Groq(api_key="YOUR_GROQ_API_HERE_EBUTANG")


class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect("yuichiro_memory.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT, content TEXT, timestamp DATETIME)
        """)
        self.conn.commit()

    def save_message(self, role, content):
        timestamp_str = datetime.now().isoformat()
        self.cursor.execute("INSERT INTO chat_history (role, content, timestamp) VALUES (?, ?, ?)",
                            (role, content, timestamp_str))
        self.conn.commit()

    def load_recent(self, limit=20):
        self.cursor.execute("SELECT role, content FROM chat_history ORDER BY id DESC LIMIT ?", (limit,))
        return [{"role": r, "content": c} for r, c in reversed(self.cursor.fetchall())]


class SettingsModal(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Yuichiro Configuration")
        self.geometry("400x600")
        self.attributes("-topmost", True)
        self.grab_set()

        ctk.CTkLabel(self, text="System Personas", font=("Tahoma", 16, "bold")).pack(pady=20)

        self.persona_menu = ctk.CTkOptionMenu(
            self,
            values=["HIMS Data Analyst", "Full-Stack Developer", "Health IT Specialist", "All in One Doctor",
                    "General Assistant"],
            command=self.change_persona
        )
        self.persona_menu.set(self.parent.current_persona)
        self.persona_menu.pack(pady=10)

        ctk.CTkSwitch(self, text="Voice Response (TTS)", variable=self.parent.voice_var).pack(pady=10)

        ctk.CTkLabel(self, text="Session Tools", font=("Tahoma", 11)).pack(pady=(15, 5))
        ctk.CTkButton(self, text="Reset Active Context", fg_color="#333333",
                      command=self.parent.reset_context).pack(pady=5)
        ctk.CTkButton(self, text="Export History (JSON)", fg_color="#2b2b2b",
                      command=self.parent.export_chat).pack(pady=5)

        ctk.CTkLabel(self, text="Danger Zone", font=("Tahoma", 11), text_color="red").pack(pady=(15, 5))
        ctk.CTkButton(self, text="Wipe SQLite Database", fg_color="#442222", hover_color="#661111",
                      command=self.parent.clear_db).pack(pady=5)

        ctk.CTkButton(self, text="Close", width=100, command=self.destroy).pack(pady=20)

    def change_persona(self, choice):
        self.parent.current_persona = choice
        if choice == "HIMS Data Analyst":
            prompt = "You are Yuichiro, a specialized HIMS Data Analyst at DGTHMC."
        elif choice == "Full-Stack Developer":
            prompt = "You are Yuichiro, a Senior Full-Stack Developer proficient in Python and PHP."
        elif choice == "All in One Doctor":
            prompt = "You are Yuichiro, an 'All in One Doctor' providing clinical insights and diagnostic reasoning."
        else:
            prompt = "You are Yuichiro, a professional AI assistant developed by Dether Lagos."

        self.parent.messages_history[0] = {"role": "system", "content": prompt}
        self.parent.log(f"--- SYSTEM: ROLE CHANGED TO {choice.upper()} ---\n\n", is_system=True)


class GroqBotGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.db = DatabaseManager()
        self.current_persona = "Full-Stack Developer"
        self.voice_var = ctk.StringVar(value="off")
        self.usage_text = ctk.StringVar(value="Tokens: 0")

        self.base_prompt = {"role": "system", "content": "You are Yuichiro, developed by Dether Lagos."}

        saved_history = self.db.load_recent()
        self.messages_history = [self.base_prompt]
        if saved_history:
            self.messages_history.extend(saved_history)

        try:
            self.engine = pyttsx3.init()
        except:
            self.engine = None

        self.title("Yuichiro AI - HIMS Edition")
        self.geometry("900x750")
        ctk.set_appearance_mode("dark")
        self.bg_color = "#121212"
        self.configure(fg_color=self.bg_color)
        self.main_font = ("Tahoma", 12)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Top Bar
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        self.status_dot = ctk.CTkLabel(self.top_frame, text="•", text_color="#444444", font=("Tahoma", 24))
        self.status_dot.pack(side="left")
        self.usage_label = ctk.CTkLabel(self.top_frame, textvariable=self.usage_text, font=("Tahoma", 10),
                                        text_color="gray")
        self.usage_label.pack(side="left", padx=15)
        self.settings_btn = ctk.CTkButton(self.top_frame, text="⚙ Settings", width=80, height=30, fg_color="#1f1f1f",
                                          command=lambda: SettingsModal(self))
        self.settings_btn.pack(side="right")

        # Chat Textbox
        self.chat_box = ctk.CTkTextbox(self, state="disabled", wrap="word", font=self.main_font, fg_color=self.bg_color,
                                       border_width=0)
        self.chat_box.grid(row=1, column=0, sticky="nsew", padx=30)

        # FIXED: Removed 'font' from tag_config as it is forbidden in CustomTkinter Textbox
        self.chat_box.tag_config("user_tag", foreground="#00FFFF")
        self.chat_box.tag_config("bot_tag", foreground="#D1D1D1")
        self.chat_box.tag_config("system_tag", foreground="#555555")

        # Input Area
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=(0, 30))
        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Ask Yuichiro...", height=50,
                                  border_color="#222222", fg_color="#181818", font=self.main_font)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", lambda e: self.send())
        self.copy_btn = ctk.CTkButton(self.input_frame, text="📋", width=40, height=50, fg_color="#1f1f1f",
                                      command=self.copy_last_response)
        self.copy_btn.pack(side="right", padx=(10, 0))

        if saved_history:
            self.log("--- SYSTEM: DGTHMC SESSION RESTORED ---\n\n", is_system=True)
            for msg in saved_history:
                role_label = "YOU: " if msg['role'] == "user" else "YUICHIRO: "
                self.log(f"{role_label}{msg['content']}\n\n", is_user=(msg['role'] == "user"))

    def log(self, text, is_user=False, is_system=False):
        self.chat_box.configure(state="normal")
        tag = "system_tag" if is_system else ("user_tag" if is_user else "bot_tag")
        self.chat_box.insert("end", text, tag)
        self.chat_box.configure(state="disabled")
        self.chat_box.see("end")

    def animate(self, text):
        if self.voice_var.get() == "on" and self.engine:
            threading.Thread(target=lambda: (self.engine.say(text), self.engine.runAndWait()), daemon=True).start()

        self.log("YUICHIRO: ", is_user=False)
        for char in text:
            self.chat_box.configure(state="normal")
            self.chat_box.insert("end", char, "bot_tag")
            self.chat_box.configure(state="disabled")
            self.chat_box.see("end")
            self.update()
            time.sleep(0.003)
        self.log("\n\n", is_user=False)

    def fetch(self):
        try:
            self.status_dot.configure(text_color="#3b8ed0")
            comp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=self.messages_history,
                                                  temperature=0.6)
            res = comp.choices[0].message.content
            self.usage_text.set(f"Tokens: {comp.usage.total_tokens}")
            self.messages_history.append({"role": "assistant", "content": res})
            self.db.save_message("assistant", res)
            self.after(0, self.animate, res)
        except Exception as e:
            self.after(0, self.log, f"Runtime Error: {str(e)}\n\n", is_system=True)
        finally:
            self.after(0, lambda: self.status_dot.configure(text_color="#444444"))

    def send(self):
        msg = self.entry.get()
        if not msg: return
        self.entry.delete(0, 'end')
        self.log(f"YOU: {msg}\n\n", is_user=True)
        self.messages_history.append({"role": "user", "content": msg})
        self.db.save_message("user", msg)
        threading.Thread(target=self.fetch, daemon=True).start()

    def reset_context(self):
        self.messages_history = [self.base_prompt]
        self.log("--- SYSTEM: CONTEXT RESET ---\n\n", is_system=True)

    def copy_last_response(self):
        last_msg = next((m['content'] for m in reversed(self.messages_history) if m['role'] == 'assistant'), "")
        if last_msg:
            pyperclip.copy(last_msg)
            self.status_dot.configure(text_color="#4CAF50")
            self.after(1000, lambda: self.status_dot.configure(text_color="#444444"))

    def export_chat(self):
        filename = f"yuichiro_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(self.messages_history, f, indent=4)

    def clear_db(self):
        self.db.cursor.execute("DELETE FROM chat_history")
        self.db.conn.commit()
        self.chat_box.configure(state="normal")
        self.chat_box.delete("1.0", "end")
        self.chat_box.configure(state="disabled")
        self.log("--- SYSTEM: DATABASE WIPED ---\n\n", is_system=True)


if __name__ == "__main__":
    app = GroqBotGUI()
    app.mainloop()