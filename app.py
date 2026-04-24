import streamlit as st
import fitz
from groq import Groq
from PIL import Image
import io

# 1. إعدادات وتنسيق متقدم للترتيب البصري
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
        border-radius: 15px;
        border: 1px solid #e1e4e8;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .question-text {
        font-size: 1.1em;
        color: #2c3e50;
        line-height: 1.6;
        margin-bottom: 10px;
        direction: ltr; /* الأسئلة إنجليزية */
        text-align: left;
    }
    .highlight-answer {
        color: #e74c3c;
        font-weight: bold;
        text-decoration: underline;
    }
    details {
        background: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
        margin-top: 10px;
        cursor: pointer;
        border-right: 4px solid #28a745;
    }
    summary {
        font-weight: bold;
        color: #28a745;
        outline: none;
    }
    .explanation-box {
        padding: 10px;
        color: #1e7e34;
        font-size: 0.95em;
    }
</style>
""", unsafe_allow_html=True)

# 2. الربط مع Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. وظيفة معالجة الـ PDF
def get_page_image(path, p_num):
    doc = fitz.open(path)
    page = doc[p_num - 1]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    return Image.open(io.BytesIO(pix.tobytes("png")))

# 4. دالة التحليل الذكي (تم تحديث الـ Prompt لإعادة صياغة الأسئلة)
def get_organized_analysis(text):
    prompt = f"""
    أنت معلم لغة إنجليزية خبير. قم بتحليل النص المستخرج وحوله إلى نظام "سؤال وإجابة" منظم جداً للطالب.
    المطلوب لكل سؤال:
    1. أعد كتابة السؤال كاملاً كما هو في الكتاب.
    2. ضع الإجابة الصحيحة داخل نص السؤال بدلاً من النقاط، وغلّف الإجابة بـ <span class="highlight-answer">الإجابة</span>.
    3. في أسئلة التوصيل، اكتب السطر كاملاً (الكلمة وعريفها الصحيح بجانبها).
    4. أضف فقاعة "الشرح والسبب" أسفل كل سؤال مباشرة.
    
    استخدم هذا التنسيق لكل سؤال:
    <div class="main-question-container">
        <div class="question-text">[نص السؤال كاملاً مع الإجابة الملونة بالداخل]</div>
        <details>
            <summary>💡 لماذا اخترنا هذه الإجابة؟</summary>
            <div class="explanation-box">[اشرح السبب بالعربية بأسلوب بسيط]</div>
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

# 5. الواجهة البرمجية
st.title("📚 نظام التفاعل الذكي - نسخة الطالب المنظمة")
pdf_path = "data/test_books/primary6_t2.pdf"

with st.sidebar:
    st.header("⚙️ الإعدادات")
    page_num = st.number_input("اختر الصفحة:", min_value=1, value=1)
    btn = st.button("🚀 عرض وتحليل منظم")

if btn:
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.subheader("📄 الصفحة الأصلية")
        st.image(get_page_image(pdf_path, page_num), use_container_width=True)
        
    with col2:
        st.subheader("📝 الأسئلة المحلولة")
        doc = fitz.open(pdf_path)
        raw_text = doc[page_num - 1].get_text()
        
        with st.spinner("⏳ جاري تنظيم الأسئلة وشرحها..."):
            structured_html = get_organized_analysis(raw_text)
            st.markdown(structured_html, unsafe_allow_html=True)

st.caption("تطوير أستاذ وليد 2026 - تجربة تعليمية بصرية متطورة")
