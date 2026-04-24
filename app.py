import streamlit as st
import fitz
from groq import Groq
from PIL import Image
import io

# 1. إعدادات وتنسيق CSS (تم تحسينه ليكون أكثر وضوحاً في العربي والإنجليزي)
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
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        border-right: 8px solid #007bff;
        margin-bottom: 20px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    .answer-header {
        color: #ff4b4b;
        font-weight: bold;
        font-size: 1.1em;
        margin-bottom: 5px;
    }
    .explanation-header {
        color: #28a745;
        font-weight: bold;
        font-size: 1.1em;
    }
    .en-text {
        direction: ltr;
        display: inline-block;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        color: #007bff;
    }
</style>
""", unsafe_allow_html=True)

# 2. الربط مع Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. دالة معالجة الـ PDF (صورة)
def get_page_image(path, p_num):
    doc = fitz.open(path)
    page = doc[p_num - 1]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    return Image.open(io.BytesIO(pix.tobytes("png")))

# 4. دالة التحليل الذكي (تم تعديل الـ Prompt هنا)
def analyze_content(text):
    prompt = f"""
    أنت معلم لغة إنجليزية خبير. قم بتحليل النص المستخرج من صفحة الكتاب.
    المطلوب:
    1. استخرج الأسئلة (سواء كانت اختيار من متعدد أو توصيل Match).
    2. في أسئلة التوصيل: اكتب الإجابة كاملة (الرقم + الكلمة + الحرف المقابل + التوصيل الصحيح).
    3. اشرح "لماذا" اخترنا هذه الإجابة بالعربية بأسلوب بسيط.
    
    نسق النتيجة داخل هذا القالب حصراً لكل سؤال:
    <div class="question-box">
        <div class="answer-header">💡 الإجابة الصحيحة:</div>
        <p dir="ltr" class="en-text">[اكتب هنا الإجابة الإنجليزية بدقة]</p>
        <div class="explanation-header">📝 الشرح والسبب:</div>
        <p>[اشرح هنا بالعربي]</p>
    </div>
    
    النص: {text}
    """
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    return response.choices[0].message.content

# 5. الواجهة البرمجية
st.title("📚 نظام التقييم التفاعلي - أستاذ وليد")
pdf_path = "data/test_books/primary6_t2.pdf"

with st.sidebar:
    st.header("🎮 التحكم")
    page_num = st.number_input("اختر الصفحة:", min_value=1, value=1)
    btn = st.button("🚀 عرض وتحليل الصفحة")

if btn:
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.subheader("📄 الصفحة الأصلية")
        st.image(get_page_image(pdf_path, page_num), use_container_width=True)
        
    with col2:
        st.subheader("💡 الإجابات والشرح")
        doc = fitz.open(pdf_path)
        raw_text = doc[page_num - 1].get_text()
        
        with st.spinner("⏳ جاري استخراج الإجابات بدقة..."):
            result_html = analyze_content(raw_text)
            st.markdown(result_html, unsafe_allow_html=True)

st.caption("تم التطوير بواسطة أستاذ وليد - 2026")
