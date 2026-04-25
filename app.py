import streamlit as st
import fitz
from groq import Groq
from PIL import Image
import io

# 1. إعدادات الصفحة والتنسيق (الأزرار والخط الأسود)
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
        color: #000000;
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
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("⚠️ يرجى وضع GROQ_API_KEY في Secrets")
    st.stop()

# 3. وظائف المعالجة
def get_page_image(path, p_num):
    doc = fitz.open(path)
    page = doc[p_num - 1]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    return Image.open(io.BytesIO(pix.tobytes("png")))

def get_analysis(text):
    prompt = f"""
    أنت معلم لغة إنجليزية خبير. قم بتحليل النص المستخرج.
    المطلوب لكل سؤال:
    1. استخرج السؤال بالإنجليزية.
    2. الحل (Answer) بالإنجليزية.
    3. الشرح (Explanation) باللغة العربية فقط من مضمون المنهج.
    
    استخدم هذا القالب حصراً:
    <div class="main-question-container">
        <div class="question-text">[السؤال هنا]</div>
        <details>
            <summary>🔘 انقر هنا لعرض الحل (Answer)</summary>
            <div class="explanation-box" style="direction: ltr; text-align: left;">
                The answer is: <span class="highlight-answer">[الإجابة]</span>
            </div>
        </details>
        <details>
            <summary>🔘 انقر هنا لعرض الشرح والسبب</summary>
            <div class="explanation-box">[شرح السبب بالعربي فقط]</div>
        </details>
    </div>
    النص: {text}
    """
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ خطأ في المحرك: {e}"

# 4. الواجهة الرئيسية
st.title("📚 مساعد الأستاذ وليد - النسخة النهائية")
pdf_path = "data/test_books/primary6_t2.pdf"

page_num = st.number_input("رقم الصفحة:", min_value=1, value=1)
if st.button("🚀 تشغيل عرض الحلول والشرح"):
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.subheader("📄 الصفحة الأصلية")
        st.image(get_page_image(pdf_path, page_num), use_container_width=True)
    with col2:
        st.subheader("📝 الأزرار التفاعلية")
        doc = fitz.open(pdf_path)
        raw_text = doc[page_num - 1].get_text()
        with st.spinner("⏳ جاري التحليل بذكاء Llama 3..."):
            result_html = get_analysis(raw_text)
            st.markdown(result_html, unsafe_allow_html=True)

st.caption("تطوير أستاذ وليد 2026")
