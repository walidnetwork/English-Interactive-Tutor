import streamlit as st
import fitz
import google.generativeai as genai
from PIL import Image
import io

# 1. إعدادات الواجهة (خط أسود واضح جداً للطلاب)
st.set_page_config(page_title="مساعد الإنجليزية الذكي", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Cairo', sans-serif; direction: RTL; text-align: right; }
    .main-question-container { background-color: #ffffff; padding: 18px; border-radius: 12px; border: 2px solid #dee2e6; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .question-text { direction: ltr; text-align: left; font-family: 'Arial', sans-serif; color: #000000; font-size: 1.2em; font-weight: bold; margin-bottom: 12px; padding: 10px; background-color: #f8f9fa; border-radius: 8px; }
    .highlight-answer { color: #d93025; font-weight: bold; text-decoration: underline; }
    details { background: #ffffff; padding: 10px; border-radius: 8px; margin-top: 10px; cursor: pointer; border: 2px solid #28a745; color: #000000; }
    summary { font-weight: bold; color: #155724; outline: none; }
    .explanation-box { margin-top: 10px; color: #000000; line-height: 1.6; text-align: right; font-size: 1.1em; }
</style>
""", unsafe_allow_html=True)

# 2. الربط مع Gemini بمفتاحك المجاني
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # هذا السطر هو الحل لمنع خطأ NotFound
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("⚠️ يرجى وضع مفتاح GEMINI_API_KEY في Secrets")
    st.stop()

# 3. وظائف معالجة الـ PDF
def get_page_image(path, p_num):
    doc = fitz.open(path)
    page = doc[p_num - 1]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    return Image.open(io.BytesIO(pix.tobytes("png")))

def get_gemini_analysis(text):
    prompt = f"""
    أنت معلم لغة إنجليزية خبير. قم بتحليل النص المستخرج من الكتاب.
    المطلوب لكل سؤال:
    1. اكتب السؤال بالإنجليزية كما هو.
    2. الحل (Answer): اكتب الإجابة بالإنجليزية حصراً.
    3. الشرح (Explanation): اكتب السبب باللغة العربية البسيطة فقط. (ممنوع كتابة أي كلمة إنجليزية أو ترجمة في الشرح).
    
    التنسيق:
    <div class="main-question-container">
        <div class="question-text">[السؤال بالإنجليزية]</div>
        <details>
            <summary>🔘 انقر هنا لعرض الحل (Answer)</summary>
            <div class="explanation-box" style="direction: ltr; text-align: left;">
                The answer is: <span class="highlight-answer">[الإجابة]</span>
            </div>
        </details>
        <details>
            <summary>🔘 انقر هنا لعرض الشرح والسبب</summary>
            <div class="explanation-box">[اشرح السبب بالعربي فقط هنا]</div>
        </details>
    </div>
    
    النص: {text}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ خطأ: تأكد من إصدار المكتبة أو المفتاح. ({e})"

# 4. الواجهة الرئيسية
st.title("📚 نظام التفاعل الذكي (نسخة الأستاذ وليد المجانية)")
pdf_path = "data/test_books/primary6_t2.pdf"
page_num = st.number_input("اختر الصفحة:", min_value=1, value=1)

if st.button("🚀 عرض الحلول والشرح"):
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.subheader("📄 الصفحة الأصلية")
        st.image(get_page_image(pdf_path, page_num), use_container_width=True)
    with col2:
        st.subheader("📝 الحلول التفاعلية")
        doc = fitz.open(pdf_path)
        raw_text = doc[page_num - 1].get_text()
        with st.spinner("⏳ جاري التحليل بواسطة Gemini..."):
            result_html = get_gemini_analysis(raw_text)
            st.markdown(result_html, unsafe_allow_html=True)
