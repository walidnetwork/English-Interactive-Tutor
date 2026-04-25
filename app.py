import streamlit as st
import fitz
import google.generativeai as genai
from PIL import Image
import io

# 1. الإعدادات وتنسيق الواجهة
st.set_page_config(page_title="مساعد الإنجليزية الذكي", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Cairo', sans-serif; direction: RTL; text-align: right; }
    .main-question-container { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 2px solid #e9ecef; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .question-text { direction: ltr; text-align: left; font-family: 'Arial', sans-serif; color: #000000; font-size: 1.25em; font-weight: bold; margin-bottom: 15px; padding: 10px; background-color: #f1f3f5; border-radius: 8px; }
    .highlight-answer { color: #d93025; font-weight: bold; text-decoration: underline; }
    details { background: #ffffff; padding: 10px; border-radius: 8px; margin-top: 10px; cursor: pointer; border: 2px solid #28a745; }
    summary { font-weight: bold; color: #155724; }
    .explanation-box { margin-top: 10px; color: #1a1a1a; line-height: 1.6; text-align: right; font-size: 1.1em; }
</style>
""", unsafe_allow_html=True)

# 2. الربط مع Gemini (المجاني والأضمن)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # استخدام هذا الإصدار تحديداً يحل مشكلة الـ 404
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("⚠️ يرجى وضع GEMINI_API_KEY في Secrets")
    st.stop()

# 3. وظائف المعالجة
def get_page_image(path, p_num):
    doc = fitz.open(path)
    page = doc[p_num - 1]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    return Image.open(io.BytesIO(pix.tobytes("png")))

def get_gemini_analysis(text):
    prompt = f"""
    أنت معلم لغة إنجليزية خبير. قم بتحليل النص المستخرج.
    المطلوب لكل سؤال:
    1. السؤال بالإنجليزية.
    2. الإجابة (Answer) بالإنجليزية داخل قالب الحل.
    3. الشرح (Explanation) باللغة العربية فقط، وبأسلوب بسيط جداً. (ممنوع أي لغة أخرى في الشرح).
    
    التنسيق:
    <div class="main-question-container">
        <div class="question-text">[السؤال بالإنجليزية]</div>
        <details>
            <summary>انقر لعرض الحل (Answer)</summary>
            <div class="explanation-box" style="direction: ltr; text-align: left;">
                The answer is: <span class="highlight-answer">[الإجابة]</span>
            </div>
        </details>
        <details>
            <summary>انقر لعرض الشرح والسبب</summary>
            <div class="explanation-box">[الشرح بالعربي فقط]</div>
        </details>
    </div>
    النص: {text}
    """
    response = model.generate_content(prompt)
    return response.text

# 4. الواجهة
st.title("📚 نظام التفاعل الذكي (نسخة Gemini المستقرة)")
pdf_path = "data/test_books/primary6_t2.pdf"
page_num = st.number_input("رقم الصفحة:", min_value=1, value=1)
if st.button("🚀 تشغيل"):
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.image(get_page_image(pdf_path, page_num), use_container_width=True)
    with col2:
        doc = fitz.open(pdf_path)
        raw_text = doc[page_num - 1].get_text()
        with st.spinner("⏳ جاري التحليل..."):
            result_html = get_gemini_analysis(raw_text)
            st.markdown(result_html, unsafe_allow_html=True)
