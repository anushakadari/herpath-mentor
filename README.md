# HerPath Mentor 💜

HerPath Mentor is a Streamlit web app that acts as a calm, non‑judgmental companion for girls and young women. It brings **career guidance**, **women‑focused opportunities**, and **emotional support** into one simple place.

> Demo (after deploy):  
> Live app: https://herpath-mentor.streamlit.app  
> Code: https://github.com/anushakadari/herpath-mentor

---

## 🌸 Inspiration

Growing up around friends and cousins with big dreams but limited guidance, I saw how confusing it can be for girls to balance education, careers, money, and emotions at the same time. Many depended on random YouTube videos or relatives' advice, which often did not match their real goals or financial situation. This is even harder for girls from non‑metro areas, where proper counselling is rare.

**HerPath Mentor** grew from a simple idea: one calm, non‑judgmental place where a girl can ask *“What should I do next?”* and get clear roadmaps, women‑focused opportunities, and emotional support in one app.

---

## 🚀 What the project does

HerPath Mentor is a three‑in‑one companion:

- **Career Guide**  
  Ask any study or career question (tech or non‑tech) and get a personalised roadmap written in clear paragraphs. The app also shows a simple **visual roadmap** where each stage of the journey appears as a separate block, so the path looks like a route map rather than a dry list.

- **Opportunities Explorer**  
  Discover curated scholarships, schemes, and programs created specifically for women, separated into:
  - 💻 **Tech Path** (e.g. Amazon WoW, Flipkart Runway, HSBC Power2Her, women‑in‑tech communities)
  - 🌸 **Non‑Tech / Govt Path** (government scholarships for girls, single‑girl‑child schemes, women entrepreneurship support, arts/humanities‑friendly opportunities)  
  The underlying data is stored with simple category flags like `"tech"` or `"non-tech"` so it is easy to extend.

- **Emotional Support (SoulFriend)**  
  A gentle chat space where users can talk about stress, confusion, relationship issues, or self‑doubt. The system is designed to be empathetic and non‑judgmental, and it adds a clear safety note when messages look related to self‑harm, reminding the user to reach out to real‑world helplines or trusted adults.

- **Profile & Resume**  
  A dedicated section where a user fills her profile once (education, projects, experience, skills, goals, financial context, etc.), uploads a profile photo, and generates a clean **PDF resume**. There is also a Markdown‑style preview with headings like:

  - `# Name`  
  - `## Education`  
  - `## Experience`  
  - `## Projects`  
  - `## Technical Skills`  
  - `## Certifications & Achievements`  
  - `## Additional`  

  The PDF is built programmatically using ReportLab.

---

## 🧱 How it’s built

### Frontend / UX

- Single‑page **Streamlit** layout with a top navigation bar:
  - **Home**
  - **Profile**
  - **Help**
- Home has three tabs:
  - 🧭 **Career Guidance**
  - 🎯 **Opportunities**
  - 💜 **Emotional Support**
- Uses `st.session_state` to keep:
  - Login state
  - Profile data
  - Profile photo
  - Chat histories
  - The last career question (for roadmap blocks)

This makes the app feel like a small product, not a stateless script.

### Authentication & State

- Minimal **Sign up → Login** flow:
  - First‑time users see only “Sign up”.
  - After sign‑up, they see only “Login”.
- On sign‑up, the app stores:
  - `user_email`, `user_name`, `user_gender`
  - `saved_password` (demo only)
  - an empty `profile`
- On login, the app restores profile and photo from `session_state`. Logging out clears chats but keeps profile and credentials so data persists across sessions.

### Career Guidance (LLM + Visual Roadmap)

- A dedicated **system prompt** ensures:
  - Each question is treated as a fresh conversation.
  - Answers are given as paragraph‑style roadmaps (not repetitive bullet lists).
- Before calling the LLM, the app scans the question for simple interest keywords:
  - Arts / creative: arts, crafts, dance, music, fashion, drama, etc.
  - Tech: engineering, ML, AI, data science, coding, etc.
  - Medical: doctor, MBBS, nursing, pharmacy, etc.
  - Law: law, lawyer, CLAT, LLB, etc.
  - Government jobs: UPSC, Group 1/2, PSC, banking, etc.
- These hints are appended to the prompt so the model focuses on what the user actually wants (e.g., art and crafts vs. software engineering).
- A small **roadmap engine**:
  - Produces structured JSON with `next_stages` and example colleges or training paths.
  - Feeds that structure into the LLM as context.
  - Powers a **Visual Roadmap**: Stage 1, Stage 2, Stage 3 cards rendered using custom CSS.

### Women‑only Opportunities (Tech vs Non‑Tech / Govt)

- Knowledge base file: `women_programs_kb.json`
  - Fields: `name`, `who`, `summary`, `focus`, `activities`, `good_for`, `link`, `category`.
- Helper module: `kb_retriever_women.py`
  - `load_women_programs_kb()` – loads JSON.
  - `filter_women_programs(kb, interests, education_level, category)` – scores and filters programs.
- If no high‑score match is found, the app still shows all items for that category, so the tabs never look empty.
- UI shows:
  - 💻 **Tech Path** tab for tech‑focused programs.
  - 🌸 **Non‑Tech / Govt Path** tab for scholarships, government schemes, and non‑tech options.

### Emotional Support (SoulFriend)

- Separate tab with its own **SoulFriend** system prompt:
  - Focused on empathy, validation, and gentle guidance.
  - Explicitly not a medical or crisis service.
- Keeps its own chat history for continuity.
- Simple safety layer:
  - Scans messages for strong self‑harm phrases.
  - If detected, appends an emergency note advising the user to contact local helplines or trusted people.

### Profile & Resume (with photo and PDF)

- Profile collects:
  - Basic: name, age, education level, interests, location, financial situation, goals.
  - Resume: college, degree, branch, CGPA, experience summary, projects, skills, certifications, extra activities.
- Users can upload a **profile photo**:
  - Displayed on the Profile page.
  - Placed neatly in the top‑right of the PDF header.
- Resume:
  - Markdown‑style preview in the app.
  - PDF generation with **ReportLab**:
    - A4 page layout.
    - Section headings in bold.
    - Wrapped text and page breaks for long content.
- A **Download Resume (PDF)** button lets the user export the latest version any time.

### Help Page

- A small **app help bot** that:
  - Explains only real features of this app (no imaginary mobile/community features).
  - Guides users on where to find women‑only schemes, how to edit profile, and how to open the emotional support chat.

---

## 🧪 Running locally

1. Clone the repo:

   ```bash
   git clone https://github.com/<your-username>/herpath-mentor.git
   cd herpath-mentor
