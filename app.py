import streamlit as st
import fitz
from groq import Groq
from PIL import Image
import io

# 1. إعدادات التنسيق (الأزرار التفاعلية والخط الغامق)
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
        color: #000000; /* خط أسود ملكي غامق */
        font-size: 1.25em;
        font-weight: bold;
        margin-bottom: 15px;
        padding: 10px;
        background-color: #f1f3f5;
        border-radius: 8px;
    }
    .highlight-answer {
        color: #d93025; /* أحمر قوي للإجابة */
        font-weight: 800;
        text-decoration: underline;
    }
    /* تنسيق أزرار الحل والشرح */
    details {
        background: #ffffff;
        padding: 10px;
        border-radius: 8px;
        margin-top: 10px;
        cursor: pointer;
        border: 2px solid #28a745;
        color: #000000;
    }
    details[open] {
        background: #f0fff4;
    }
    summary {
        font-weight: bold;
        color: #155724;
        font-size: 1.1em;
        list-style: none;
        outline: none;
    }
    summary:before {
        content: "🔘 "; /* شكل الزر */
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

# 3. وظائف معالجة الـ PDF
def get_page_image(path, p_num):
    doc = fitz.open(path)
    page = doc[p_num - 1]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    return Image.open(io.BytesIO(pix.tobytes("png")))

def get_advanced_analysis(text):
    prompt = f"""
    أنت معلم لغة إنجليزية خبير. قم بتحليل الصفحة المرفقة.
    المطلوب لكل سؤال:
    1. استخرج السؤال كاملاً.
    2. صمم زرين (فقاعتين) لكل سؤال كما يلي:
    
    <div class="main-question-container">
        <div class="question-text">[نص السؤال بالإنجليزية]</div>
        <details>
            <summary>انقر هنا لعرض الحل (Answer)</summary>
            <div class="explanation-box" style="direction: ltr; text-align: left;">
                The answer is: <span class="highlight-answer">[إجابة السؤال بالإنجليزية]</span>
            </div>
        </details>
        <details>
            <summary>انقر هنا لعرض الشرح (Explanation)</summary>
            <div class="explanation-box">
                [اشرح بالعربية والإنجليزية لماذا اخترنا هذه الإجابة]
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

# 4. الواجهة الرئيسية
st.title("📚 نظام التفاعل الذكي")
st.subheader("مساعد الأستاذ وليد - النسخة التفاعلية النهائية")

page_num = st.number_input("أدخل رقم الصفحة:", min_value=1, value=1, step=1)
btn = st.button("🚀 تشغيل عرض الحلول والشرح")

pdf_path = "data/test_books/primary6_t2.pdf"

if btn:
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.subheader("📄 الصفحة الأصلية")
        st.image(get_page_image(pdf_path, page_num), use_container_width=True)
    with col2:
        st.subheader("📝 الأزرار التفاعلية")
        doc = fitz.open(pdf_path)
        raw_text = doc[page_num - 1].get_text()
        with st.spinner("⏳ جاري إنشاء أزرار الحل والشرح..."):
            result_html = get_advanced_analysis(raw_text)
            st.markdown(result_html, unsafe_allow_html=True)

st.caption("برمجة وتطوير أستاذ وليد 2026")
