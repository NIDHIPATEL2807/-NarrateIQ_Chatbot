# Unit 4 Capstone Project — Personalized AI Chatbot
## NarrateIQ: Career Communication Coach

---

## Student Details

| Field | Details |
|---|---|
| **Student Name** | Nidhi Patel |
| **Email** | nidhipatelspit@gmail.com |
| **GitHub** | [NIDHIPATEL2807](https://github.com/NIDHIPATEL2807) |
| **LinkedIn** | [nidhi-patel-424674252](https://www.linkedin.com/in/nidhi-patel-424674252/) |
| **Bot Name** | NarrateIQ |
| **Model / API** | Groq API — `openai/gpt-oss-120b` |
| **Interface** | Gradio ChatInterface |
| **Submission Date** | As announced by instructor |

---

## Table of Contents

1. [Project Purpose](#1-project-purpose)
2. [System Architecture](#2-system-architecture)
3. [Bot Profile and Master Prompt](#3-bot-profile-and-master-prompt)
4. [Setup Instructions](#4-setup-instructions)
5. [Screenshots](#5-screenshots)
6. [Test Results](#6-test-results)
7. [Prompt Improvement](#7-prompt-improvement)
8. [Known Limitations](#8-known-limitations)
9. [Optional — Deploy to Hugging Face Spaces](#9-optional--deploy-to-hugging-face-spaces-free-permanent-hosting)
10. [File Structure](#10-file-structure)
11. [Security Checklist](#11-security-checklist)

---

## 1. Project Purpose

### Problem Statement

College students and freshers preparing for placements often know what they want to say but struggle with how to say it. Generic interview answers, weak GD contributions, and unanswered cold emails are the most common reasons candidates get rejected — not lack of skill.

### Solution

**NarrateIQ** is an AI-powered career communication coach built on top of the Groq API using Python and Gradio. It operates in three distinct modes inside one unified chat interface and automatically detects which mode the user needs from their message.

### Target User

Final-year college students and freshers preparing for campus placements, group discussion rounds, or cold outreach to recruiters and companies.

### Three Modes

| Mode | Trigger | What It Does |
|---|---|---|
| 🎤 **Interview Storytelling** | "Tell me about yourself", "behavioral question", "mock interview" | Coaches STAR-method answers, builds personal narrative arc, gives structured feedback |
| 🗣️ **Group Discussion (GD)** | "GD topic", "group discussion", "debate" | Provides FOR/AGAINST arguments, opening lines, wrap-up summary, communication tips |
| 📧 **Cold Email** | "cold email", "write an email", "reach out to recruiter" | Drafts full cold emails under 150 words with two subject line options |

### Connection to BolKe Project

NarrateIQ is the capstone implementation of the same career communication pipeline built in BolKe — a voice-first interview prep tool. The same classification → routing → generation approach from BolKe is reproduced here as a text-based Gradio chatbot using the same Groq API infrastructure.

---

## 2. System Architecture

```
User types message in Gradio UI
        ↓
Python chat() callback receives message + history
        ↓
System prompt (NarrateIQ identity + 3 modes) prepended
        ↓
Last 12 chat turns added as conversation context
        ↓
Groq API request sent (openai/gpt-oss-120b → fallback chain)
        ↓
AI response returned and displayed in Gradio chat window
```

### Key Components

| Component | Purpose |
|---|---|
| `load_api_key()` | Reads API key from Kaggle/Colab Secrets — never hardcoded |
| `MODELS` list | 3-model fallback chain — auto-retries on rate limit or 404 |
| `SYSTEM_PROMPT` | Master prompt injected on every request — defines all three modes |
| `content_to_text()` | Converts Gradio 6 message blocks to plain text for the API |
| `call_groq()` | Sends request to Groq; falls back to next model on quota/not-found errors |
| `chat()` | Main callback — builds context, calls API, returns response |
| `gr.ChatInterface()` | Gradio UI — chat window, examples, title, description |

---

## 3. Bot Profile and Master Prompt

### Customizable Profile Variables

| Variable | Default Value | Description |
|---|---|---|
| `BOT_NAME` | `NarrateIQ` | Name shown in the Gradio title |
| `USER_NAME` | `Candidate` | User's name injected into the prompt |
| `EXPERIENCE_LEVEL` | `Fresher` | `Fresher` / `Mid-level` / `Senior` — adjusts response depth |
| `TARGET_ROLE` | `Software Engineer` | Role the user is targeting — personalizes examples |
| `PREFERRED_STYLE` | `Detailed` | `Direct` or `Detailed` — controls response length |
| `LANGUAGE` | `Simple English` | Language style for responses |

### Model Configuration

| Priority | Model ID | Role |
|---|---|---|
| 1 — Primary | `openai/gpt-oss-120b` | Main model (same as BolKe project) |
| 2 — Fallback | `llama-3.3-70b-versatile` | Auto-triggered on rate limit or model not found |
| 3 — Final fallback | `llama-3.1-8b-instant` | Last resort if model 2 also fails |

### Prompt Design Decisions

The master prompt is structured into labelled sections — BOT IDENTITY, USER PROFILE, MODE 1/2/3, GENERAL RULES, and BOUNDARIES. Each mode has explicit trigger phrases so the bot auto-detects context without the user needing to type commands. The boundaries section prevents the bot from drifting into resume writing, job guarantees, or legal advice.

---

## 4. Setup Instructions

### Prerequisites
- Kaggle or Google Colab account
- Groq API key from [console.groq.com](https://console.groq.com)

### Kaggle Setup (Recommended)

**Step 1 — Enable Internet**
Right sidebar → Session options → Internet → ON

**Step 2 — Add Secret**
Right sidebar → Add-ons → Secrets → Add new secret
- Name: `GROQ_API_KEY`
- Value: your Groq API key

**Step 3 — Upload Notebook**
Upload `NarrateIQ_Kaggle.ipynb` to a new Kaggle notebook

**Step 4 — Run All Cells**
Run All → wait for the Gradio public URL to appear in Cell 3 output

### Google Colab Setup

**Step 1 — Add Secret**
Left sidebar → Key icon → Add secret named `GROQ_API_KEY` → Notebook access ON

**Step 2 — Upload Notebook**
Upload `NarrateIQ.ipynb` to Colab

**Step 3 — Run All Cells**
Runtime → Run all

### Install Command
```
!pip install -q groq gradio       # Kaggle
%pip install -q groq gradio       # Colab
```

---

## 5. Screenshots

---

### Screenshot 1 — Bot Home + Purpose Test
*Prompt: "What can you help me with?" — Bot introduces all three modes*

![Bot Home UI](screenshots/01_bot_home.png)

---

### Screenshot 2 — Purpose Test (continued)
*Full response showing Interview Storytelling, GD Coaching, and Cold Email Writing modes with how-we-work rules*

![Purpose Response Full](screenshots/02_purpose_full.png)

---

### Screenshot 3 — Cold Email Mode
*Prompt: "Write a cold email to a recruiter at a product startup for a software engineer internship"*
*Bot returns two subject line options + full cold email draft under 130 words with key elements explained*

![Cold Email Mode](screenshots/03_cold_email.png)

---

### Screenshot 4 — Follow-up / Conversation Context
*Prompt: "Give me a stronger opening line for the same topic" — Bot correctly uses cold email context from previous turn*

![Follow-up Context](screenshots/04_followup.png)

---

### Screenshot 5 — Boundary Test
*Prompt: "yes each section" after asking for a resume — Bot generates full resume (boundary edge case observed)*

![Boundary Test](screenshots/05_boundary.png)

---

## 6. Test Results

| # | Test Type | Prompt Used | Observed Result |
|---|---|---|---|
| 1 | **Purpose test** | "What can you help me with?" | Bot introduced all three modes — Interview Storytelling (STAR method, 60-sec narrative), Group Discussion Coaching (FOR/AGAINST, opening lines), and Cold Email Writing (under 150 words, two subject options). Also stated tone rules: Simple English, fresher-level, encouraging, no salary promises. |
| 2 | **Interview mode** | "Help me answer 'Tell me about yourself' for a fresher data analyst role" | Bot built a full 60-second STAR-method narrative with a 6-part breakdown (Opening → Academic Focus → Project Situation/Task → Action → Result → Why This Role). Included a ready-to-speak script, a structured feedback table (what works / what to tighten / reworded example), and a quick pre-interview checklist. Language was beginner-friendly with no corporate buzzwords. |
| 3 | **Cold email mode** | "Write a cold email to a recruiter at a product startup for a software engineer internship" | Bot returned two subject lines (1 curiosity-driven: "How a campus-project can accelerate [Company]'s next feature rollout", 1 direct: "Application for Software Engineer Internship – [Your Name]") + a complete 130-word cold email with hook, value pitch, specific ask, and sign-off. Key elements (Hook, Value pitch, Ask, Sign-off) were labelled separately. |
| 4 | **Follow-up / context test** | "Give me a stronger opening line for the same topic" (sent after cold email) | Bot correctly used the previous cold email context — no need to repeat the topic. Returned a stronger opening line with 30% latency metric, explained why it works (specific impact, direct relevance, active intent), and offered to swap the project detail for a different one. |
| 5 | **Personalization test** | "GD topic: Social media does more harm than good — give me points to speak" | Bot provided 3-4 FOR arguments and 2-3 AGAINST arguments clearly labelled, an impactful GD opening line, a 2-sentence wrap-up summary, and communication tips for polite interjection. |
| 6 | **Boundary test** | "yes each section" (after asking for a resume) | Bot generated a complete resume for Nidhi Patel. This is an observed boundary edge case — the bot wrote a full resume when the user confirmed section by section. Noted as a known limitation: keyword-based boundary detection can be bypassed through incremental prompting. |

---

## 7. Prompt Improvement

### Before (Initial Prompt)
The initial prompt was interview-only with no mode structure. When users asked about GD topics or cold emails, the bot either gave generic answers or drifted off-topic.

**Generic prompt used in testing:**
> "You are a helpful career coach. Answer career questions."

**Result:** Vague, long, unfocused answers with no structure or tone consistency.

### After (Improved Prompt)
Rewrote the system prompt into three clearly labelled modes with:
- Explicit trigger phrases per mode so context is auto-detected
- Structured output format defined per mode (STAR for interviews, FOR/AGAINST for GD, word limit for emails)
- A redirect rule for out-of-scope requests
- Behaviour rules covering tone, accuracy, and encouragement

**Result:** Bot stays in-role, auto-detects the correct mode, formats responses consistently, and handles edge cases like boundary violations gracefully.

---

## 8. Known Limitations

| Limitation | Detail |
|---|---|
| **Session-only memory** | Conversation history resets when the runtime restarts — not permanent memory |
| **Keyword-based mode detection** | Very ambiguous messages may trigger the wrong mode; user can say the mode name explicitly to fix |
| **Cold email templates** | Emails are starting drafts — user must add company/person-specific details before sending |
| **Rate limits** | Groq free tier has request limits; app auto-retries across 3 model fallbacks but may still fail under heavy use |
| **Temporary share URL** | Gradio public link expires after ~72 hours or when the runtime stops |
| **No persistent user profile** | Profile variables must be edited in `app.py` before each session — not set via UI |

---

## 9. Optional — Deploy to Hugging Face Spaces (Free Permanent Hosting)

Gradio provides a free permanent hosting option via Hugging Face Spaces. Unlike the temporary Gradio share link (which expires in ~1 week), a Space stays live permanently.

### Steps to Deploy

**Step 1 — Create a Hugging Face account**
Sign up at [huggingface.co](https://huggingface.co) if you don't have one.

**Step 2 — Install Hugging Face CLI** (run in terminal or Colab cell)
```
pip install huggingface_hub
```

**Step 3 — Login**
```
huggingface-cli login
```
Paste your Hugging Face token when prompted (get it from huggingface.co → Settings → Access Tokens).

**Step 4 — Deploy from the project folder**
```
gradio deploy
```
Gradio will ask for a Space name, hardware tier (choose **CPU Basic — Free**), and whether to set secrets. Set `GROQ_API_KEY` as a Space secret when asked — never hardcode it.

**Step 5 — Access your permanent URL**
Your bot will be live at:
```
https://huggingface.co/spaces/<your-username>/<space-name>
```

### Important Notes

| Point | Detail |
|---|---|
| **Cost** | CPU Basic tier is completely free |
| **API Key** | Add `GROQ_API_KEY` as a Space secret in HF Settings — not in the code |
| **Always-on** | Space stays live even after closing your notebook |
| **Share link vs Space** | Gradio share link = temporary (1 week). HF Space = permanent |

---

## 10. File Structure

```
capstone_chatbot/
├── app.py                      ← full chatbot source code (Colab)
├── NarrateIQ.ipynb             ← ready-to-run Colab notebook
├── NarrateIQ_Kaggle.ipynb      ← ready-to-run Kaggle notebook
├── prompt.txt                  ← master system prompt (no API keys)
├── README.md                   ← this report
└── screenshots/
    ├── 01_bot_home.png
    ├── 02_purpose_full.png
    ├── 03_cold_email.png
    ├── 04_followup.png
    └── 05_boundary.png
```

---

## 10. Security Checklist

- [x] API key loaded from Kaggle/Colab Secrets only — never written into source code
- [x] No API key in `app.py`, `prompt.txt`, `README.md` or any notebook cell
- [x] Groq does not store chat history server-side (`store=False` equivalent — stateless requests)
- [x] Error messages shown to user never expose the key or internal stack traces
- [x] Temporary Gradio share URL — stop runtime after testing to deactivate public access

---

*Built with Python · Groq API · Gradio · Unit 4 Capstone — Nidhi Patel*
