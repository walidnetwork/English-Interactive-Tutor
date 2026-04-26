import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
from PIL import Image
import io
import json

# --- 1. إعدادات الصفحة والتصميم البصري (نفس تصميم Claude) ---
st.set_page_config(page_title="ALABTAL AI - سلسلة الأبطال", page_icon="📚", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    body { background-color: #07080f; color: #e2e8f0; }
    .stApp { background-color: #07080f; }
    
    /* الحاويات (Cards) */
    .css-1r6p78r, .stMarkdown div[data-testid="stVerticalBlock"] > div {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 14px;
    }
    
    /* الأزرار الذهبية */
    .stButton > button {
        background: linear-gradient(135deg, #f7971e, #ffd200) !important;
        color: #1c1917 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        width: 100%;
        transition: 0.3s;
    }
    
    /* أزرار الأسئلة المستخرجة */
    .q-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        transition: 0.3s;
    }
    
    /* الهيدر */
    .header-container {
        background: rgba(10,13,25,0.97);
        border-bottom: 1px solid rgba(255,215,0,0.2);
        padding: 10px 24px;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. الربط بـ Gemini API ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("⚠️ يرجى ضبط GEMINI_API_KEY في Secrets")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 3. الدوال البرمجية (المحرك) ---
def get_pdf_page_image(pdf_path, page_num):
    doc = fitz.open(pdf_path)
    page = doc[page_num - 1]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    img_data = pix.tobytes("png")
    return Image.open(io.BytesIO(img_data)), doc[page_num - 1].get_text()

def ask_gemini(prompt):
    response = model.generate_content(prompt)
    return response.text

# --- 4. واجهة التطبيق (نفس خطوات Claude) ---

# الهيدر الاحترافي
st.markdown("""
    <div class="header-container">
        <h1 style="background:linear-gradient(135deg,#ffd200,#f7971e);-webkit-background-clip:text;-webkit-text-fill-color:transparent; font-weight:900;">ALABTAL Book Series</h1>
        <p style="color:#64748b; font-size:12px;">English Language · الذكاء الاصطناعي · Walid Elhagary</p>
    </div>
    """, unsafe_allow_html=True)

# الحالة (State) لإدارة الخطوات
if 'step' not in st.session_state: st.session_state.step = "term"
if 'term' not in st.session_state: st.session_state.term = None
if 'grade' not in st.session_state: st.session_state.grade = None

# --- الخطوة 1: اختيار الترم ---
if st.session_state.step == "term":
    st.subheader("اختر الترم الدراسي")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📘 الترم الأول"):
            st.session_state.term = 1
            st.session_state.step = "grade"
            st.rerun()
    with col2:
        if st.button("📗 الترم الثاني"):
            st.session_state.term = 2
            st.session_state.step = "grade"
            st.rerun()

# --- الخطوة 2: اختيار الصف ---
elif st.session_state.step == "grade":
    if st.button("← رجوع للترم"): 
        st.session_state.step = "term"
        st.rerun()
    
    st.subheader(f"اختر الصف الدراسي - ترم {st.session_state.term}")
    grades = [
        "الأول الابتدائي", "الثاني الابتدائي", "الثالث الابتدائي",
        "الرابع الابتدائي", "الخامس الابتدائي", "السادس الابتدائي",
        "الأول الإعدادي", "الثاني الإعدادي", "الثالث الإعدادي"
    ]
    cols = st.columns(2)
    for i, g in enumerate(grades):
        with cols[i % 2]:
            if st.button(g):
                st.session_state.grade = g
                st.session_state.step = "page"
                st.rerun()

# --- الخطوة 3: اختيار الصفحة والحل ---
elif st.session_state.step == "page":
    col_back1, col_back2 = st.columns([1, 5])
    with col_back1:
        if st.button("🏠 البداية"):
            st.session_state.step = "term"
            st.rerun()
    
    st.title(f"📖 {st.session_state.grade} - ترم {st.session_state.term}")
    
    page_num = st.number_input("ادخل رقم الصفحة من كتاب الأبطال:", min_value=1, step=1)
    
    if st.button("عرض الصفحة واستخراج الأسئلة 🚀"):
        # ملاحظة: تأكد من وجود ملفات الـ PDF في مجلد data/books/
        # بتسمية مثل p1_t1.pdf (Grade 1 Term 1)
        pdf_path = f"data/books/grade_{st.session_state.grade}_t{st.session_state.term}.pdf"
        
        try:
            img, text = get_pdf_page_image(pdf_path, page_num)
            
            c1, c2 = st.columns([1, 1])
            with c1:
                st.image(img, caption=f"صفحة رقم {page_num}", use_column_width=True)
            
            with c2:
                st.markdown("### 🤖 تحليل الذكاء الاصطناعي")
                with st.spinner("جاري قراءة الصفحة واستخراج الأسئلة..."):
                    # استخراج الأسئلة
                    q_prompt = f"Extract only the English questions from this text and list them: {text}"
                    questions = ask_gemini(q_prompt)
                    
                    st.info("الأسئلة المكتشفة في الصفحة:")
                    st.write(questions)
                    
                    st.divider()
                    st.markdown("#### 💡 اطلب الحل والشرح")
                    action = st.radio("ماذا تريد من الأبطال؟", ["حل السؤال فقط", "شرح مفصل للسبب والقاعدة"])
                    
                    target_q = st.text_input("انسخ السؤال الذي تريد حله هنا:")
                    
                    if st.button("توليد الإجابة"):
                        if target_q:
                            with st.spinner("جاري التفكير..."):
                                if action == "حل السؤال فقط":
                                    final_prompt = f"Give me the correct answer for this English question: {target_q}"
                                else:
                                    final_prompt = f"Explain the answer for this English question in Arabic, including the grammar rule: {target_q}"
                                
                                result = ask_gemini(final_prompt)
                                st.success("✨ النتيجة:")
                                st.write(result)
                        else:
                            st.warning("يرجى كتابة أو نسخ السؤال أولاً")
                            
        except Exception as e:
            st.error(f"يرجى التأكد من رفع ملف الـ PDF الخاص بـ {st.session_state.grade} في المجلد المخصص.")
            st.info("نصيحة: تأكد من تسمية الملفات بشكل صحيح في Github.")

# تذييل الصفحة
st.markdown("---")
st.caption("ALABTAL AI v2.0 - تطوير أستاذ وليد")
