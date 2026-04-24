import streamlit as st
import fitz
from groq import Groq
from PIL import Image
import io

# 1. إعدادات التنسيق البصري (تحسين العرض للموبايل)
st.set_page_config(page_title="مساعد الإنجليزية الذكي", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] {
        font-family: 'Cairo', sans-serif;
        direction: RTL;
        text-align: right;
    }
    /* تحسين شكل المدخلات على الموبايل */
    .stNumberInput, .stButton button {
        width: 100% !important;
    }
    .main-question-container {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #dee2e6;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .question-content {
        direction: ltr;
        text-align: left;
        font-family: 'Arial', sans-serif;
        color: #202124;
        font-size: 1.1em;
        line-height: 1.5;
        margin-bottom: 10px;
    }
    .highlight-answer {
        color: #d93025;
        font-weight: bold;
        text-decoration: underline;
    }
    details {
        background: #f1f8ff;
        padding: 10px;
        border-radius: 8px;
        cursor: pointer;
        border-right: 5px solid #28a745;
    }
    summary {
        font-weight: bold;
        color: #155724;
    }
    .en-inline {
        direction: ltr;
        display: inline-block;
        font-weight: bold;
        color: #1a73e8;
    }
</style>
""", unsafe_allow_html=True)

# 2. الربط مع Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. وظائف المعالجة
def get_page_image(path, p_num):
    doc = fitz.open(path)
    page = doc[p_num - 1]
    pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)) # تقليل الحجم قليلاً للموبايل
    return Image.open(io.BytesIO(pix.tobytes("png")))

def get_advanced_analysis(text):
    prompt = f"""
    أنت معلم لغة إنجليزية خبير. قم بتحليل الصفحة المرفقة بدقة.
    المطلوب:
    1. استخراج كل سؤال برقمه الأصلي.
    2. وضع الإجابة الإنجليزية داخل السؤال بلون مميز باستخدام: <span class="highlight-answer">[Answer]</span>
    3. الشرح يكون (انجليزي + عربي) يوضح السبب.
    نسق النتيجة داخل div class="main-question-container".
    النص: {text}
    """
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    return response.choices[0].message.content

# 4. الواجهة الرئيسية (نقل المدخلات من Sidebar إلى الصفحة الرئيسية)
st.title("📚 نظام التفاعل الذكي")
st.subheader("مساعد الأستاذ وليد - 2026")

# وضع مربع البحث والزر في الأعلى لسهولة الاستخدام على الموبايل
col_input, col_btn = st.columns([2, 1])
with col_input:
    page_num = st.number_input("أدخل رقم الصفحة:", min_value=1, value=1, step=1)
with col_btn:
    st.write(" ") # لضبط المحاذاة
    btn = st.button("🚀 عرض وتحليل")

pdf_path = "data/test_books/primary6_t2.pdf"

if btn:
    # على الموبايل، يفضل عرض العناصر تحت بعضها بدلاً من عمودين متجاورين
    # لذا سنقوم بفحص عرض الشاشة أو استخدام ترتيب مرن
    
    st.subheader("📄 الصفحة الأصلية")
    st.image(get_page_image(pdf_path, page_num), use_container_width=True)
    
    st.markdown("---")
    st.subheader("📝 الحلول الذكية")
    
    doc = fitz.open(pdf_path)
    raw_text = doc[page_num - 1].get_text()
    
    with st.spinner("⏳ جاري التحليل لطلابك..."):
        result_html = get_advanced_analysis(raw_text)
        st.markdown(result_html, unsafe_allow_html=True)

st.caption("برمجة وتطوير أستاذ وليد 2026")
