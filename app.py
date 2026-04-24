import streamlit as st
import fitz
import google.generativeai as genai

# الإعدادات
st.set_page_config(page_title="مساعد الإنجليزية الذكي", page_icon="📚")

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # هذا الاسم هو الأضمن للعمل مع كل الإصدارات
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("المفتاح السري غير مضبوط")
    st.stop()

st.title("📚 نظام التدريبات الذكي")

# القائمة الجانبية
page_num = st.sidebar.number_input("رقم الصفحة:", min_value=1, value=1)
if st.sidebar.button("🚀 شرح الأسئلة"):
    try:
        doc = fitz.open("data/test_books/primary6_t2.pdf")
        text = doc[page_num - 1].get_text()
        
        with st.spinner("جاري التحليل..."):
            response = model.generate_content(f"حل واشرح باللغة العربية:\n{text}")
            st.markdown(response.text)
    except Exception as e:
        st.error(f"حدث خطأ: {e}")
