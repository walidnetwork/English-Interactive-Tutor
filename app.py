import streamlit as st
import fitz
from groq import Groq
from PIL import Image
import io

# 1. إعدادات التنسيق البصري (تحسين الخطوط والألوان)
st.set_page_config(page_title="مساعد الإنجليزية الذكي", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] {
        font-family: 'Cairo', sans-serif;
        direction: RTL;
        text-align: right;
    }
    .main-question-container {
        background-color: #ffffff;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #dee2e6;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .question-header {
        font-weight: bold;
        color: #1a73e8;
        margin-bottom: 8px;
        font-size: 1.1em;
    }
    .question-content {
        direction: ltr; /* لضمان ظهور السؤال الإنجليزي بشكل صحيح */
        text-align: left;
        font-family: 'Arial', sans-serif;
        color: #202124;
        font-size: 1.15em;
        line-height: 1.6;
        margin-bottom: 12px;
    }
    .highlight-answer {
        color: #d93025; /* لون أحمر احترافي للإجابة */
        font-weight: bold;
        text-decoration: underline;
        background-color: #fff8f7;
        padding: 0 4px;
        border-radius: 4px;
    }
    details {
        background: #f1f8ff;
        padding: 12px;
        border-radius: 8px;
        cursor: pointer;
        border-right: 5px solid #28a745;
    }
    summary {
        font-weight: bold;
        color: #155724;
        outline: none;
    }
    .explanation-content {
        margin-top: 10px;
        font-size: 0.95em;
        color: #3c4043;
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

# 3. وظائف معالجة الملف
def get_page_image(path, p_num):
    doc = fitz.open(path)
    page = doc[p_num - 1]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    return Image.open(io.BytesIO(pix.tobytes("png")))

# 4. دالة التحليل المطور (Prompt محسن جداً)
def get_advanced_analysis(text):
    prompt = f"""
    أنت معلم لغة إنجليزية خبير. قم بتحليل الصفحة المرفقة بدقة عالية.
    المطلوب:
    1. استخراج كل سؤال مع الالتزام برقمه الأصلي (مثلاً: 1- , 2- ).
    2. وضع الإجابة الصحيحة باللغة الإنجليزية حصراً داخل سياق السؤال بلون مميز باستخدام: 
       <span class="highlight-answer">[English Answer]</span>
    3. في أسئلة التوصيل (Matching): ادمج الكلمة وتعريفها في جملة واحدة كاملة.
    4. في خانة الشرح: قدم تفسيراً مزدوجاً (انجليزي + عربي) يوضح المعنى والقاعدة.
    
    التنسيق المطلوب لكل سؤال:
    <div class="main-question-container">
        <div class="question-header">السؤال رقم [رقم السؤال]:</div>
        <div class="question-content">[نص السؤال بالكامل مع الإجابة الإنجليزية بالداخل]</div>
        <details>
            <summary>💡 الشرح والسبب (Explanation)</summary>
            <div class="explanation-content">
                اشرح بالعربي بوضوح، مع ذكر المفتاح بالإنجليزي مثل: 
                "اخترنا كلمة <span class='en-inline'>[Answer]</span> لأن التعريف يقول <span class='en-inline'>[Definition]</span>"
            </div>
        </details>
    </div>
    
    النص المستخرج:
    {text}
    """
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    return response.choices[0].message.content

# 5. الواجهة
st.title("📚 نظام التفاعل الذكي - مساعد الأستاذ وليد")
pdf_path = "data/test_books/primary6_t2.pdf"

with st.sidebar:
    st.header("⚙️ الإعدادات")
    page_num = st.number_input("اختر الصفحة:", min_value=1, value=1)
    btn = st.button("🚀 عرض وتحليل السؤال")

if btn:
    col1, col2 = st.columns([1, 1.3])
    with col1:
        st.subheader("📄 الصفحة الأصلية")
        st.image(get_page_image(pdf_path, page_num), use_container_width=True)
    with col2:
        st.subheader("📝 الحلول الذكية")
        doc = fitz.open(pdf_path)
        raw_text = doc[page_num - 1].get_text()
        with st.spinner("⏳ جاري تنظيم الأسئلة وشرحها لطلابك..."):
            result_html = get_advanced_analysis(raw_text)
            st.markdown(result_html, unsafe_allow_html=True)

st.caption("برمجة وتطوير أستاذ وليد 2026")
