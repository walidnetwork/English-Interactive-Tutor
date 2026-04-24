import streamlit as st
import fitz
from groq import Groq

# 1. إعدادات الصفحة والجماليات
st.set_page_config(page_title="مساعد الإنجليزية التفاعلي", layout="wide")

# تصميم الفقاعات التفاعلية باستخدام CSS
st.markdown("""
<style>
    .question-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-right: 5px solid #ff4b4b;
        margin-bottom: 20px;
    }
    details {
        background: #ffffff;
        padding: 10px;
        border-radius: 8px;
        margin-top: 5px;
        cursor: pointer;
        border: 1px solid #ddd;
    }
    details[open] {
        background: #e1f5fe;
    }
    summary {
        font-weight: bold;
        color: #1565c0;
    }
    .explanation {
        color: #2e7d32;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# 2. الربط مع Groq
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("⚠️ يرجى ضبط المفتاح في Secrets")
    st.stop()

# 3. دالة معالجة النصوص
def get_interactive_explanation(text):
    prompt = f"""
    أنت معلم لغة إنجليزية خبير. قم بتحويل الأسئلة التالية إلى نظام فقاعات تفاعلية.
    لكل سؤال، أخرج النتيجة بتنسيق HTML التالي حصراً:
    
    <div class="question-box">
        <p><b>السؤال:</b> [اكتب السؤال هنا]</p>
        <details>
            <summary>💡 انقر لعرض الإجابة</summary>
            <p><b>الإجابة الصحيحة:</b> [الإجابة]</p>
        </details>
        <details>
            <summary>📝 انقر لعرض الشرح والسبب</summary>
            <p class="explanation">[اشرح السبب باللغة العربية بأسلوب تربوي ممتع]</p>
        </details>
    </div>
    
    النص المستخرج:
    {text}
    """
    completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    return completion.choices[0].message.content

# 4. الواجهة الرئيسية
st.title("📚 نظام التقييم التفاعلي الذكي")
st.subheader("تحويل صفحات الكتاب إلى تجربة تعليمية نابضة")

TEST_BOOK_PATH = "data/test_books/primary6_t2.pdf"

with st.sidebar:
    st.header("⚙️ التحكم")
    page_num = st.number_input("رقم الصفحة:", min_value=1, value=1)
    process_btn = st.button("🚀 تشغيل التفاعل")

if process_btn:
    try:
        # قراءة الـ PDF
        doc = fitz.open(TEST_BOOK_PATH)
        page = doc[page_num - 1]
        text = page.get_text()
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.info(f"📄 النص المستخرج من الصفحة {page_num}")
            st.text_area("", text, height=400)
            
        with col2:
            st.success("✨ الشرح التفاعلي (انقر على الأزرار)")
            with st.spinner("⏳ جاري بناء الفقاعات..."):
                html_response = get_interactive_explanation(text)
                st.markdown(html_response, unsafe_allow_html=True)
                
    except Exception as e:
        st.error(f"حدث خطأ: {e}")

st.markdown("---")
st.caption("مطور بواسطة الأستاذ وليد - تجربة تعليمية تفاعلية 2026")
