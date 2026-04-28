# ============================================================================
# සිංහල පිළිතුරු ඇගයීම් පද්ධතිය — අනුරාධපුර යුගයේ ඉතිහාසය
# Streamlit UI — ප්‍රධාන යෙදුම
# ============================================================================
#
# සූදානම් කිරීම:
#   1) pip install -r requirements.txt
#   2) ollama pull Tharusha_Dilhara_Jayadeera/singemma:latest
#   3) streamlit run app.py
#
# ============================================================================

import streamlit as st
import os
import sys
import time

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="සිංහල පිළිතුරු ඇගයීම් පද්ධතිය — අනුරාධපුර යුගය",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# SINHALA FONT SUPPORT + CUSTOM CSS
# ============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Sinhala:wght@400;600;700&display=swap');

* {
    font-family: 'Noto Sans Sinhala', 'Iskoola Pota', sans-serif !important;
}

.sinhala-text {
    font-family: 'Noto Sans Sinhala', 'Iskoola Pota', sans-serif !important;
    font-size: 18px !important;
    line-height: 2.2 !important;
    color: #ffffff;
}

.question-box {
    background: #1e3a5f;
    border-radius: 10px;
    padding: 20px;
    margin: 10px 0;
    font-family: 'Noto Sans Sinhala', sans-serif;
    font-size: 18px;
    line-height: 2.2;
    color: #ffffff;
    border-left: 4px solid #4fc3f7;
}

.result-box {
    background: #1b3a2d;
    border-radius: 10px;
    padding: 20px;
    font-family: 'Noto Sans Sinhala', sans-serif;
    font-size: 16px;
    line-height: 2.2;
    color: #ffffff;
    border-left: 4px solid #66bb6a;
}

textarea {
    font-family: 'Noto Sans Sinhala', 'Iskoola Pota', sans-serif !important;
    font-size: 17px !important;
    line-height: 2.2 !important;
}

.stSelectbox label, .stTextArea label {
    font-family: 'Noto Sans Sinhala', sans-serif !important;
    font-size: 16px !important;
}

/* Main header styling */
.main-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 2rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    text-align: center;
    color: white;
}
.main-header h1 {
    color: #e8d44d;
    font-size: 2rem;
    margin-bottom: 0.5rem;
}
.main-header p {
    color: #a0a0b0;
    font-size: 1rem;
}

