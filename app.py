import base64
from io import BytesIO

import streamlit as st

from ai_client import call_ai_model
from prompts import (
    build_guidance_system_prompt,
    build_guidance_user_prompt,
    build_support_system_prompt,
    build_support_user_prompt,
)
from kb_retriever_women import (
    load_women_programs_kb,
    filter_women_programs,
    format_women_programs_for_display,
)
from roadmap_engine import generate_dynamic_roadmap, get_matching_colleges


def init_session():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_email" not in st.session_state:
        st.session_state.user_email = ""
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""
    if "user_gender" not in st.session_state:
        st.session_state.user_gender = ""
    if "has_signed_up" not in st.session_state:
        st.session_state.has_signed_up = False
    if "saved_password" not in st.session_state:
        st.session_state.saved_password = ""

    # Profile starts empty, not with fake 18 / 12th defaults
    if "profile" not in st.session_state:
        st.session_state.profile = {
            "name": "",
            "age": 0,
            "education_level": "",
            "interests": "",
            "location": "",
            "financial_constraint": "",
            "goals": "",
            "college": "",
            "degree": "",
            "branch": "",
            "cgpa": "",
            "experience_summary": "",
            "projects_summary": "",
            "skills_summary": "",
            "certifications_summary": "",
            "extra_summary": "",
        }

    if "profile_photo" not in st.session_state:
        st.session_state.profile_photo = None

    if "guidance_history" not in st.session_state:
        st.session_state.guidance_history = []
    if "support_history" not in st.session_state:
        st.session_state.support_history = []
    if "mini_bot_history" not in st.session_state:
        st.session_state.mini_bot_history = []

    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False

    if "support_input_value" not in st.session_state:
        st.session_state.support_input_value = ""
    if "guidance_input_value" not in st.session_state:
        st.session_state.guidance_input_value = ""
    if "help_input_value" not in st.session_state:
        st.session_state.help_input_value = ""


