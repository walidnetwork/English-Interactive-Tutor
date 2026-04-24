import streamlit as st
import fitz
from groq import Groq
from PIL import Image
import io

# 1. إعدادات الصفحة وتحسين الـ CSS للفقاعات والتنسيق العربي
st.set_page_config(page_title="مساعد الإنجليزية التفاعلي", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Cairo', sans-serif;
        direction: RTL;
        text-align: right;
    }
    .question-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 12px;
        border-right: 6px solid #007bff;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    details {
        background: #ffffff;
        padding: 10px;
        border-radius: 8px;
        margin-top: 8px;
        cursor: pointer;
        border: 1px solid #e9ecef;
    }
    summary {
        font-weight: bold;
        color: #0056b3;
        outline: none;
    }
    .answer-content {
        color: #d9534f;
        font-weight: bold;
        direction: ltr;
        display: block;
        text-align: left;
        padding: 5px;
        font-family: 'Arial', sans-serif;
    }
    .explanation-content {
        color: #28a745;
        line-height: 1.6;
        padding: 5px;
    }
</style>
""", unsafe_allow_html=True)

# 2. الربط مع Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. دالة عرض صفحة الـ PDF
def get_page_image(path, p_num):
    doc = fitz.open(path)
    page = doc[p_num - 1]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    return Image.open(io.BytesIO(pix.tobytes("png")))

# 4. دالة التحليل الذكي مع نظام الفقاعات
def get_interactive_analysis(text):
    prompt = f"""
    أنت معلم لغة إنجليزية خبير. قم بتحليل الأسئلة في النص المرفق.
    المطلوب:
    1. استخرج كل سؤال (سواء اختيار أو توصيل Match).
    2. في أسئلة التوصيل، يجب ذكر الإجابة كاملة (الرقم + الكلمة + الحرف المقابل + التعريف).
    3. نسق الإجابة داخل فقاعات تفاعلية (details/summary) كما يلي:
    
    <div class="question-box">
        <p><b>السؤال:</b> [اكتب نص السؤال هنا]</p>
        <details>
            <summary>💡 انقر لعرض الإجابة الصحيحة</summary>
            <div class="answer-content">[اكتب الإجابة الإنجليزية بدقة هنا]</div>
        </details>
        <details>
            <summary>📝 انقر لعرض الشرح والسبب</summary>
            <div class="explanation-content">[اشرح السبب بالعربي بأسلوب تعليمي]</div>
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

# 5. الواجهة الرئيسية
st.title("📚 نظام التقييم التفاعلي - أستاذ وليد")
pdf_path = "data/test_books/primary6_t2.pdf"

with st.sidebar:
    st.header("🎮 التحكم")
    page_num = st.number_input("اختر الصفحة:", min_value=1, value=1)
    btn = st.button("🚀 تشغيل النظام التفاعلي")

if btn:
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.subheader("📄 الصفحة الأصلية")
        st.image(get_page_image(pdf_path, page_num), use_container_width=True)
        
    with col2:
        st.subheader("💡 الأسئلة التفاعلية")
        doc = fitz.open(pdf_path)
        raw_text = doc[page_num - 1].get_text()
        
        with st.spinner("⏳ جاري بناء الفقاعات التفاعلية..."):
            interactive_html = get_interactive_analysis(raw_text)
            st.markdown(interactive_html, unsafe_allow_html=True)

st.caption("تم التطوير بواسطة أستاذ وليد - تجربة تعليمية ممتعة 2026")
