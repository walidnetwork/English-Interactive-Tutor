import streamlit as st
import google.generativeai as genai

# الإعداد الأساسي
st.title("تجربة تشغيل النظام 🚀")

# فحص المفتاح السري
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # تجربة اتصال سريعة
        if st.button("اضغط هنا لاختبار الذكاء الاصطناعي"):
            response = model.generate_content("Say 'Hello Professor Walid, I am working!'")
            st.success(response.text)
            st.balloons()
    except Exception as e:
        st.error(f"خطأ في الاتصال: {e}")
else:
    st.error("المفتاح السري GEMINI_API_KEY غير موجود في إعدادات Secrets")
