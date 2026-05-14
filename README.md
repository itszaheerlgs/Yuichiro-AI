# 🤖 Yuichiro AI

A personal AI chat assistant powered by **Groq** (LLaMA 3.3 70B) with persistent memory, switchable personas, text-to-speech, and a sleek dark GUI built with CustomTkinter.

---

## ✨ Features

- **Groq LLaMA 3.3 70B** — Fast inference via the Groq API.
- **Persistent memory** — All conversations are saved to a local SQLite database and restored on the next session.
- **Switchable personas** — Change Yuichiro's role on the fly without restarting.
- **Text-to-Speech (TTS)** — Optionally have responses read aloud via `pyttsx3`.
- **Animated responses** — Bot replies stream character-by-character for a live feel.
- **Copy last response** — One-click clipboard copy of the most recent reply.
- **Export history** — Save the full session as a timestamped JSON file.
- **Token usage tracker** — Live token count displayed in the top bar.
- **Context reset** — Clear active conversation context without wiping the database.
- **Database wipe** — Full SQLite history purge from the settings panel.

---

## 🎭 Personas

| Persona | Description |
|---|---|
| **HIMS Data Analyst** | Specialized in health information management systems |
| **Full-Stack Developer** | Senior dev proficient in Python and PHP |
| **Health IT Specialist** | Focused on health technology and systems |
| **All in One Doctor** | Clinical insights and diagnostic reasoning |
| **General Assistant** | Default all-purpose assistant |

Switch personas at any time via the **⚙ Settings** panel — context updates instantly without losing chat history.

---

## 🚀 Getting Started

### Prerequisites
- Python **3.8+**
- A [Groq API key](https://console.groq.com/)

### Installation

```bash
git clone https://github.com/your-username/yuichiro-ai.git
cd yuichiro-ai
pip install customtkinter groq pyttsx3 pyperclip
```

### Configuration

Open `chatai.py` and replace the API key with your own:

```python
client = Groq(api_key="YOUR_GROQ_API_KEY_HERE")
```

### Running

```bash
python chatai.py
```

---

## 🖥️ Screenshots

> *Add your screenshots here.*

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `customtkinter` | Dark-themed modern GUI |
| `groq` | Groq API client for LLaMA inference |
| `pyttsx3` | Offline text-to-speech engine |
| `pyperclip` | Clipboard access for copy button |
| `sqlite3` | Persistent chat history (built-in) |

---

## 🗂️ Data & Storage

- **`yuichiro_memory.db`** — SQLite database storing all chat history locally.
- **`yuichiro_export_YYYYMMDD_HHMMSS.json`** — JSON export files saved to the working directory on demand.

The last 20 messages are loaded into context on startup to maintain conversational continuity.

---

## ⚠️ Security Note

Do not commit your Groq API key to a public repository. Move it to an environment variable before sharing:

```python
import os
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

## 👤 Author

**Dether/Zaheer Lagos**  
I.T NGANI  
GitHub: [itszaheerlgs](https://github.com/itszaheerlgs)