def set_background(image_file: str):
    try:
        with open(image_file, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        bg = f"""
        <style>
        .stApp {{
            background-image: linear-gradient(
                    rgba(240, 235, 252, 0.90),
                    rgba(235, 230, 250, 0.95)
                ),
                url("data:image/png;base64,{data}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: #1e1535;
            font-size: 1rem;
        }}
        .her-card {{
            background-color: rgba(255, 255, 255, 0.98);
            padding: 1.4rem 1.6rem;
            border-radius: 14px;
            box-shadow: 0 3px 12px rgba(0,0,0,0.15);
            margin-bottom: 1rem;
            color: #1e1535;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #24104f;
            font-weight: 700;
        }}
        .stMarkdown p {{
            font-size: 1rem;
        }}
        .stButton>button {{
            border-radius: 999px;
            padding: 0.35rem 0.9rem;
            border: 1px solid #b037a0;
            background-color: #ffffff;
            color: #24104f;
            font-size: 0.9rem;
        }}
        .stButton>button:hover {{
            background-color: #f4e6ff;
            border-color: #8b2b7e;
        }}
        .stTabs [data-baseweb="tab-list"] button {{
            background-color: rgba(255, 255, 255, 0.6);
            color: #24104f;
            font-size: 0.95rem;
        }}
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
            background-color: #f4e6ff;
            color: #24104f;
            font-weight: 600;
        }}
        .roadmap-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 1rem;
            margin-top: 0.8rem;
        }}
        .roadmap-card {{
            background: #f8f2ff;
            border-radius: 12px;
            padding: 0.9rem 1rem;
            border: 1px solid #e1c9ff;
        }}
        .roadmap-badge {{
            display: inline-block;
            font-size: 0.75rem;
            padding: 0.1rem 0.5rem;
            border-radius: 999px;
            background-color: #fff;
            color: #7a2c8b;
            border: 1px solid #d8b3ff;
            margin-bottom: 0.4rem;
        }}
        .roadmap-title {{
            font-weight: 600;
            margin-bottom: 0.2rem;
            color: #2a174f;
        }}
        .roadmap-desc {{
            font-size: 0.9rem;
            margin-bottom: 0.3rem;
        }}
        </style>
        """
        st.markdown(bg, unsafe_allow_html=True)
    except FileNotFoundError:
        pass


def show_login():
    st.title("HerPath Mentor – Welcome")

    if not st.session_state.has_signed_up:
        st.subheader("Sign up")
        st.write(
            "Create your account one time. Later, you can login every time with the same email and password."
        )

        email = st.text_input("Email", key="signup_email")
        name = st.text_input("Name", key="signup_name")
        gender = st.selectbox("Gender", ["Select", "Female", "Other"], key="signup_gender")
        password = st.text_input("Password (demo only, not secure)", type="password", key="signup_password")

        if st.button("Sign up"):
            if not email or not name or gender == "Select" or not password:
                st.error("Please fill all fields.")
            elif gender != "Female":
                st.error(
                    "HerPath Mentor is designed specifically for girls and young women for this demo."
                )
            else:
                st.session_state.user_email = email
                st.session_state.user_name = name
                st.session_state.user_gender = gender
                st.session_state.saved_password = password
                st.session_state.profile["name"] = name
                st.session_state.has_signed_up = True
                st.success("Sign up successful! Now login below.")
                st.rerun()
    else:
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            if email != st.session_state.user_email or password != st.session_state.saved_password:
                st.error("Incorrect email or password. Please use the same details you used while signing up.")
            else:
                st.session_state.logged_in = True
                st.success("Logged in successfully!")
                st.rerun()


def get_profile():
    return st.session_state.profile


def add_emergency_footer(text: str) -> str:
    warning = (
        "\n\n⚠️ If you feel you might hurt yourself or are in immediate danger, "
        "please contact local emergency services or a trusted adult right now. "
        "This tool cannot handle emergencies."
    )
    return text + warning


def render_top_nav():
    left, mid1, mid2, right = st.columns([1, 4, 1, 1])

    with left:
        if st.button("🏠", help="Home", key="home_icon"):
            st.session_state.current_page = "Home"
            st.rerun()
    with mid1:
        st.markdown("### HerPath Mentor")
    with mid2:
        if st.button("💬", help="App help", key="help_icon"):
            st.session_state.current_page = "Help"
            st.rerun()
    with right:
        if st.button("👤", help="Profile", key="profile_icon"):
            st.session_state.current_page = "Profile"
            st.rerun()


def render_profile_page():
    profile = st.session_state.profile

    st.header("Profile & Resume Details")

    st.subheader("Basic details")
    st.write(f"**Email:** {st.session_state.user_email}")
    st.write(f"**Gender:** {st.session_state.user_gender or 'Not set yet'}")
    st.write(f"**Name:** {profile['name'] or 'Not set yet'}")
    st.write(f"**Age:** {profile['age'] or 'Not set yet'}")
    st.write(f"**Education level:** {profile['education_level'] or 'Not set yet'}")
    st.write(f"**Interests:** {profile['interests'] or 'Not set yet'}")
    st.write(f"**Location:** {profile['location'] or 'Not set yet'}")
    st.write(f"**Financial situation:** {profile['financial_constraint'] or 'Not set yet'}")
    st.write(f"**Goals:** {profile['goals'] or 'Not set yet'}")

    st.markdown("---")
    st.subheader("Education & Resume fields")
    st.write(f"**College:** {profile.get('college', '')}")
    st.write(f"**Degree / Branch:** {profile.get('degree', '')} {profile.get('branch', '')}")
    st.write(f"**CGPA:** {profile.get('cgpa', '')}")
    st.write(f"**Experience (summary):** {profile.get('experience_summary', '')}")
    st.write(f"**Projects (summary):** {profile.get('projects_summary', '')}")
    st.write(f"**Technical Skills:** {profile.get('skills_summary', '')}")
    st.write(f"**Certifications / Achievements:** {profile.get('certifications_summary', '')}")
    st.write(f"**Extra (CP, interests, etc.):** {profile.get('extra_summary', '')}")

    st.markdown("---")
    st.subheader("Profile photo (optional)")
    uploaded_photo = st.file_uploader("Upload a profile picture (JPG/PNG)", type=["jpg", "jpeg", "png"])
    if uploaded_photo is not None:
        st.session_state.profile_photo = uploaded_photo.getvalue()

    if st.session_state.profile_photo:
        st.image(st.session_state.profile_photo, width=150, caption="Profile photo")

    st.markdown("---")

    if not st.session_state.edit_mode:
        if st.button("Edit profile"):
            st.session_state.edit_mode = True
            st.rerun()
    else:
        st.subheader("Edit all resume details")

        name = st.text_input("Name", value=profile["name"], key="profile_name")
        education_level = st.selectbox(
            "Education level",
            ["", "10th", "12th / Inter", "Degree", "Working"],
            index=["", "10th", "12th / Inter", "Degree", "Working"].index(profile["education_level"]),
            key="profile_edu",
        )
        age = st.number_input(
            "Age",
            min_value=10,
            max_value=60,
            value=profile["age"] or 18,
            key="profile_age",
        )
        interests = st.text_input(
            "Your interests (e.g., arts, dance, ML, law, doctor, etc.)",
            profile["interests"],
            key="profile_interests",
        )
        location = st.text_input("Location (city/state)", profile["location"], key="profile_location")
        financial_constraint = st.selectbox(
            "Financial situation",
            ["", "Need low-budget options", "Moderate", "Can afford higher fees"],
            index=["", "Need low-budget options", "Moderate", "Can afford higher fees"].index(
                profile["financial_constraint"]
            ),
            key="profile_financial",
        )
        goals = st.text_area(
            "Your goals (short, in your own words)",
            profile["goals"],
            key="profile_goals",
        )

        college = st.text_input("College", profile.get("college", ""), key="profile_college")
        degree = st.text_input("Degree (e.g., B.Tech, BSc, BA)", profile.get("degree", ""), key="profile_degree")
        branch = st.text_input("Branch / Major (e.g., CSE, ECE, Arts)", profile.get("branch", ""), key="profile_branch")
        cgpa = st.text_input("CGPA / Percentage", profile.get("cgpa", ""), key="profile_cgpa")

        experience_summary = st.text_area(
            "Experience (internships, part-time, volunteering, etc.)",
            profile.get("experience_summary", ""),
            key="profile_experience",
        )

        projects_summary = st.text_area(
            "Projects (college, personal, hackathons, etc.)",
            profile.get("projects_summary", ""),
            key="profile_projects",
        )

        skills_summary = st.text_area(
            "Technical / Other Skills",
            profile.get("skills_summary", ""),
            key="profile_skills",
        )

        certifications_summary = st.text_area(
            "Certifications / Achievements",
            profile.get("certifications_summary", ""),
            key="profile_certs",
        )

        extra_summary = st.text_area(
            "Extra (competitive programming, hobbies, clubs, responsibilities)",
            profile.get("extra_summary", ""),
            key="profile_extra",
        )

        col_save, col_cancel = st.columns(2)
        with col_save:
            if st.button("Save Profile"):
                st.session_state.profile = {
                    "name": name,
                    "age": age,
                    "education_level": education_level,
                    "interests": interests,
                    "location": location,
                    "financial_constraint": financial_constraint,
                    "goals": goals,
                    "college": college,
                    "degree": degree,
                    "branch": branch,
                    "cgpa": cgpa,
                    "experience_summary": experience_summary,
                    "projects_summary": projects_summary,
                    "skills_summary": skills_summary,
                    "certifications_summary": certifications_summary,
                    "extra_summary": extra_summary,
                }
                st.session_state.user_name = name
                st.session_state.edit_mode = False
                st.success("Profile updated.")
                st.rerun()
        with col_cancel:
            if st.button("Cancel"):
                st.session_state.edit_mode = False
                st.rerun()

    st.markdown("### Resume from your profile")

    p = st.session_state.profile

    resume_md = f"""
# {p.get('name','')}

**Email:** {st.session_state.user_email}  
**Location:** {p.get('location','')}

---

## Education
- **{p.get('college','')}** — {p.get('degree','')} in {p.get('branch','')}  
  **CGPA:** {p.get('cgpa','')}

---

## Experience
{p.get('experience_summary','')}

---

## Projects
{p.get('projects_summary','')}

---

## Technical Skills
{p.get('skills_summary','')}

---

## Certifications & Achievements
{p.get('certifications_summary','')}

---

## Additional
- **Financial situation:** {p.get('financial_constraint','')}
- **Goals:** {p.get('goals','')}
- **Extra:** {p.get('extra_summary','')}
"""

    if st.button("Show Resume Preview"):
        st.markdown(resume_md)

    # PDF generation
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader

    def build_resume_pdf():
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Start text a bit lower to avoid header collisions
        y = height - 70

        # Optional photo on the top-right
        photo_size = 80
        if st.session_state.get("profile_photo"):
            try:
                img = ImageReader(BytesIO(st.session_state.profile_photo))
                c.drawImage(
                    img,
                    width - photo_size - 40,   # x
                    height - photo_size - 40,  # y
                    width=photo_size,
                    height=photo_size,
                    preserveAspectRatio=True,
                    mask="auto",
                )
            except Exception:
                # Ignore image errors
                pass

        x = 40  # text always from left

        c.setFont("Helvetica-Bold", 16)
        c.drawString(x, y, p.get("name", ""))
        y -= 25
        c.setFont("Helvetica", 11)
        c.drawString(x, y, f"Email: {st.session_state.user_email}")
        y -= 15
        c.drawString(x, y, f"Location: {p.get('location','')}")
        y -= 30

        def section(title):
            nonlocal y
            if y < 80:
                c.showPage()
                y = height - 70
            c.setFont("Helvetica-Bold", 13)
            c.drawString(x, y, title)
            y -= 18
            c.setFont("Helvetica", 11)

        def split_line(text, max_width, canv):
            words = text.split()
            if not words:
                return [""]
            lines = []
            cur = words[0]
            for w in words[1:]:
                if canv.stringWidth(cur + " " + w, "Helvetica", 11) < max_width:
                    cur += " " + w
                else:
                    lines.append(cur)
                    cur = w
            lines.append(cur)
            return lines

        def write_paragraph(text):
            nonlocal y
            max_width = width - 2 * x
            for line in text.split("\n"):
                for chunk in split_line(line, max_width, c):
                    if y < 60:
                        c.showPage()
                        y = height - 70
                        c.setFont("Helvetica", 11)
                    c.drawString(x, y, chunk)
                    y -= 14
            y -= 8

        section("Education")
        edu = f"{p.get('college','')} — {p.get('degree','')} in {p.get('branch','')} | CGPA: {p.get('cgpa','')}"
        write_paragraph(edu)

        section("Experience")
        write_paragraph(p.get("experience_summary", ""))

        section("Projects")
        write_paragraph(p.get("projects_summary", ""))

        section("Technical Skills")
        write_paragraph(p.get("skills_summary", ""))

        section("Certifications & Achievements")
        write_paragraph(p.get("certifications_summary", ""))

        section("Additional")
        extra_text = (
            f"Financial situation: {p.get('financial_constraint','')}. "
            f"Goals: {p.get('goals','')}. "
            f"Extra: {p.get('extra_summary','')}."
        )
        write_paragraph(extra_text)

        c.save()
        buffer.seek(0)
        return buffer.getvalue()

    pdf_bytes = build_resume_pdf()
    st.download_button(
        "Download Resume (PDF)",
        data=pdf_bytes,
        file_name="resume.pdf",
        mime="application/pdf",
    )

    st.markdown("---")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.guidance_history = []
        st.session_state.support_history = []
        st.session_state.mini_bot_history = []
        st.rerun()


def render_home_page(women_kb, profile):
    st.title("HerPath Mentor")
    st.write(
        "A calm, friendly guide for girls and young women to explore education and career paths, "
        "discover opportunities, and find emotional support."
    )

    tab1, tab2, tab3 = st.tabs(["🧭 Career Guidance", "🎯 Opportunities", "💜 Emotional Support"])

    # -------- Career Guidance tab --------
    with tab1:
        st.subheader("Career & Education")

        user_input = st.text_input(
            "Ask anything about your studies or career path",
            st.session_state.guidance_input_value,
            key="guidance_input",
            placeholder="Example: I finished 10th and I love arts and singing, what can I do next?",
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            send = st.button("Ask HerPath Mentor")
        with col2:
            clear = st.button("Clear career chat")

        if clear:
            st.session_state.guidance_history = []

        if send and user_input.strip():
            system_prompt = build_guidance_system_prompt()

            enriched_question = (
                "User question: "
                + user_input
                + "\n\nYou must give a fresh roadmap each time in paragraph form, not bullet points. "
                  "Adapt strongly to what she typed now. "
                  "If she mentions arts, dance, singing, crafts, design, theatre, or similar, "
                  "focus mainly on creative and arts paths (fine arts, design, animation, fashion, etc.). "
                  "If she says engineering, ML, AI, data science, coding, or similar, "
                  "focus mainly on tech paths. "
                  "Include realistic Indian examples (e.g., entrance exams, common degrees, scholarship searches) "
                  "and keep it budget-aware where needed."
            )
            text_lower = user_input.lower()

            arts_words = [
                "art", "arts", "craft", "crafts", "dance", "sing", "singing",
                "design", "fashion", "music", "drama", "painting", "drawing"
            ]
            tech_words = [
                "engineering", "engineer", "software", "coding", "programming",
                "ml", "machine learning", "ai", "data science", "developer",
                "scientist", "cs", "computer science"
            ]
            medical_words = [
                "doctor", "mbbs", "dentist", "dental", "nurse", "nursing",
                "pharmacy", "pharmacist", "physiotherapist", "medical"
            ]
            law_words = [
                "law", "lawyer", "advocate", "llb", "judge", "legal", "clat"
            ]
            government_words = [
                "government job", "govt job", "group 1", "group 2", "upsc",
                "civil services", "ias", "ips", "ifs", "psc"
            ]

            if any(w in text_lower for w in arts_words):
                enriched_question += (
                    "\n\nShe is especially interested in arts or creative fields. "
                    "Talk mainly about creative courses, diplomas, degrees and careers "
                    "(fine arts, design, animation, fashion, music, theatre, etc.), "
                    "not software engineering."
                )
            if any(w in text_lower for w in tech_words):
                enriched_question += (
                    "\n\nShe is especially interested in technology. "
                    "Talk mainly about engineering, computer science, data, AI/ML, and related paths. "
                    "Mention common entrance exams and budget-friendly options."
                )
            if any(w in text_lower for w in medical_words):
                enriched_question += (
                    "\n\nShe is especially interested in medical fields. "
                    "Talk about MBBS, BDS, nursing, pharmacy, paramedical and related options, "
                    "with entrance exams and realistic challenges."
                )
            if any(w in text_lower for w in law_words):
                enriched_question += (
                    "\n\nShe is especially interested in law. "
                    "Explain paths like 5-year integrated law after 12th, 3-year LLB after degree, "
                    "important exams (like CLAT), and common law careers."
                )
            if any(w in text_lower for w in government_words):
                enriched_question += (
                    "\n\nShe is especially interested in government jobs. "
                    "Talk clearly about realistic paths (state PSC, UPSC, banking exams, SSC, etc.) "
                    "and how to prepare over multiple years from her current stage."
                )

            # Call structured roadmap for extra context like college keywords and budget
            roadmap_json = generate_dynamic_roadmap(profile, user_input)
            colleges_text = ""
            if roadmap_json:
                colleges = get_matching_colleges(roadmap_json)
                if colleges:
                    lines = ["Some example colleges or training places you could search for:"]
                    for c in colleges:
                        lines.append(f"- {c['name']} ({c['course']}) – approx budget: {c['budget']}")
                        lines.append(f"  Link: {c['link']}")
                    colleges_text = "\n".join(lines)

            kb_context = colleges_text

            user_prompt = build_guidance_user_prompt(profile, enriched_question, kb_context)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            with st.spinner("HerPath Mentor is thinking about your path..."):
                answer = call_ai_model(messages)

            # Save the conversation
            st.session_state.guidance_history = []
            st.session_state.guidance_history.append({"role": "user", "content": user_input})
            st.session_state.guidance_history.append({"role": "assistant", "content": answer})

            # Also store the last question for roadmap visualization
            st.session_state.last_guidance_question = user_input

            st.session_state.guidance_input_value = ""
            st.rerun()

        if st.session_state.guidance_history:
            st.markdown("### Career Conversation (roadmap in paragraphs)")
            for msg in st.session_state.guidance_history:
                if msg["role"] == "user":
                    st.markdown(f"**You:** {msg['content']}")
                else:
                    st.markdown("**HerPath Mentor:**")
                    st.markdown(msg["content"])

            # Visual roadmap blocks
            last_q = st.session_state.get("last_guidance_question")
            if last_q:
                st.markdown("### Visual Roadmap (blocks)")
                with st.spinner("Drawing your roadmap..."):
                    roadmap_json = generate_dynamic_roadmap(profile, last_q)
                if roadmap_json and roadmap_json.get("next_stages"):
                    stages = roadmap_json["next_stages"]

                    st.markdown('<div class="roadmap-grid">', unsafe_allow_html=True)

                    for i, stage in enumerate(stages, start=1):
                        title = stage.get("title", f"Stage {i}")
                        desc = stage.get("description", "")
                        exams = stage.get("entrance_exams", [])

                        exams_text = ""
                        if exams:
                            exams_text = "Entrance exams: " + ", ".join(exams)

                        card_html = f"""
                        <div class="roadmap-card">
                          <div class="roadmap-badge">Stage {i}</div>
                          <div class="roadmap-title">{title}</div>
                          <div class="roadmap-desc">{desc}</div>
                          <div class="roadmap-desc"><em>{exams_text}</em></div>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.info(
                        "Roadmap blocks could not be created this time, but you can still follow the written guidance above."
                    )

    # -------- Opportunities tab (schemes and women-only programs) --------
    with tab2:
        st.subheader("Journey Planner – Opportunities")

        tech_tab, nontech_tab = st.tabs(["💻 Tech Path", "🌸 Non‑Tech / Govt Path"])

        with tech_tab:
            st.markdown("#### Women‑focused tech opportunities")
            tech_programs = filter_women_programs(
                women_kb,
                interests=profile.get("interests", ""),
                education_level=profile.get("education_level", ""),
                category="tech",
            )
            st.markdown(format_women_programs_for_display(tech_programs))

        with nontech_tab:
            st.markdown("#### Women‑focused non‑tech & government opportunities")
            nontech_programs = filter_women_programs(
                women_kb,
                interests=profile.get("interests", ""),
                education_level=profile.get("education_level", ""),
                category="non-tech",
            )
            st.markdown(format_women_programs_for_display(nontech_programs))

    # -------- Emotional Support tab --------
    with tab3:
        st.subheader("SoulFriend – Emotional Support")

        st.info(
            "Note: This is not professional medical advice. "
            "For emergencies, please contact local helplines or a trusted adult."
        )

        st.markdown("### Support Conversation")
        for msg in st.session_state.support_history:
            if msg["role"] == "user":
                st.markdown(f"**You:** {msg['content']}")
            else:
                st.markdown(f"**HerPath SoulFriend:** {msg['content']}")

        user_input_support = st.text_input(
            "Type your message",
            st.session_state.support_input_value,
            key="support_input",
            placeholder="Example: I feel very stressed and alone...",
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            send_support = st.button("Send to SoulFriend")
        with col2:
            clear_support = st.button("Clear support chat")

        if clear_support:
            st.session_state.support_history = []

        if send_support and user_input_support.strip():
            system_prompt = build_support_system_prompt()
            profile_local = st.session_state.profile

            messages = [
                {"role": "system", "content": system_prompt},
            ]

            for msg in st.session_state.support_history:
                if msg["role"] == "user":
                    user_prompt_past = build_support_user_prompt(profile_local, msg["content"])
                    messages.append({"role": "user", "content": user_prompt_past})
                else:
                    messages.append({"role": "assistant", "content": msg["content"]})

            user_prompt_now = build_support_user_prompt(profile_local, user_input_support)
            messages.append({"role": "user", "content": user_prompt_now})

            with st.spinner("HerPath SoulFriend is listening with care..."):
                answer = call_ai_model(messages)

            lowered = user_input_support.lower()
            if any(
                phrase in lowered
                for phrase in [
                    "end my life",
                    "kill myself",
                    "suicide",
                    "don't want to live",
                    "hurt myself",
                ]
            ):
                answer = add_emergency_footer(answer)

            st.session_state.support_history.append({"role": "user", "content": user_input_support})
            st.session_state.support_history.append({"role": "assistant", "content": answer})

            st.session_state.support_input_value = ""
            st.rerun()


def render_help_page():
    st.header("HerPath App Help")

    st.markdown(
        """
        This page is like a small support centre.  
        You can ask doubts about how to use the app, where to find schemes, or how to edit your profile.
        """
    )

    st.markdown("### Help chat")

    for msg in st.session_state.mini_bot_history:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**HerPath App Help:** {msg['content']}")

    help_msg = st.text_input(
        "Type a question about the app",
        st.session_state.help_input_value,
        key="mini_bot_input",
        placeholder="Example: How do I see women-only schemes?",
    )

    col_a, col_b = st.columns([1, 1])
    with col_a:
        send_mini = st.button("Send", key="mini_bot_send")
    with col_b:
        clear_mini = st.button("Clear help chat", key="mini_bot_clear")

    if clear_mini:
        st.session_state.mini_bot_history = []

    if send_mini and help_msg.strip():
        system_prompt = (
            "You are a helpful in-app support assistant for the *HerPath Mentor* Streamlit web app. "
            "Only talk about features that exist in this app: Login, Profile & Resume, "
            "Home tabs (Career Guidance, Opportunities, Emotional Support), and the app Help page. "
            "Do NOT invent mobile app features like bottom navigation, community forums, events, or resource libraries. "
            "Explain where the user should click (Home tab, Profile icon, Emotional Support tab, etc.) in simple, friendly language."
        )
        user_prompt = f"User question about the app: {help_msg}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        with st.spinner("HerPath help is replying..."):
            reply = call_ai_model(messages)

        st.session_state.mini_bot_history.append({"role": "user", "content": help_msg})
        st.session_state.mini_bot_history.append({"role": "assistant", "content": reply})

        st.session_state.help_input_value = ""
        st.rerun()


def main():
    st.set_page_config(page_title="HerPath Mentor", page_icon="💜")
    init_session()
    set_background("independent_woman_bg.png")

    if not st.session_state.logged_in:
        show_login()
        return

    women_kb = load_women_programs_kb()
    profile = get_profile()

    render_top_nav()

    page = st.session_state.current_page

    st.markdown('<div class="her-card">', unsafe_allow_html=True)

    if page == "Home":
        render_home_page(women_kb, profile)
    elif page == "Profile":
        render_profile_page()
    elif page == "Help":
        render_help_page()
    else:
        render_home_page(women_kb, profile)

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
