import streamlit as st
import fitz
from groq import Groq
from PIL import Image
import io

# 1. إعدادات التنسيق البصري
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
        padding: 20px;
        border-radius: 12px;
        border: 2px solid #e9ecef;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .question-text {
        direction: ltr;
        text-align: left;
        font-family: 'Arial', sans-serif;
        color: #000000;
        font-size: 1.25em;
        font-weight: bold;
        margin-bottom: 15px;
        padding: 10px;
        background-color: #f1f3f5;
        border-radius: 8px;
    }
    .highlight-answer {
        color: #d93025;
        font-weight: 800;
        text-decoration: underline;
    }
    details {
        background: #ffffff;
        padding: 10px;
        border-radius: 8px;
        margin-top: 10px;
        cursor: pointer;
        border: 2px solid #28a745;
    }
    summary {
        font-weight: bold;
        color: #155724;
        font-size: 1.1em;
        outline: none;
    }
    .explanation-box {
        margin-top: 10px;
        color: #1a1a1a;
        line-height: 1.6;
        text-align: right;
        font-size: 1.1em;
    }
</style>
""", unsafe_allow_html=True)

# 2. الربط مع Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. دالة التحليل (تم تعديل الـ Prompt لمنع الترجمة الإنجليزية في الشرح)
def get_advanced_analysis(text):
    prompt = f"""
    أنت معلم لغة إنجليزية خبير. قم بتحليل الصفحة المرفقة.
    المطلوب لكل سؤال:
    1. استخرج السؤال كاملاً بالإنجليزية.
    2. في زر الحل (Answer): اكتب الإجابة بالإنجليزية حصراً.
    3. في زر الشرح (Explanation): اكتب السبب باللغة العربية فقط بأسلوب تربوي، وممنوع نهائياً كتابة أي ترجمة إنجليزية للشرح.
    
    التنسيق:
    <div class="main-question-container">
        <div class="question-text">[السؤال بالإنجليزية]</div>
        <details>
            <summary>انقر هنا لعرض الحل (Answer)</summary>
            <div class="explanation-box" style="direction: ltr; text-align: left;">
                The answer is: <span class="highlight-answer">[الإجابة بالإنجليزية]</span>
            </div>
        </details>
        <details>
            <summary>انقر هنا لعرض الشرح والسبب</summary>
            <div class="explanation-box">
                [اكتب هنا شرح السبب باللغة العربية فقط]
            </div>
        </details>
    </div>
    
    النص: {text}
    """
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    return response.choices[0].message.content

# 4. الواجهة البرمجية (باقي الكود كما هو)
st.title("📚 نظام التفاعل الذكي")
st.subheader("مساعد الأستاذ وليد - الإصدار المخصص")

page_num = st.number_input("أدخل رقم الصفحة:", min_value=1, value=1, step=1)
btn = st.button("🚀 تشغيل عرض الحلول والشرح")

pdf_path = "data/test_books/primary6_t2.pdf"

if btn:
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.subheader("📄 الصفحة الأصلية")
        doc = fitz.open(pdf_path)
        page = doc[page_num - 1]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        st.image(Image.open(io.BytesIO(pix.tobytes("png"))), use_container_width=True)
    with col2:
        st.subheader("📝 التفاعل الذكي")
        raw_text = doc[page_num - 1].get_text()
        with st.spinner("⏳ جاري إنشاء الحلول والشرح بالعربي..."):
            result_html = get_advanced_analysis(raw_text)
            st.markdown(result_html, unsafe_allow_html=True)

st.caption("برمجة وتطوير أستاذ وليد 2026")
