import streamlit as st
import fitz
from groq import Groq

# 1. الإعدادات
st.set_page_config(page_title="مساعد الإنجليزية الذكي", layout="wide")

# 2. الربط مع Groq
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("⚠️ يرجى وضع مفتاح GROQ_API_KEY في Secrets")
    st.stop()

# 3. المسار
TEST_BOOK_PATH = "data/test_books/primary6_t2.pdf"

# 4. الواجهة
st.title("📚 نظام التدريبات الذكي (نسخة Groq القوية)")
page_num = st.sidebar.number_input("رقم الصفحة:", min_value=1, value=1)

if st.sidebar.button("🚀 شرح الأسئلة"):
    try:
        # قراءة الـ PDF
        doc = fitz.open(TEST_BOOK_PATH)
        text = doc[page_num - 1].get_text()
        
        with st.spinner("⏳ جاري الشرح بواسطة Llama 3..."):
            # طلب الشرح من Groq
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": f"أنت معلم لغة إنجليزية خبير. اشرح الأسئلة التالية بالعربي وبأسلوب ممتع للطلاب:\n{text}",
                    }
                ],
                model="llama3-8b-8192",
            )
            st.markdown(chat_completion.choices[0].message.content)
            
    except Exception as e:
        st.error(f"حدث خطأ: {e}")
