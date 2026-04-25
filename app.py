import streamlit as st
import fitz
from groq import Groq
from PIL import Image
import io

# تنسيق الأزرار والخط الأسود الواضح
st.set_page_config(page_title="مساعد الإنجليزية الذكي", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@700&display=swap');
    html, body, [class*="st-"] { font-family: 'Cairo', sans-serif; direction: RTL; text-align: right; }
    .main-question-container { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 2px solid #000000; margin-bottom: 25px; }
    .question-text { direction: ltr; text-align: left; color: #000000; font-size: 1.3em; font-weight: bold; padding: 10px; background-color: #f1f3f5; border-radius: 8px; }
    .highlight-answer { color: #d93025; font-weight: 800; text-decoration: underline; }
    details { background: #ffffff; padding: 10px; border-radius: 8px; margin-top: 10px; cursor: pointer; border: 2px solid #28a745; color: #000000; }
    summary { font-weight: bold; color: #155724; font-size: 1.1em; }
    .explanation-box { margin-top: 10px; color: #000000; line-height: 1.6; text-align: right; font-size: 1.1em; }
</style>
""", unsafe_allow_html=True)

# الربط مع Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def get_analysis(text):
    prompt = f"""
    أنت معلم لغة إنجليزية خبير. قم بتحليل الأسئلة التالية:
    1. استخرج السؤال بالإنجليزية.
    2. الحل (Answer) بالإنجليزية.
    3. الشرح (Explanation) باللغة العربية فقط من مضمون المنهج المصري.
    
    استخدم هذا القالب HTML حصراً:
    <div class="main-question-container">
        <div class="question-text">[السؤال هنا]</div>
        <details>
            <summary>🔘 انقر هنا لعرض الحل (Answer)</summary>
            <div class="explanation-box" style="direction: ltr; text-align: left;">
                The answer is: <span class="highlight-answer">[الإجابة]</span>
            </div>
        </details>
        <details>
            <summary>🔘 انقر هنا لعرض الشرح (بالعربي)</summary>
            <div class="explanation-box">[الشرح بالعربي فقط]</div>
        </details>
    </div>
    النص: {text}
    """
    # استخدام موديل Llama 3.1 المستقر جداً
    response = client.chat.completions.create(
        model="llama3-8b-8192"
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# الواجهة
st.title("📚 مساعد الأستاذ وليد - النسخة المستقرة")
pdf_path = "data/test_books/primary6_t2.pdf"
page_num = st.number_input("رقم الصفحة:", min_value=1, value=1)

if st.button("🚀 تشغيل"):
    col1, col2 = st.columns([1, 1.2])
    with col1:
        doc = fitz.open(pdf_path)
        page = doc[page_num - 1]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        st.image(Image.open(io.BytesIO(pix.tobytes("png"))), use_container_width=True)
    with col2:
        raw_text = doc[page_num - 1].get_text()
        with st.spinner("⏳ جاري التحليل..."):
            result = get_analysis(raw_text)
            st.markdown(result, unsafe_allow_html=True)
