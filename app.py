import streamlit as st
import fitz
import google.generativeai as genai
from PIL import Image
import io

# 1. تنسيق الواجهة (ألوان واضحة وتصميم متجاوب للموبايل واللاب)
st.set_page_config(page_title="مساعد الإنجليزية الذكي", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Cairo', sans-serif; direction: RTL; text-align: right; }
    .main-question-container { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 2px solid #e9ecef; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .question-text { direction: ltr; text-align: left; font-family: 'Arial', sans-serif; color: #000000; font-size: 1.25em; font-weight: bold; margin-bottom: 15px; padding: 10px; background-color: #f1f3f5; border-radius: 8px; }
    .highlight-answer { color: #d93025; font-weight: 800; text-decoration: underline; }
    details { background: #ffffff; padding: 10px; border-radius: 8px; margin-top: 10px; cursor: pointer; border: 2px solid #28a745; color: #000000; }
    summary { font-weight: bold; color: #155724; outline: none; }
    .explanation-box { margin-top: 10px; color: #1a1a1a; line-height: 1.6; text-align: right; font-size: 1.1em; }
</style>
""", unsafe_allow_html=True)

# 2. الربط مع Gemini (المجاني تماماً)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # استخدام هذا الإصدار حصراً لمنع تعليق السيرفر
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

# 4. دالة التحليل الذكي من مضمون الكتاب
def get_gemini_analysis(text):
    prompt = f"""
    أنت معلم لغة إنجليزية خبير. قم بتحليل النص المستخرج من كتاب الشرح المرفق.
    المطلوب لكل سؤال:
    1. استخرج السؤال بالإنجليزية كما هو.
    2. في زر الحل (Answer): اكتب الحل بالإنجليزية حصراً.
    3. في زر الشرح (Explanation): اشرح "لماذا" اخترنا الحل بناءً على مضمون كتابك، ويجب أن يكون الشرح باللغة العربية فقط (ممنوع الإنجليزية في الشرح).
    
    التنسيق:
    <div class="main-question-container">
        <div class="question-text">[السؤال بالإنجليزية]</div>
        <details>
            <summary>🔘 عرض الحل (Answer)</summary>
            <div class="explanation-box" style="direction: ltr; text-align: left;">
                The answer is: <span class="highlight-answer">[الإجابة بالإنجليزية]</span>
            </div>
        </details>
        <details>
            <summary>🔘 عرض شرح المعلم (عربي)</summary>
            <div class="explanation-box">[اشرح بالعربي فقط هنا]</div>
        </details>
    </div>
    
    النص المستخرج:
    {text}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ حدث خطأ في التحليل: {e}"

# 5. الواجهة الرئيسية
st.title("📚 مساعد الأستاذ وليد الذكي (نسخة Gemini المجانية)")
pdf_path = "data/test_books/primary6_t2.pdf"

page_num = st.number_input("اختر الصفحة:", min_value=1, value=1, step=1)
btn = st.button("🚀 تحليل الصفحة وعرض الحلول")

if btn:
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.subheader("📄 الصفحة الأصلية")
        st.image(get_page_image(pdf_path, page_num), use_container_width=True)
    with col2:
        st.subheader("📝 الحلول والشرح")
        doc = fitz.open(pdf_path)
        raw_text = doc[page_num - 1].get_text()
        with st.spinner("⏳ جاري تحليل الكتاب مجاناً..."):
            result_html = get_gemini_analysis(raw_text)
            st.markdown(result_html, unsafe_allow_html=True)

st.caption("برمجة وتطوير أستاذ وليد 2026")
