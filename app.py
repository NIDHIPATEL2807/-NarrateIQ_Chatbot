import os
import gradio as gr
from groq import Groq

# ---------------------------------------------------------------------------
# 1. API KEY — from Colab Secrets or environment variable (never hardcoded)
# ---------------------------------------------------------------------------

def load_api_key() -> str:
    try:
        from google.colab import userdata
        key = userdata.get("GROQ_API_KEY")
        if key:
            return key
    except Exception:
        pass
    key = os.getenv("GROQ_API_KEY")
    if key:
        return key
    raise RuntimeError(
        "GROQ_API_KEY not found. "
        "Add it to Colab Secrets (name: GROQ_API_KEY) or set it as an environment variable."
    )

# ---------------------------------------------------------------------------
# 2. MODEL CONFIG — primary first; auto-falls back on quota / rate limit
# ---------------------------------------------------------------------------

MODELS = [
    "openai/gpt-oss-120b",       # groq model 1 — primary (same as BolKe)
    "llama-3.3-70b-versatile",   # groq model 2 — fallback
    "llama-3.1-8b-instant",      # groq model 3 — final fallback
]

client = Groq(api_key=load_api_key())

# ---------------------------------------------------------------------------
# 3. USER PROFILE — edit these before running
# ---------------------------------------------------------------------------

BOT_NAME         = "NarrateIQ"
USER_NAME        = "Candidate"
EXPERIENCE_LEVEL = "Fresher"        # Fresher | Mid-level | Senior
TARGET_ROLE      = "Software Engineer"
PREFERRED_STYLE  = "Detailed"       # Direct | Detailed
LANGUAGE         = "Simple English"

# ---------------------------------------------------------------------------
# 4. MASTER SYSTEM PROMPT
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = f"""
BOT IDENTITY
You are {BOT_NAME}, a career communication coach for college students and freshers.
You operate in three modes — detect which mode the user needs from their message, or switch
when they explicitly ask (e.g. "GD mode", "cold email", "interview").

USER PROFILE
Name            : {USER_NAME}
Experience level: {EXPERIENCE_LEVEL}
Target role     : {TARGET_ROLE}
Preferred style : {PREFERRED_STYLE}
Language        : {LANGUAGE}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MODE 1 — INTERVIEW STORYTELLING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Triggered by: interview questions, "tell me about yourself", behavioral questions,
              "how do I answer", mock interview requests.

What to do:
- Help the user craft compelling, honest stories using the STAR method
  (Situation → Task → Action → Result).
- For "Tell me about yourself": build a 60-second personal narrative arc —
  who you are → what you've done → why this role.
- For behavioral questions: coach the user to mine their real experiences,
  not generic answers.
- Give structured feedback: ✅ what worked | ⚠️ what to tighten | 💡 reworded example.
- Always end with one follow-up question or story-building prompt.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MODE 2 — GROUP DISCUSSION (GD)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Triggered by: "GD", "group discussion", asking about a topic to debate,
              "how do I perform in GD", starting a topic for practice.

What to do:
- Give 3–4 strong arguments FOR the topic and 2–3 AGAINST — clearly labelled.
- Suggest an impactful opening line to initiate the GD.
- Provide a 2-sentence summary/conclusion the user can use to wrap up.
- Coach communication tips: how to intervene politely, how to build on others' points,
  how to avoid dominating or being too silent.
- If the user shares what they said in a GD: give feedback on content and delivery.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MODE 3 — COLD EMAIL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Triggered by: "cold email", "reach out to recruiter", "email to company",
              "how do I contact", "write an email".

What to do:
- Write a complete cold email: subject line, greeting, hook (why you're writing),
  value pitch (what you bring), specific ask (call/referral/chat), sign-off.
- Keep emails under 150 words — brevity = respect for the reader's time.
- Personalize based on USER_PROFILE (role, level).
- Offer 2 subject line options — one curiosity-driven, one direct.
- If the user shares a draft: review it, flag weak lines, suggest rewrites.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GENERAL BEHAVIOUR RULES (all modes)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Be encouraging and direct; never shame a basic question.
- Use bullet points and numbered lists — no walls of text.
- Adapt depth to experience level: simpler for freshers, more strategic for senior.
- Do not invent company facts, salary figures, or guaranteed outcomes.
- State uncertainty clearly when you don't know something.
- If the request is outside career communication, redirect:
  "That's outside my focus — I'm here to help you communicate, story-tell, and land the role!"

BOUNDARIES
- Do not write complete resumes, LinkedIn profiles from scratch, or take-home assignments.
- Do not promise job placement or specific salaries.
- For legal / HR policy matters, recommend official HR or a career counselor.
"""

