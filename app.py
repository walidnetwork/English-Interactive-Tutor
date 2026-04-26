import streamlit as st
import pdfplumber
import google.generativeai as genai
from PIL import Image
import io
import base64
import json
import re

# ========== إعداد الصفحة ==========
st.set_page_config(
    page_title="معلمي الذكي",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== إعداد Gemini API (مجاني) ==========
# احصل على مفتاح مجاني من: https://aistudio.google.com/app/apikey
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')  # نموذج مجاني ممتاز
else:
    st.warning("⚠️ يرجى إضافة مفتاح Gemini API في secrets")
    model = None

# ========== بيانات الصفوف ==========
GRADES = [
    {"id": "p1", "label": "الصف الأول الابتدائي", "short": "أول ابتدائي", "level": "primary", "color": "#4ecdc4"},
    {"id": "p2", "label": "الصف الثاني الابتدائي", "short": "ثاني ابتدائي", "level": "primary", "color": "#45b7d1"},
    {"id": "p3", "label": "الصف الثالث الابتدائي", "short": "ثالث ابتدائي", "level": "primary", "color": "#96ceb4"},
    {"id": "p4", "label": "الصف الرابع الابتدائي", "short": "رابع ابتدائي", "level": "primary", "color": "#88d8b0"},
    {"id": "p5", "label": "الصف الخامس الابتدائي", "short": "خامس ابتدائي", "level": "primary", "color": "#6bcb77"},
    {"id": "p6", "label": "الصف السادس الابتدائي", "short": "سادس ابتدائي", "level": "primary", "color": "#4d9de0"},
    {"id": "m1", "label": "الصف الأول الإعدادي", "short": "أول إعدادي", "level": "middle", "color": "#e15554"},
    {"id": "m2", "label": "الصف الثاني الإعدادي", "short": "ثاني إعدادي", "level": "middle", "color": "#e1bc29"},
    {"id": "m3", "label": "الصف الثالث الإعدادي", "short": "ثالث إعدادي", "level": "middle", "color": "#f7971e"},
]

# ========== دوال مساعدة ==========
def extract_text_from_pdf_page(pdf_file, page_num):
    """استخراج النص من صفحة محددة في PDF"""
    with pdfplumber.open(pdf_file) as pdf:
        if page_num < 1 or page_num > len(pdf.pages):
            return None
        page = pdf.pages[page_num - 1]
        text = page.extract_text()
        return text or ""

def render_pdf_page_as_image(pdf_file, page_num):
    """تحويل صفحة PDF إلى صورة لعرضها"""
    with pdfplumber.open(pdf_file) as pdf:
        if page_num < 1 or page_num > len(pdf.pages):
            return None
        page = pdf.pages[page_num - 1]
        # تحويل الصفحة إلى صورة
        im = page.to_image(resolution=150)
        img_bytes = io.BytesIO()
        im.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        return Image.open(img_bytes)

def call_gemini(prompt, system_prompt=""):
    """استدعاء Gemini API"""
    if not model:
        return "⚠️ Gemini API غير متاح. يرجى إضافة المفتاح في secrets."
    
    try:
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"❌ خطأ: {str(e)}"

def extract_questions_from_text(text):
    """استخراج الأسئلة من النص باستخدام AI"""
    if not text or not text.strip():
        return []
    
    prompt = f"""النص التالي مأخوذ من صفحة كتاب تقييمات مدرسي مصري.
استخرج جميع الأسئلة من هذا النص فقط.
قم بإرجاع JSON array من الكائنات بهذا التنسيق:
[{{"id": 1, "text": "نص السؤال الأول"}}, {{"id": 2, "text": "نص السؤال الثاني"}}]

لا ترجع أي شيء آخر غير JSON.

النص:
{text[:4000]}"""

    try:
        response = call_gemini(prompt, "أنت مساعد تعليمي متخصص. أجب بـ JSON فقط.")
        # تنظيف الرد
        clean = re.sub(r'```json\s*|```\s*', '', response)
        questions = json.loads(clean)
        return questions if isinstance(questions, list) else []
    except:
        # محاولة استخراج أسئلة بسيطة إذا فشل JSON
        lines = text.split('\n')
        questions = []
        q_num = 1
        for line in lines:
            line = line.strip()
            if len(line) > 15 and any(marker in line for marker in ['؟', 'ما', 'من', 'اذكر', 'عرف', 'اشرح']):
                questions.append({"id": q_num, "text": line[:200]})
                q_num += 1
                if q_num > 10:
                    break
        return questions

def get_answer_and_explanation(question_text, ref_text="", page_context=""):
    """الحصول على الإجابة والشرح من AI"""
    
    answer_prompt = f"""السؤال: {question_text}

{ref_text if ref_text else ''}

أعطني الإجابة الصحيحة فقط في جملة أو جملتين قصيرتين، بدون مقدمات أو شرح."""

    explanation_prompt = f"""السؤال: {question_text}

{ref_text if ref_text else ''}

اشرح الإجابة بطريقة مبسطة ومفيدة للطالب. اذكر السبب أو التحليل. استخدم اللغة العربية الفصحى البسيطة."""

    answer = call_gemini(answer_prompt, "أنت مدرس مصري محترف. أجب بإجابة قصيرة ومباشرة.")
    explanation = call_gemini(explanation_prompt, "أنت مدرس مصري محترف. اشرح بطريقة مبسطة تناسب الطالب.")
    
    return answer, explanation

# ========== تهيئة حالة الجلسة ==========
if 'files' not in st.session_state:
    st.session_state.files = {}
if 'view' not in st.session_state:
    st.session_state.view = 'student'
if 'student_term' not in st.session_state:
    st.session_state.student_term = None
if 'student_grade' not in st.session_state:
    st.session_state.student_grade = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = None
if 'current_page_image' not in st.session_state:
    st.session_state.current_page_image = None
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'answers_cache' not in st.session_state:
    st.session_state.answers_cache = {}

# ========== CSS تنسيق ==========
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    * {
        font-family: 'Cairo', sans-serif;
    }
    .stApp {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
    }
    .main-header {
        background: #161b22;
        border-bottom: 1px solid #30363d;
        padding: 1rem 2rem;
        border-radius: 0;
        margin-bottom: 2rem;
    }
    .grade-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .grade-card:hover {
        transform: translateY(-5px);
        border-color: #f7971e;
        box-shadow: 0 8px 25px rgba(247,151,30,0.2);
    }
    .question-card {
        background: #0d1117;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    .question-card:hover {
        border-color: #58a6ff;
        background: #161b22;
    }
    .answer-box {
        background: rgba(67,206,162,0.1);
        border: 1px solid #43cea2;
        border-radius: 12px;
        padding: 1rem;
        margin-top: 0.75rem;
    }
    .explain-box {
        background: rgba(247,151,30,0.1);
        border: 1px solid #f7971e;
        border-radius: 12px;
        padding: 1rem;
        margin-top: 0.75rem;
    }
    .stButton > button {
        background: linear-gradient(135deg, #f7971e, #ffd200);
        color: #1a1a1a;
        font-weight: 700;
        border: none;
        border-radius: 12px;
        padding: 0.5rem 1.5rem;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(247,151,30,0.4);
    }
    </style>
""", unsafe_allow_html=True)

# ========== واجهة المستخدم ==========

# الهيدر
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <span style="font-size: 3rem;">📚</span>
            <h1 style="color: #e6edf3; margin: 0;">معلمي الذكي</h1>
            <p style="color: #8b949e;">منصة الحلول التعليمية المصرية</p>
        </div>
    """, unsafe_allow_html=True)

# أزرار التبديل بين الطالب والمعلم
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
with col2:
    if st.button("🎓 الطالب", use_container_width=True, type="primary" if st.session_state.view == 'student' else "secondary"):
        st.session_state.view = 'student'
        st.rerun()
with col3:
    if st.button("🏫 المعلم", use_container_width=True, type="primary" if st.session_state.view == 'teacher' else "secondary"):
        st.session_state.view = 'teacher'
        st.rerun()

st.divider()

# ========== عرض لوحة المعلم ==========
if st.session_state.view == 'teacher':
    st.markdown("### 🏫 لوحة تحكم المعلم")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### 📖 اختر الصف")
        selected_grade_id = st.selectbox(
            "الصف الدراسي",
            options=[g["id"] for g in GRADES],
            format_func=lambda x: next(g["label"] for g in GRADES if g["id"] == x)
        )
        selected_grade = next(g for g in GRADES if g["id"] == selected_grade_id)
        
        selected_term = st.radio("الترم", ["الترم الأول", "الترم الثاني"], horizontal=True)
        term_key = "term1" if selected_term == "الترم الأول" else "term2"
    
    with col2:
        st.markdown("#### 📂 رفع الملفات")
        
        # رفع ملف التقييمات
        book_file = st.file_uploader(
            "📋 ملف التقييمات (الأسئلة)",
            type=['pdf'],
            key=f"book_{selected_grade_id}_{term_key}"
        )
        if book_file:
            if selected_grade_id not in st.session_state.files:
                st.session_state.files[selected_grade_id] = {}
            if term_key not in st.session_state.files[selected_grade_id]:
                st.session_state.files[selected_grade_id][term_key] = {}
            st.session_state.files[selected_grade_id][term_key]["book"] = book_file
            st.success(f"✅ تم رفع {book_file.name}")
        
        # رفع ملف المرجع
        ref_file = st.file_uploader(
            "📖 مرجع الشرح (الحلول)",
            type=['pdf'],
            key=f"ref_{selected_grade_id}_{term_key}"
        )
        if ref_file:
            if selected_grade_id not in st.session_state.files:
                st.session_state.files[selected_grade_id] = {}
            if term_key not in st.session_state.files[selected_grade_id]:
                st.session_state.files[selected_grade_id][term_key] = {}
            st.session_state.files[selected_grade_id][term_key]["ref"] = ref_file
            st.success(f"✅ تم رفع {ref_file.name}")
    
    # عرض الملفات المرفوعة
    st.markdown("#### 📊 ملفات تم رفعها")
    uploaded_count = 0
    for g in GRADES:
        for t in ["term1", "term2"]:
            if st.session_state.files.get(g["id"], {}).get(t, {}).get("book"):
                uploaded_count += 1
            if st.session_state.files.get(g["id"], {}).get(t, {}).get("ref"):
                uploaded_count += 1
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📚 إجمالي الصفوف", len(GRADES))
    with col2:
        st.metric("📂 الملفات المرفوعة", uploaded_count)
    with col3:
        st.metric("📅 الترمين", "الأول + الثاني")

# ========== عرض واجهة الطالب ==========
else:
    # اختيار الترم
    if st.session_state.student_term is None:
        st.markdown("### 📅 اختر الترم الدراسي")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📘 الترم الأول", use_container_width=True):
                st.session_state.student_term = 1
                st.rerun()
        with col2:
            if st.button("📙 الترم الثاني", use_container_width=True):
                st.session_state.student_term = 2
                st.rerun()
    
    # اختيار الصف
    elif st.session_state.student_grade is None:
        st.markdown(f"### 🎓 اختر الصف الدراسي - الترم {st.session_state.student_term}")
        
        if st.button("← العودة لاختيار الترم"):
            st.session_state.student_term = None
            st.rerun()
        
        term_key = f"term{st.session_state.student_term}"
        cols = st.columns(3)
        
        for idx, grade in enumerate(GRADES):
            with cols[idx % 3]:
                has_files = st.session_state.files.get(grade["id"], {}).get(term_key, {}).get("book") is not None
                
                if has_files:
                    if st.button(
                        f"📚 {grade['label']}",
                        key=f"grade_{grade['id']}",
                        use_container_width=True
                    ):
                        st.session_state.student_grade = grade
                        st.rerun()
                else:
                    st.markdown(f"""
                        <div style="background:#161b22; border:1px solid #30363d; border-radius:16px; padding:1.5rem; text-align:center; opacity:0.5;">
                            <div style="font-size:2rem;">📚</div>
                            <div style="color:#e6edf3;">{grade['label']}</div>
                            <div style="color:#8b949e; font-size:0.8rem;">❌ لا توجد ملفات</div>
                        </div>
                    """, unsafe_allow_html=True)
    
    # عرض الصفحة
    else:
        term_key = f"term{st.session_state.student_term}"
        book_file = st.session_state.files.get(st.session_state.student_grade["id"], {}).get(term_key, {}).get("book")
        ref_file = st.session_state.files.get(st.session_state.student_grade["id"], {}).get(term_key, {}).get("ref")
        
        # زر العودة
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("← تغيير الصف"):
                st.session_state.student_grade = None
                st.session_state.current_page = None
                st.session_state.questions = []
                st.rerun()
        
        st.markdown(f"""
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <h2 style="color: #f7971e;">{st.session_state.student_grade['label']}</h2>
                <p style="color: #8b949e;">الترم {st.session_state.student_term}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # إدخال رقم الصفحة
        if st.session_state.current_page is None:
            page_num = st.number_input("📖 أدخل رقم الصفحة", min_value=1, step=1, key="page_input")
            
            if st.button("🔍 عرض الصفحة", use_container_width=True):
                if book_file:
                    with st.spinner("جاري تحميل الصفحة..."):
                        # عرض الصفحة كصورة
                        image = render_pdf_page_as_image(book_file, page_num)
                        if image:
                            st.session_state.current_page = page_num
                            st.session_state.current_page_image = image
                            
                            # استخراج النص والأسئلة
                            text = extract_text_from_pdf_page(book_file, page_num)
                            if text:
                                with st.spinner("جاري استخراج الأسئلة..."):
                                    questions = extract_questions_from_text(text)
                                    st.session_state.questions = questions
                            st.rerun()
                        else:
                            st.error("رقم الصفحة غير موجود")
                else:
                    st.error("لم يتم رفع ملف التقييمات لهذا الصف بعد")
        
        # عرض الصفحة والأسئلة
        else:
            # عرض الصفحة
            col_img, col_questions = st.columns([1, 0.8])
            
            with col_img:
                st.markdown("#### 📄 صفحة الكتاب")
                st.image(st.session_state.current_page_image, use_container_width=True)
                
                # أزرار التنقل بين الصفحات
                col_prev, col_page, col_next = st.columns([1, 2, 1])
                with col_prev:
                    if st.button("⬅️ السابق", use_container_width=True):
                        new_page = st.session_state.current_page - 1
                        if new_page >= 1:
                            st.session_state.current_page = new_page
                            image = render_pdf_page_as_image(book_file, new_page)
                            if image:
                                st.session_state.current_page_image = image
                                text = extract_text_from_pdf_page(book_file, new_page)
                                if text:
                                    with st.spinner("جاري استخراج الأسئلة..."):
                                        st.session_state.questions = extract_questions_from_text(text)
                                st.rerun()
                with col_next:
                    if st.button("التالي ➡️", use_container_width=True):
                        new_page = st.session_state.current_page + 1
                        st.session_state.current_page = new_page
                        image = render_pdf_page_as_image(book_file, new_page)
                        if image:
                            st.session_state.current_page_image = image
                            text = extract_text_from_pdf_page(book_file, new_page)
                            if text:
                                with st.spinner("جاري استخراج الأسئلة..."):
                                    st.session_state.questions = extract_questions_from_text(text)
                            st.rerun()
            
            with col_questions:
                st.markdown("#### 📝 الأسئلة")
                
                if not st.session_state.questions:
                    st.info("🤖 لم يتم العثور على أسئلة في هذه الصفحة")
                else:
                    for idx, q in enumerate(st.session_state.questions):
                        with st.expander(f"❓ السؤال {idx + 1}", expanded=False):
                            st.markdown(f"**{q['text']}**")
                            
                            col_a, col_e = st.columns(2)
                            
                            with col_a:
                                if st.button("💡 الإجابة", key=f"ans_{idx}"):
                                    cache_key = f"{st.session_state.current_page}_{idx}_answer"
                                    if cache_key not in st.session_state.answers_cache:
                                        with st.spinner("جاري الحصول على الإجابة..."):
                                            ref_text = ""
                                            if ref_file:
                                                page_text = extract_text_from_pdf_page(ref_file, st.session_state.current_page)
                                                if page_text:
                                                    ref_text = page_text[:2000]
                                            answer, _ = get_answer_and_explanation(q['text'], ref_text)
                                            st.session_state.answers_cache[cache_key] = answer
                                    st.session_state[f"show_answer_{idx}"] = True
                            
                            with col_e:
                                if st.button("📖 الشرح", key=f"exp_{idx}"):
                                    cache_key = f"{st.session_state.current_page}_{idx}_explain"
                                    if cache_key not in st.session_state.answers_cache:
                                        with st.spinner("جاري الحصول على الشرح..."):
                                            ref_text = ""
                                            if ref_file:
                                                page_text = extract_text_from_pdf_page(ref_file, st.session_state.current_page)
                                                if page_text:
                                                    ref_text = page_text[:2000]
                                            _, explanation = get_answer_and_explanation(q['text'], ref_text)
                                            st.session_state.answers_cache[cache_key + "_explain"] = explanation
                                    st.session_state[f"show_explain_{idx}"] = True
                            
                            # عرض الإجابة
                            if st.session_state.get(f"show_answer_{idx}", False):
                                ans_key = f"{st.session_state.current_page}_{idx}_answer"
                                if ans_key in st.session_state.answers_cache:
                                    st.markdown(f"""
                                        <div class="answer-box">
                                            <strong>✅ الإجابة:</strong><br>
                                            {st.session_state.answers_cache[ans_key]}
                                        </div>
                                    """, unsafe_allow_html=True)
                            
                            # عرض الشرح
                            if st.session_state.get(f"show_explain_{idx}", False):
                                exp_key = f"{st.session_state.current_page}_{idx}_explain_explain"
                                if exp_key in st.session_state.answers_cache:
                                    st.markdown(f"""
                                        <div class="explain-box">
                                            <strong>📖 التحليل والشرح:</strong><br>
                                            {st.session_state.answers_cache[exp_key]}
                                        </div>
                                    """, unsafe_allow_html=True)
