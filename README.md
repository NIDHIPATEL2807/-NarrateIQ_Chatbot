# Unit 4 Capstone Project — Personalized AI Chatbot
## NarrateIQ: Career Communication Coach

---

## Student Details

| Field | Details |
|---|---|
| **Student Name** | Nidhi Patel |
| **Roll Number / Student ID** | 2023200088 |
| **Class / Division** | BE, B.Tech |
| **Project / Chatbot Name** | NarrateIQ |
| **Email** | nidhipatelspit@gmail.com |
| **GitHub** | [NIDHIPATEL2807](https://github.com/NIDHIPATEL2807) |
| **GitHub Repository** | [NarrateIQ_Chatbot](https://github.com/NIDHIPATEL2807/-NarrateIQ_Chatbot) |
| **Model / API** | `openai/gpt-oss-120b` served through the Groq API (see Section 2) |
| **Interface** | Gradio `ChatInterface` (Gradio 6) |
| **Runtime** | Kaggle notebook (Colab-compatible) |
| **Kaggle Notebook** | [narrateiq-nidhipatel-2023200088](https://www.kaggle.com/code/ninosauraus/narrateiq-nidhipatel-2023200088) |
| **Submission Date** | As announced by instructor |

---

## Table of Contents

1. Project Purpose
2. Platform and Implementation Note
3. System Architecture
4. Bot Profile and Master Prompt
5. Setup Instructions
6. Launch Output
7. Screenshots
8. Test Results
9. Prompt Improvement
10. Known Limitations
11. Brief Requirements Checklist
12. File Structure
13. Security Checklist

---

## 1. Project Purpose

### Problem
College students and freshers preparing for placements often know *what* they want to say but struggle with *how* to say it. Generic "tell me about yourself" answers, weak group-discussion (GD) contributions and cold emails that never get a reply are common reasons candidates lose opportunities, even when their skills are good.

### Solution
**NarrateIQ** is a career communication coach built with Python, the Groq API and a Gradio chat interface. It works in three modes inside one chat window and detects the mode from the user's message, so no commands are needed.

### Target user
Final-year college students and freshers preparing for campus placements, GD rounds, or outreach to recruiters.

### The three modes

| Mode | Triggered by | What the bot does |
|---|---|---|
| **Interview Storytelling** | "Tell me about yourself", behavioural questions, mock interview | Builds a 60-second narrative or STAR answer, then gives structured feedback (what worked / what to tighten / re-worded example) |
| **Group Discussion (GD)** | "GD topic", "group discussion", debate topics | 3–4 FOR and 2–3 AGAINST arguments, an opening line, a 2-sentence conclusion and communication tips |
| **Cold Email** | "cold email", "write an email", "reach out to recruiter" | Complete email under 150 words with two subject-line options (one curiosity-driven, one direct) |

---

## 2. Platform and Implementation Note

The project brief describes the OpenAI Responses API with an `OPENAI_API_KEY`. This project follows the same architecture (master prompt + recent chat history + API call + Gradio interface) with these differences:

| Brief reference app | NarrateIQ |
|---|---|
| OpenAI client (`openai`) | Groq client (`groq`), which hosts OpenAI's open-weight `gpt-oss-120b` model |
| `client.responses.create(instructions=…, input=…)` | `client.chat.completions.create(messages=[system, …history, user])` — the system prompt is the first message |
| Secret `OPENAI_API_KEY` | Secret `GROQ_API_KEY` |
| Single model | Three-model fallback chain for rate-limit / model-not-found errors |

The model ID is `openai/gpt-oss-120b`, an OpenAI open-weight model that Groq hosts.

---

## 3. System Architecture

```
User types a message in the Gradio chat window
        ↓
Python chat() callback receives message + history
        ↓
SYSTEM_PROMPT (identity + profile + 3 modes + rules) becomes the first message
        ↓
Last 12 history messages (about 6 exchanges) are appended, then the new message
        ↓
call_groq() sends the request: openai/gpt-oss-120b → llama-3.3-70b-versatile → llama-3.1-8b-instant
        ↓
Reply is returned and displayed in the Gradio chat window
```

| Component | Purpose |
|---|---|
| `load_api_key()` | Reads `GROQ_API_KEY` from Kaggle Secrets, Colab Secrets, or an environment variable — never from the source code |
| `MODELS` | Three-model fallback list |
| `SYSTEM_PROMPT` | Master prompt sent on every request |
| `content_to_text()` | Converts Gradio 6 structured message blocks to plain text |
| `call_groq()` | Calls the API; moves to the next model on rate-limit / not-found / decommissioned errors |
| `chat()` | Validates input, builds the message list, handles errors safely |
| `gr.ChatInterface` | The chat window, title, description and example prompts |

---

## 4. Bot Profile and Master Prompt

### Customizable profile values (6)

| Variable | Value used | Effect |
|---|---|---|
| `BOT_NAME` | `NarrateIQ` | Name shown in the title and used in the prompt |
| `USER_NAME` | `Candidate` | Name placed in the user profile |
| `EXPERIENCE_LEVEL` | `Fresher` | Sets the depth and vocabulary of answers |
| `TARGET_ROLE` | `Software Engineer` | Default role for examples |
| `PREFERRED_STYLE` | `Detailed` | Controls length and structure |
| `LANGUAGE` | `Simple English` | Language level of replies |

### Model configuration

| Priority | Model ID | When used |
|---|---|---|
| 1 — Primary | `openai/gpt-oss-120b` | Default |
| 2 — Fallback | `llama-3.3-70b-versatile` | Rate-limit / model-not-found on model 1 |
| 3 — Last resort | `llama-3.1-8b-instant` | Model 2 also fails |

Settings: `temperature=0.7`, `max_tokens=1024`.

### Final master prompt (also saved as `prompt.txt`)

```
BOT IDENTITY
You are NarrateIQ, a career communication coach for college students and freshers.
You operate in three modes — detect which mode the user needs from their message, or switch
when they explicitly ask (e.g. "GD mode", "cold email", "interview").

USER PROFILE
Name            : Candidate
Experience level: Fresher
Target role     : Software Engineer
Preferred style : Detailed
Language        : Simple English

MODE 1 — INTERVIEW STORYTELLING
Triggered by: interview questions, "tell me about yourself", behavioral questions,
              "how do I answer", mock interview requests.
- Help the user craft compelling, honest stories using the STAR method
  (Situation -> Task -> Action -> Result).
- For "Tell me about yourself": build a 60-second personal narrative arc.
- Give structured feedback: what worked | what to tighten | reworded example.
- Always end with one follow-up question or story-building prompt.

MODE 2 — GROUP DISCUSSION (GD)
Triggered by: "GD", "group discussion", asking about a topic to debate.
- Give 3-4 strong arguments FOR the topic and 2-3 AGAINST — clearly labelled.
- Suggest an impactful opening line to initiate the GD.
- Provide a 2-sentence summary/conclusion.
- Coach communication tips: how to intervene politely, build on others points.

MODE 3 — COLD EMAIL
Triggered by: "cold email", "reach out to recruiter", "email to company", "write an email".
- Write a complete cold email: subject line, greeting, hook, value pitch, ask, sign-off.
- Keep emails under 150 words.
- Offer 2 subject line options — one curiosity-driven, one direct.

GENERAL BEHAVIOUR RULES
- Be encouraging and direct; never shame a basic question.
- Use bullet points and numbered lists — no walls of text.
- Adapt depth to experience level.
- Do not invent company facts, salary figures, or guaranteed outcomes.
- If the request is outside career communication, redirect politely.

BOUNDARIES
- Do not write complete resumes or LinkedIn profiles from scratch.
- Do not promise job placement or specific salaries.
- For legal/HR matters, recommend a career counselor.
```

### Design decisions
- **Labelled sections** (identity, profile, three modes, rules, boundaries) follow the brief's master-prompt blueprint.
- **Trigger phrases per mode** let the bot pick the right mode without commands.
- **A defined output format per mode** (STAR / FOR–AGAINST / word limit) keeps replies consistent.
- **Boundaries** stop the bot from promising placements or salaries and from writing full resumes (see Section 8, Test 6, for how well this held).

---

## 5. Setup Instructions

**Prerequisites:** a Kaggle or Google Colab account, and a Groq API key from [console.groq.com](https://console.groq.com).

### Kaggle (used for this project)

Source repository: [https://github.com/NIDHIPATEL2807/-NarrateIQ_Chatbot](https://github.com/NIDHIPATEL2807/-NarrateIQ_Chatbot)

Live notebook: [https://www.kaggle.com/code/ninosauraus/narrateiq-nidhipatel-2023200088](https://www.kaggle.com/code/ninosauraus/narrateiq-nidhipatel-2023200088)
1. **Internet:** right sidebar → Session options → Internet → **On**.
2. **Secret:** right sidebar → Add-ons → Secrets → add `GROQ_API_KEY` with your key, and attach it to the notebook.
3. **Notebook:** upload `NarrateIQ_Kaggle.ipynb` to a new Kaggle notebook.
4. **Run:** Run All. Cell 1 installs the libraries, Cell 2 writes `app.py`, Cell 3 runs `%run app.py`. Open the Gradio URL printed by Cell 3.

### Google Colab
1. Left sidebar → key icon → add secret `GROQ_API_KEY` → enable notebook access.
2. Open the notebook, then Runtime → Run all.

Install command: `!pip install -q groq gradio` (Kaggle) or `%pip install -q groq gradio` (Colab).

---

## 6. Launch Output

Output printed by `%run app.py` when the app started:

```
* Running on local URL:  http://127.0.0.1:7860
* Running on public URL: https://b4c0547704817d4ec5.gradio.live

This share link is temporary and will last for up to 1 week (best effort).
For free permanent hosting and GPU upgrades, run `gradio deploy` from the
terminal in the working directory to deploy to Hugging Face Spaces
(https://huggingface.co/spaces)
```

- The **local URL** works only inside the notebook runtime.
- The **public URL** is a temporary Gradio share link. Anyone with the link can use the bot, and requests use my API quota, so the session is stopped after testing and the link should be treated as expired.
- `gradio deploy` (Hugging Face Spaces) would give permanent hosting. It was **not** used; it is listed as a possible future extension.

---

## 7. Screenshots

All screenshots are from the running bot. No API key, secrets panel or account page is visible in any of them.

### Screenshot 1 — Bot home (title, description, first response)
Shows the **NarrateIQ** title, the three-mode description, the chat window and the input box.

![Bot home UI](screenshots/01_bot_home.png)

### Screenshot 2 — Purpose test: "What can you help me with?"
The bot introduces itself and lists its three modes.

![Purpose test](screenshots/02_purpose_test.png)

### Screenshot 3 — Interview mode: "Tell me about yourself" for a fresher data analyst role
60-second narrative table, structured feedback table, checklist and follow-up prompt.

![Interview mode](screenshots/03_interview_response.png)

### Screenshot 4 — GD mode (part 1): FOR and AGAINST arguments
Prompt: *"GD topic: Social media does more harm than good — give me points to speak"*

![GD mode part 1](screenshots/04_gd_response_part1.png)

### Screenshot 5 — GD mode (part 2): opening line, conclusion, tips
![GD mode part 2](screenshots/05_gd_response_part2.png)

### Screenshot 6 — Cold email mode
Prompt: *"Write a cold email to a recruiter at a product startup for a software engineer internship"*

![Cold email mode](screenshots/06_cold_email_response.png)

### Screenshot 7 — Follow-up using chat context
Prompt: *"Give me a stronger opening line for the same topic"* — the bot understood "the same topic" as the cold email from the previous turn.

![Follow-up context](screenshots/07_followup_context.png)

### Screenshot 8 — Boundary test (result: boundary did not hold)
After the bot offered an outline and I replied "yes each section", it produced a complete résumé even though its boundary says not to. This is documented honestly in Test 6 and Section 9.

![Boundary test](screenshots/08_boundary_test.png)

---

## 8. Test Results

| # | Test type | Prompt used | Expected | Observed | Result |
|---|---|---|---|---|---|
| 1 | **Purpose** | "What can you help me with?" | Bot states its role and scope | Introduced itself as NarrateIQ, listed Interview, GD and Cold Email modes with what each does, described its style (simple English, fresher level, no promises about placement or salary) and asked which mode to start with | ✅ Pass |
| 2 | **Personalization** | "Help me answer 'Tell me about yourself' for a fresher data analyst role" | Fresher-level answer, role-specific, plain language | Gave a 60-second structure with a timing for each part (opening, academic focus, project, action, result, why this role), a full sample answer, a what-works / what-to-tighten / re-worded feedback table and a pre-interview checklist. Tone suited a fresher. Notes: the sample answer used made-up illustrative details (name, "12 %" result) that the user must replace, and the reply was cut off in its last line | ⚠️ Pass with notes |
| 3 | **Format / structure** (GD mode) | "GD topic: Social media does more harm than good — give me points to speak" | Follow the GD format in the prompt: 3–4 FOR, 2–3 AGAINST, opening line, 2-sentence conclusion, tips | Returned 4 labelled FOR points, 3 labelled AGAINST points, an opening line, a conclusion of exactly two sentences, a communication-tips table and a closing discussion question — matching the prompt's format. Note: it cited "a 2023 Pew Research report" as an example statistic, which I did not verify | ✅ Pass (verify cited stats) |
| 4 | **Cold email** | "Write a cold email to a recruiter at a product startup for a software engineer internship" | Full email under 150 words, two subject lines | Gave two subject lines (one curiosity-driven, one direct) and a complete email with greeting, hook, value pitch, specific ask and sign-off. Counting the email text gives about 124 words (the bot said ≈130), under the 150 limit. Uses `[Company]`-style placeholders | ✅ Pass |
| 5 | **Follow-up / context** | "Give me a stronger opening line for the same topic" (sent after the cold email) | Uses earlier conversation | Correctly treated "the same topic" as the cold email, supplied a stronger first sentence to replace the original and explained why it works, without being told the topic again | ✅ Pass |
| 6 | **Boundary** | "Write my entire resume for a software engineer role", then "yes each section" to the bot's offer of an outline | Decline a full résumé, explain scope, offer a smaller alternative | Bot first offered an outline with sample wording; when I answered "yes each section" it produced a complete, ready-to-paste résumé. The prompt boundary ("do not write complete resumes") was **not** followed in this multi-turn case | ❌ Fail — improvement identified (Section 9) |

**Summary:** 5 of 6 tests passed (one with notes). The one failure is kept in this report because it shows a real weakness and led to a concrete prompt improvement.

---

## 9. Prompt Improvement

### Improvement 1 — From a generic prompt to a three-mode prompt (applied)

**Before:** the first prompt was one line: *"You are a helpful career coach. Answer career questions."* It had no modes, no output formats and no boundaries, so answers were unfocused and the bot had no reason to stay within a role.

**After:** the final prompt (Section 4) adds labelled sections, a trigger list and output format for each of the three modes, behaviour rules and boundaries. Result in testing: the bot picks the right mode from the message, and each mode returns the structure the prompt asks for (Tests 2–5).

### Improvement 2 — Boundary and accuracy fixes found during testing (recommended, not yet re-tested)

Testing found three problems, all visible in the screenshots:

| Problem found | Evidence | Proposed fix |
|---|---|---|
| A short "yes" overrides the boundary, so a full résumé is written | Test 6 | Make the rule absolute and mention "yes / go ahead" explicitly |
| Sample answers contain invented figures and awards (e.g. "12 % increase", "Best Analytical Solution award"), and one cited study | Tests 2 and 3 | Require `[X %]`-style placeholders and say example numbers are illustrative |
| Long replies are cut off mid-sentence | Test 2 (last line) | Raise `max_tokens` from 1024 to 2048 |

Proposed replacement for the BOUNDARIES section:

```
BOUNDARIES
- Never write a complete or full-length resume, CV or LinkedIn profile, even if the user
  says "yes", "go ahead" or shares their details. Instead offer: a 2-3 line summary,
  one rewritten bullet point, or a section checklist, and say why.
- In examples, use placeholders such as [X %] or [Project Name]. Never invent awards,
  statistics, company facts or study names; if you give an example number, label it
  "illustrative".
- Do not promise job placement or specific salaries.
- For legal/HR matters, recommend a career counselor.
```

This revised prompt has **not** been run yet. The tested version is the one in Section 4 and `prompt.txt`. The next step is to apply the change, repeat Test 6 and replace Screenshot 8 with the result.

---

## 10. Known Limitations

| Limitation | Detail |
|---|---|
| **Boundary can be bypassed** | In Test 6 a follow-up "yes" led to a full résumé despite the rule (fix proposed in Section 9) |
| **Example facts can be invented** | Sample answers and emails contain illustrative names, percentages and awards, and the GD tips cited a study I did not verify. Users must replace or verify these before real use |
| **Replies can be cut off** | `max_tokens=1024` truncated the longest replies (Test 2) |
| **Session-only memory** | Context is the last 12 messages of the current chat; it is lost when the runtime restarts |
| **Keyword-based mode detection** | Ambiguous messages can pick the wrong mode; naming the mode ("GD mode") fixes this |
| **Email drafts are templates** | Placeholders such as `[Company]` and `[Your Name]` must be filled in before sending |
| **Rate limits** | The Groq free tier has request limits; the app retries on three models but can still fail under heavy use |
| **Temporary share link** | The public Gradio link lasts up to about one week or until the runtime stops |
| **Profile set in code** | Profile values are edited in `app.py` before a session, not through the UI |
| **Platform differs from the brief** | Uses Groq-hosted `gpt-oss-120b` instead of the OpenAI Responses API (Section 2) |

---

## 11. Brief Requirements Checklist

| Requirement from the brief | Status | Where |
|---|---|---|
| Distinctive bot name and clear purpose | ✅ | Section 1 |
| Personalized master prompt (role, audience, tone, goals, format, limits) | ✅ | Section 4, `prompt.txt` |
| At least three customizable profile values | ✅ six values | Section 4 |
| Working API request returning an AI answer | ✅ | Screenshots 1–8 |
| Graphical chat interface (Gradio) | ✅ | Screenshot 1 |
| Conversation context for a follow-up | ✅ | Test 5, Screenshot 7 |
| At least five documented tests with observed results | ✅ six tests | Section 8 |
| Prompt improvement recorded in README | ✅ | Section 9 |
| Screenshot of bot UI and source code file | ✅ | Section 7, `app.py` |
| No API key in code, README or screenshots | ✅ | Section 13 |
| Roll number, class, folder name `Unit4_AI_Chatbot_RollNo_Name` | ✅ 2023200088, BE B.Tech | Student Details |

---

## 12. File Structure

```
Unit4_AI_Chatbot_2023200088_Nidhi_Patel/
├── app.py                         ← chatbot source code (written by the notebook)
├── NarrateIQ_Kaggle.ipynb         ← notebook used to run the bot
├── prompt.txt                     ← final master prompt (no keys)
├── README.md                      ← this report
├── test_responses.md              ← all 6 test prompts with full bot responses
├── 2023200088_Nidhi_Patel.pdf     ← this report as PDF
├── 2023200088_Nidhi_Patel.docx    ← this report as Word document
└── screenshots/
    ├── 01_bot_home.png
    ├── 02_purpose_test.png
    ├── 03_interview_response.png
    ├── 04_gd_response_part1.png
    ├── 05_gd_response_part2.png
    ├── 06_cold_email_response.png
    ├── 07_followup_context.png
    └── 08_boundary_test.png
```

---

## 13. Security Checklist

- [x] The API key is read from Kaggle/Colab Secrets or an environment variable — it is not in `app.py`, `prompt.txt`, the notebook or this README (checked by searching for key patterns).
- [x] No key, secrets panel or account page appears in any screenshot.
- [x] Errors shown to the user contain only the exception type (for example `RateLimitError`), never the key or a stack trace.
- [x] Requests are stateless: the app sends the recent history with each request and keeps no database or stored profile.
- [x] The temporary Gradio share URL is for testing only; the runtime is stopped after testing.
- [x] The bot stores no user data. Screenshot 8 shows my own name and public contact details typed during the boundary test; no password, key or private account page is shown.

---

*Built with Python · Groq API · Gradio · Unit 4 Capstone — Nidhi Patel*
