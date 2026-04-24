import streamlit as st
import fitz  # PyMuPDF
from groq import Groq
from PIL import Image
import io

# 1. إعدادات الصفحة وتحسين الخطوط والتنسيق
st.set_page_config(page_title="مساعد الإنجليزية التفاعلي", layout="wide")

# CSS متطور لحل مشكلة العربي والإنجليزي وعرض الفقاعات
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Cairo', sans-serif;
        direction: RTL;
        text-align: right;
    }
    .question-box {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 15px;
        border-right: 8px solid #4A90E2;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        direction: rtl; /* لضمان اتجاه الصندوق عربي */
    }
    details {
        background: #ffffff;
        padding: 12px;
        border-radius: 10px;
        margin-top: 10px;
        cursor: pointer;
        border: 1px solid #e0e0e0;
        transition: 0.3s;
    }
    details summary {
        list-style: none;
        font-weight: bold;
        color: #2c3e50;
        outline: none;
    }
    .answer-text {
        color: #d35400;
        font-weight: bold;
        direction: ltr; /* الإجابة غالباً إنجليزية */
        display: inline-block;
    }
    .explanation-text {
        color: #27ae60;
        line-height: 1.6;
        display: block;
        margin-top: 10px;
    }
    /* تحسين عرض الإنجليزية داخل النص العربي */
    span.en {
        direction: ltr;
        display: inline-block;
        font-family: 'Arial', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# 2. الربط مع Groq
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("⚠️ يرجى ضبط المفتاح GROQ_API_KEY")
    st.stop()

# 3. دالة تحويل صفحة الـ PDF إلى صورة
def get_page_image(pdf_path, p_num):
    doc = fitz.open(pdf_path)
    page = doc[p_num - 1]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # جودة عالية
    img_data = pix.tobytes("png")
    return Image.open(io.BytesIO(img_data))

# 4. دالة معالجة النصوص وطلب التفاعل
def get_interactive_data(text):
    prompt = f"""
    أنت معلم لغة إنجليزية خبير. قم بتحليل الأسئلة التالية وحولها إلى نظام فقاعات تفاعلية.
    استخدم التنسيق التالي لكل سؤال (تأكد من وضع الكلمات الإنجليزية داخل <span class='en'></span>):
    
    <div class="question-box">
        <p><b>السؤال:</b> [اكتب السؤال هنا]</p>
        <details>
            <summary>💡 الإجابة الصحيحة</summary>
            <p class="answer-text">[الإجابة هنا]</p>
        </details>
        <details>
            <summary>📝 الشرح والسبب</summary>
            <p class="explanation-text">[اشرح بالعربي بوضوح لماذا اخترنا هذه الإجابة]</p>
        </details>
    </div>
    
    النص: {text}
    """
    completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    return completion.choices[0].message.content

# 5. بناء الواجهة
st.title("📚 مساعد الإنجليزية الذكي - أستاذ وليد")
TEST_BOOK_PATH = "data/test_books/primary6_t2.pdf"

with st.sidebar:
    st.header("🎮 لوحة التحكم")
    page_num = st.number_input("اختر رقم الصفحة:", min_value=1, value=1)
    run_btn = st.button("✨ عرض الصفحة وتحليلها")

if run_btn:
    try:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📄 الصفحة الأصلية")
            img = get_page_image(TEST_BOOK_PATH, page_num)
            st.image(img, use_container_width=True, caption=f"كتاب التقييم - صفحة {page_num}")
            
        with col2:
            st.subheader("💡 التفاعل والتحليل")
            doc = fitz.open(TEST_BOOK_PATH)
            text = doc[page_num - 1].get_text()
            
            with st.spinner("⏳ جاري تحليل الأسئلة وترتيب الفقاعات..."):
                interactive_html = get_interactive_data(text)
                st.markdown(interactive_html, unsafe_allow_html=True)
                
    except Exception as e:
        st.error(f"حدث خطأ: {e}")

st.markdown("---")
st.caption("برمجة وتطوير أستاذ وليد 2026 - تجربة تعليمية متطورة")
