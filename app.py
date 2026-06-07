import streamlit as st
from core.orchestrator import AgentOrchestrator

# ── Page config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="සිංහල පිළිතුරු ඇගයීම",
    page_icon="📜",
    layout="wide",
)

# ── Load orchestrator once ─────────────────────────────────────────
@st.cache_resource
def load_orchestrator():
    return AgentOrchestrator()

orchestrator = load_orchestrator()

# ── Header ─────────────────────────────────────────────────────────
st.title("📜 ශ්‍රී ලංකාවේ යටත් විජිත ඉතිහාසය")
st.subheader("සිංහල විවෘත-අවසාන පිළිතුරු ඇගයීමේ පද්ධතිය")
st.markdown("---")

# ── Sidebar ────────────────────────────────────────────────────────
with st.sidebar:
    st.header("ℹ️ පද්ධතිය ගැන")
    st.markdown("""
    **තාක්ෂණ:**
    - 🤖 SinGemma (OLLAMA)
    - 🔍 RAG (ChromaDB)
    - 🧠 ඔන්ටොලොජිය (OWL)
    - 🕵️ නියෝජිත ගෘහ නිර්මාණය

    **යුග:**
    - 🇵🇹 පෘතුගීසි (1505–1658)
    - 🇳🇱 ලන්දේසි (1658–1796)
    - 🇬🇧 බ්‍රිතාන්‍ය (1796–1948)
    """)
    st.markdown("---")
    st.caption("සම්පූර්ණයෙන්ම නොබැඳි (Offline) ක්‍රියාකාරිත්වය")

# ── Question selector ──────────────────────────────────────────────
questions = orchestrator.get_question_list()
era_icons = {
    "portuguese": "🇵🇹",
    "dutch":      "🇳🇱",
    "british":    "🇬🇧",
    "general":    "🌐",
    "comparative":"⚖️",
}

question_options = {
    f"{era_icons.get(q['era'], '📌')} {q['id']} — {q['text'][:80]}...": q["id"]
    for q in questions
}

st.markdown("### 1️⃣ ප්‍රශ්නය තෝරන්න")
selected_label  = st.selectbox("ප්‍රශ්නය", list(question_options.keys()), label_visibility="collapsed")
selected_qid    = question_options[selected_label]
selected_q      = next(q for q in questions if q["id"] == selected_qid)

# Show full question
st.info(f"**ප්‍රශ්නය:** {selected_q['text']}")

# ── Answer input ───────────────────────────────────────────────────
st.markdown("### 2️⃣ ඔබේ පිළිතුර සිංහලෙන් ලියන්න")
student_answer = st.text_area(
    "පිළිතුර",
    height=200,
    placeholder="මෙහි ඔබේ සිංහල පිළිතුර ලියන්න...",
    label_visibility="collapsed",
)

col1, col2 = st.columns([1, 5])
with col1:
    submit = st.button("📊 ලකුණු ගණනය කරන්න", type="primary", use_container_width=True)
with col2:
    clear = st.button("🗑️ මකන්න", use_container_width=False)

if clear:
    st.rerun()

# ── Scoring ────────────────────────────────────────────────────────
if submit:
    if not student_answer.strip():
        st.warning("⚠️ කරුණාකර ඔබේ පිළිතුර ඇතුළත් කරන්න.")
    else:
        with st.spinner("🤖 ඇගයීම සිදු කරමින් පවතී... (30-60 තත්පර)"):
            result = orchestrator.run(selected_qid, student_answer)

        if "error" in result:
            st.error(result["error"])
        else:
            st.markdown("---")

            # ── Score summary ──────────────────────────────────────
            st.markdown("### 📊 ලකුණු සාරාංශය")
            total     = result["total"]
            max_marks = result["total_marks"]
            pct       = int((total / max_marks) * 100) if max_marks else 0

            col1, col2, col3 = st.columns(3)
            col1.metric("ලබාගත් ලකුණු", f"{total} / {max_marks}")
            col2.metric("ප්‍රතිශතය", f"{pct}%")

            if pct >= 75:
                grade, color = "විශිෂ්ට (A)", "🟢"
            elif pct >= 55:
                grade, color = "හොඳ (B)", "🟡"
            elif pct >= 35:
                grade, color = "සමත් (C)", "🟠"
            else:
                grade, color = "අසමත් (F)", "🔴"
            col3.metric("ශ්‍රේණිය", f"{color} {grade}")

            st.progress(pct / 100)

            # ── Criteria breakdown ─────────────────────────────────
            st.markdown("### 📋 නිර්ණායක අනුව ලකුණු")
            for cs in result["criteria_scores"]:
                awarded = cs.get("awarded", 0)
                max_m   = cs.get("max", 0)
                reason  = cs.get("reason", "")
                bar_pct = awarded / max_m if max_m > 0 else 0

                with st.container():
                    c1, c2 = st.columns([1, 5])
                    with c1:
                        st.markdown(f"**{cs['id']}**  \n`{awarded}/{max_m}`")
                    with c2:
                        st.progress(bar_pct)
                        st.caption(reason)

            # ── Overall comment ────────────────────────────────────
            if result.get("overall_comment"):
                st.markdown("### 💬 සාමාන්‍ය අදහස")
                st.success(result["overall_comment"])

            # ── Detailed explanation ───────────────────────────────
            st.markdown("### 📝 සවිස්තර පැහැදිලි කිරීම")
            st.markdown(result["explanation"])

            # ── Era warnings ───────────────────────────────────────
            if result.get("era_warnings"):
                st.markdown("### ⚠️ යුග දෝෂ")
                for w in result["era_warnings"]:
                    st.warning(w)

            # ── Expandable evidence ────────────────────────────────
            with st.expander("🔍 RAG මගින් ලබාගත් සාක්ෂි"):
                for i, chunk in enumerate(result["retrieved_chunks"], 1):
                    st.markdown(f"**සාක්ෂිය {i}** ({chunk['era']})")
                    st.text(chunk["content"][:400])
                    st.markdown("---")

            with st.expander("🧠 ඔන්ටොලොජිය හඳුනාගත් සංකල්ප"):
                if result["ontology_concepts"]:
                    for c in result["ontology_concepts"]:
                        st.markdown(
                            f"- **{c['label']}** `{c['type']}` — {', '.join(c['eras'])}"
                        )
                else:
                    st.info("කිසිදු සංකල්පයක් හඳුනා නොගැනිණි.")