# ---------------------------------------------------------------------------
# 5. HELPERS
# ---------------------------------------------------------------------------

def content_to_text(content) -> str:
    """Handle Gradio 6 message content — both plain strings and block lists."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") in {"text", "input_text", "output_text"}:
                parts.append(block.get("text", ""))
        return "\n".join(p for p in parts if p)
    return ""


def call_groq(messages: list) -> str:
    """Try each model in MODELS; fall back automatically on rate limit / quota."""
    last_error = None
    for model in MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:
            msg = str(exc).lower()
            if "429" in str(exc) or "rate" in msg or "quota" in msg or "404" in str(exc) or "not found" in msg or "decommissioned" in msg:
                last_error = exc
                continue
            raise exc
    raise last_error  # all models exhausted

# ---------------------------------------------------------------------------
# 6. CHAT FUNCTION
# ---------------------------------------------------------------------------

def chat(message: str, history: list) -> str:
    if not isinstance(message, str) or not message.strip():
        return "Please type a question or tell me what mode you'd like — Interview, GD, or Cold Email!"

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for item in (history or [])[-12:]:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        if role not in {"user", "assistant"}:
            continue
        text = content_to_text(item.get("content", ""))
        if text.strip():
            messages.append({"role": role, "content": text})

    messages.append({"role": "user", "content": message.strip()})

    try:
        return call_groq(messages)
    except Exception as exc:
        error_type = type(exc).__name__
        return (
            f"Sorry, I couldn't complete that request ({error_type}). "
            "Check your GROQ_API_KEY, billing/quota, and internet connection — then try again."
        )

# ---------------------------------------------------------------------------
# 7. GRADIO UI — dark navy theme matching BolKe's aesthetic
# ---------------------------------------------------------------------------

CUSTOM_CSS = """
/* ── Page background ── */
body, .gradio-container {
    background-color: #0f172a !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── Chatbot area ── */
.chatbot {
    background-color: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
}

/* ── User bubbles ── */
.message.user {
    background-color: #4f46e5 !important;
    color: #ffffff !important;
    border-radius: 12px 12px 4px 12px !important;
}

/* ── Bot bubbles ── */
.message.bot {
    background-color: #1e293b !important;
    color: #e2e8f0 !important;
    border: 1px solid #334155 !important;
    border-radius: 12px 12px 12px 4px !important;
}

/* ── Input box ── */
.textbox textarea, .textbox input {
    background-color: #1e293b !important;
    color: #e2e8f0 !important;
    border: 1px solid #4f46e5 !important;
    border-radius: 8px !important;
}

/* ── Submit button ── */
button.primary {
    background-color: #4f46e5 !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
button.primary:hover {
    background-color: #4338ca !important;
}

/* ── Title & description ── */
h1 { color: #818cf8 !important; }
.description { color: #94a3b8 !important; }

/* ── Example buttons ── */
.example-set button {
    background-color: #1e293b !important;
    color: #94a3b8 !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
}
"""

demo = gr.ChatInterface(
    fn=chat,
    title=f"✨ {BOT_NAME}",
    description=(
        "Your career communication coach — three modes in one.\n"
        "🎤 **Interview** · craft your story, nail behavioral questions, mock Q&A\n"
        "🗣️ **GD** · arguments, opening lines, GD strategy & feedback\n"
        "📧 **Cold Email** · write outreach emails that actually get replies"
    ),
    examples=[
        "What can you help me with?",
        "Help me answer 'Tell me about yourself' for a data analyst role",
        "GD topic: Social media does more harm than good — give me points",
        "Write a cold email to a recruiter at a product company for an internship",
        "Ask me a behavioral interview question and give feedback on my answer",
    ],
)

# ---------------------------------------------------------------------------
# 8. LAUNCH
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    demo.launch(share=True, css=CUSTOM_CSS)