/* Score display */
.score-box {
    background: linear-gradient(135deg, #0f3460, #16213e);
    padding: 1.5rem;
    border-radius: 12px;
    text-align: center;
    color: white;
    margin: 1rem 0;
}
.score-value {
    font-size: 3rem;
    font-weight: bold;
    color: #e8d44d;
}

/* Status indicators */
.status-ok { color: #00c853; font-weight: bold; }
.status-err { color: #ff5252; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# CACHED RESOURCE LOADERS
# ============================================================================

@st.cache_resource(show_spinner="දැනුම් පදනම පූරණය කරමින්...")
def load_rag_pipeline():
    """Load the RAG pipeline."""
    try:
        from rag.knowledge_base import get_chunks
        from rag.vectorstore import get_or_build_index

        chunks = get_chunks()
        if not chunks:
            return None, None, None, "දැනුම් පදනම පූරණය කිරීමට අසමත් විය"

        index, stored_chunks, model = get_or_build_index(chunks)
        if index is None:
            return None, None, None, "FAISS දර්ශකය ගොඩ නැගීමට අසමත් විය"

        return index, stored_chunks, model, "OK"
    except Exception as e:
        return None, None, None, str(e)


@st.cache_resource(show_spinner="ඔන්ටොලොජිය පූරණය කරමින්...")
def load_ontology_agent():
    """Load the ontology agent."""
    try:
        from agents.ontology_agent import OntologyAgent
        agent = OntologyAgent()
        return agent, "OK"
    except Exception as e:
        return None, str(e)


# ============================================================================
# SIDEBAR — පද්ධති තත්ත්වය
# ============================================================================

with st.sidebar:
    st.markdown("## ⚙️ පද්ධති තත්ත්වය")

    # Check OLLAMA status
    try:
        from agents.scoring_agent import ScoringAgent
        ollama_ok, ollama_msg = ScoringAgent.check_ollama_status()
    except Exception:
        ollama_ok, ollama_msg = False, "ඇගයීම් නියෝජිතය ආනයනය කළ නොහැක"

    if ollama_ok:
        st.markdown('<span class="status-ok">✅ OLLAMA: සම්බන්ධයි</span>',
                     unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-err">❌ OLLAMA: නොබැඳි</span>',
                     unsafe_allow_html=True)
    st.caption(ollama_msg)

    st.markdown("**ආකෘතිය:** `Tharusha_Dilhara_Jayadeera/singemma:latest`")

    # RAG status
    index, stored_chunks, model, rag_status = load_rag_pipeline()
    if rag_status == "OK":
        st.markdown(f'<span class="status-ok">✅ RAG දර්ශකය: පූරණය කළා '
                     f'(කොටස් {len(stored_chunks)}ක්)</span>',
                     unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-err">❌ RAG දර්ශකය: දෝෂයකි</span>',
                     unsafe_allow_html=True)
        st.caption(rag_status)

    # Ontology status
    ontology_agent, ont_status = load_ontology_agent()
    if ont_status == "OK":
        st.markdown('<span class="status-ok">✅ ඔන්ටොලොජිය: පූරණය කළා</span>',
                     unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-err">❌ ඔන්ටොලොජිය: දෝෂයකි</span>',
                     unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 📋 උපදෙස්")
    st.markdown("""
    1. පතන ලැයිස්තුවෙන් **ප්‍රශ්නයක් තෝරන්න**
    2. ප්‍රශ්නය **කියවන්න**
    3. **ඔබේ පිළිතුර සිංහලෙන්** ලියන්න
    4. **පිළිතුර ඇගයීම් කරන්න** බොත්තම ඔබන්න
    5. සවිස්තරාත්මක ප්‍රතිඵල බලන්න
    """)

    st.markdown("---")
    st.caption("NLP තනි පැවරුම 02")
    st.caption("නොබැඳි බුද්ධිමත් පිළිතුරු ඇගයීම් පද්ධතිය")


# ============================================================================
# ප්‍රධාන කොටස — මාතෘකාව
# ============================================================================

st.markdown("""
<div class="main-header">
    <h1>🏛️ සිංහල පිළිතුරු ඇගයීම් පද්ධතිය</h1>
    <p>අනුරාධපුර යුගයේ ඉතිහාසය — බුද්ධිමත් ඇගයීම් පද්ධතිය</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# ප්‍රශ්න පූරණය
# ============================================================================

try:
    from questions.questions import get_all_questions, get_question
    all_questions = get_all_questions()
except Exception as e:
    st.error(f"ප්‍රශ්න පූරණය කිරීමට අසමත් විය: {e}")
    all_questions = []

if not all_questions:
    st.error("ප්‍රශ්න නොමැත. questions/questions.py පරීක්ෂා කරන්න")
    st.stop()

# ============================================================================
# ප්‍රශ්නය තෝරාගැනීම
# ============================================================================

question_options = {
    f"ප්‍රශ්නය {q['id']}: {q['title']}": q["id"] for q in all_questions
}

selected_label = st.selectbox(
    "📝 ප්‍රශ්නයක් තෝරන්න",
    options=list(question_options.keys()),
    index=0
)

selected_id = question_options[selected_label]
selected_q = get_question(selected_id)

if selected_q:
    # Display the question in Sinhala only
    st.markdown("### ප්‍රශ්නය")
    st.markdown(f'<div class="question-box sinhala-text">{selected_q["sinhala"]}</div>',
                unsafe_allow_html=True)

# ============================================================================
# පිළිතුර ඇතුළත් කිරීම
# ============================================================================

st.markdown("---")
st.markdown("### ✍️ ඔබේ පිළිතුර සිංහලෙන් ලියන්න")

student_answer = st.text_area(
    "ඔබේ පිළිතුර මෙහි ටයිප් කරන්න",
    height=200,
    placeholder="ඔබේ පිළිතුර සිංහලෙන් මෙහි ලියන්න..."
)

# ============================================================================
# ඇගයීම් බොත්තම සහ ප්‍රවාහය
# ============================================================================

col_btn, col_space = st.columns([1, 3])
with col_btn:
    score_button = st.button("🎯 පිළිතුර ඇගයීම් කරන්න", type="primary",
                              use_container_width=True)

if score_button:
    if not student_answer or student_answer.strip() == "":
        st.error("⚠️ කරුණාකර ඇගයීම් කිරීමට පෙර ඔබේ පිළිතුර ලියන්න.")
    elif not selected_q:
        st.error("⚠️ කරුණාකර පළමුව ප්‍රශ්නයක් තෝරන්න.")
    elif rag_status != "OK":
        st.error("⚠️ RAG ප්‍රවාහය පූරණය වී නැත. පැති තීරුවේ පද්ධති තත්ත්වය පරීක්ෂා කරන්න.")
    elif not ollama_ok:
        st.error("⚠️ OLLAMA ක්‍රියාත්මක නොවේ. කරුණාකර පළමුව OLLAMA ආරම්භ කරන්න: `ollama serve`")
    else:
        # ================================================================
        # ඇගයීම් ප්‍රවාහය
        # ================================================================
        results_container = st.container()

        with results_container:
            # Step 1: Retrieval
            with st.spinner("🔍 දැනුම් පදනමෙන් තොරතුරු සොයමින්..."):
                try:
                    from agents.retrieval_agent import RetrievalAgent
                    retrieval_agent = RetrievalAgent(index, stored_chunks, model)
                    retrieved_chunks = retrieval_agent.retrieve(
                        student_answer, selected_q["sinhala"]
                    )
                    time.sleep(0.3)
                except Exception as e:
                    st.error(f"සෙවීම් දෝෂය: {e}")
                    retrieved_chunks = []

            # Step 2: Ontology
            with st.spinner("🧠 ඔන්ටොලොජියෙන් අදාළ සංකල්ප සොයමින්..."):
                try:
                    if ontology_agent:
                        ontology_facts = ontology_agent.get_context(
                            selected_q["topic"], student_answer
                        )
                    else:
                        ontology_facts = "ඔන්ටොලොජිය ලබා ගත නොහැක."
                    time.sleep(0.3)
                except Exception as e:
                    st.error(f"ඔන්ටොලොජි දෝෂය: {e}")
                    ontology_facts = "ඔන්ටොලොජි විමසුම අසාර්ථක විය."

            # Step 3: Scoring with LLM
            with st.spinner("🤖 AI මගින් ඇගයීම් කරමින් (CPU මත මිනිත්තු 1-2ක් ගත විය හැක)..."):
                try:
                    scoring_agent = ScoringAgent()
                    score_result = scoring_agent.score(
                        question=selected_q["sinhala"],
                        marking_guide=selected_q["marking_guide"],
                        student_answer=student_answer,
                        retrieved_chunks=retrieved_chunks,
                        ontology_facts=ontology_facts
                    )
                except Exception as e:
                    st.error(f"ඇගයීම් දෝෂය: {e}")
                    score_result = {
                        "total_score": 0,
                        "criteria_scores": {},
                        "raw_response": f"දෝෂය: {e}"
                    }

            # Step 4: Generate Explanation
            with st.spinner("📝 පැහැදිලි කිරීම ජනනය කරමින්..."):
                try:
                    from agents.explanation_agent import ExplanationAgent
                    explanation_agent = ExplanationAgent()
                    explanation = explanation_agent.explain(
                        question=selected_q["sinhala"],
                        student_answer=student_answer,
                        total_score=score_result["total_score"],
                        criteria_scores=score_result["criteria_scores"],
                        retrieved_chunks=retrieved_chunks,
                        ontology_facts=ontology_facts
                    )
                except Exception as e:
                    st.error(f"පැහැදිලි කිරීම් දෝෂය: {e}")
                    explanation = f"පැහැදිලි කිරීම ජනනය කළ නොහැක: {e}"

            # ================================================================
            # ප්‍රතිඵල පෙන්වීම
            # ================================================================
            st.markdown("---")
            st.markdown("## 📊 ඇගයීම් ප්‍රතිඵල")

            total = score_result["total_score"]
            pass_fail = "සමත් ✅" if total >= 10 else "අසමත් ❌"

            # Score metric display
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown(f"""
                <div class="score-box">
                    <div class="score-value">{total} / 20</div>
                    <div style="font-size: 1.2rem; margin-top: 0.5rem;">
                        {pass_fail}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Progress bar
            st.progress(min(total / 20.0, 1.0))

            # Criteria table
            st.markdown("### සවිස්තරාත්මක නිර්ණායක ලකුණු")
            criteria_table = []
            for criterion, scores in score_result["criteria_scores"].items():
                awarded = scores["awarded"]
                max_marks = scores["max"]
                pct = (awarded / max_marks * 100) if max_marks > 0 else 0

                if pct >= 70:
                    status = "✅ හොඳයි"
                elif pct >= 40:
                    status = "⚠️ අර්ධ වශයෙන්"
                else:
                    status = "❌ දුර්වලයි"

                criteria_table.append({
                    "නිර්ණායකය": criterion,
                    "උපරිම ලකුණු": max_marks,
                    "ලබාදුන් ලකුණු": awarded,
                    "තත්ත්වය": status
                })

            st.table(criteria_table)

            # Explanation
            st.markdown("### 💬 පැහැදිලි කිරීම")
            st.markdown(f'<div class="result-box sinhala-text">{explanation}</div>',
                        unsafe_allow_html=True)

            # Expanders for evidence and ontology
            with st.expander("📚 සොයාගත් සාක්ෂි"):
                if retrieved_chunks:
                    for i, chunk in enumerate(retrieved_chunks, 1):
                        if isinstance(chunk, dict):
                            st.markdown(f"**කොටස {i}** "
                                        f"(සමානතාවය: {chunk.get('score', 0):.4f})")
                            st.text(chunk.get("chunk", ""))
                        else:
                            st.markdown(f"**කොටස {i}**")
                            st.text(str(chunk))
                        st.markdown("---")
                else:
                    st.write("සාක්ෂි කොටස් කිසිවක් සොයාගත නොහැකි විය.")

            with st.expander("🧠 භාවිත කළ සංකල්ප"):
                if ontology_facts and ontology_facts != "ඔන්ටොලොජිය ලබා ගත නොහැක.":
                    st.markdown(ontology_facts)
                else:
                    st.write("ඔන්ටොලොජි සංකල්ප කිසිවක් යොමු නොකළේය.")

            # Marking guide AFTER results (ISSUE 3)
            with st.expander("📊 ලකුණු ලබාදීමේ මාර්ගෝපදේශය"):
                guide = selected_q["marking_guide"]
                st.markdown(f"**මුළු ලකුණු: {selected_q['total_marks']}**")

                table_data = []
                for i, c in enumerate(guide, 1):
                    table_data.append({
                        "#": i,
                        "නිර්ණායකය": c["criterion"],
                        "උපරිම ලකුණු": c["marks"],
                        "විස්තර": c["details"]
                    })
                st.table(table_data)
