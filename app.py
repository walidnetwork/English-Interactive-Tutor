import streamlit as st
import google.generativeai as genai

# 1. إعدادات الصفحة والتصميم
st.set_page_config(page_title="ALABTAL AI - سلسلة الأبطال", page_icon="📚", layout="centered")

# تنسيق الشكل الجمالي ليناسب ذوقك الأصلي
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] {
        font-family: 'Cairo', sans-serif;
        text-align: right;
        direction: rtl;
    }
    .stTextArea textarea {
        background-color: #0f172a;
        color: white;
        border: 1px solid #1e293b;
        border-radius: 10px;
    }
    .main-card {
        background-color: #0f172a;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #1e293b;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. الربط بمفتاح Gemini
if "GEMINI_API_KEY" not in st.secrets:
    st.error("⚠️ يرجى وضع مفتاح GEMINI_API_KEY في Secrets")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. واجهة التطبيق
st.image("https://img.icons8.com/fluency/96/book.png", width=80)
st.title("ALABTAL AI - سلسلة الأبطال")
st.write("مساعدك الذكي في اللغة الإنجليزية - تحت إشراف أستاذ وليد")

with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    user_input = st.text_area("اكتب سؤالك التعليمي هنا أو انسخ نصاً من الكتاب:", height=150, placeholder="مثال: اشرح لي زمن المضارع البسيط...")
    
    if st.button("إرسال للأبطال 🚀", use_container_width=True):
        if user_input:
            with st.spinner("🤖 جاري التفكير بذكاء..."):
                try:
                    # إرسال الطلب لجيميناي
                    prompt = f"أنت مساعد تعليمي خبير في المنهج المصري للغة الإنجليزية. قم بالرد على هذا السؤال باللغة العربية مع الحفاظ على المصطلحات الإنجليزية: {user_input}"
                    response = model.generate_content(prompt)
                    
                    st.markdown("### ✨ الإجابة والتحليل:")
                    st.info(response.text)
                    st.balloons()
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")
        else:
            st.warning("رجاءً اكتب شيئاً أولاً!")
    st.markdown('</div>', unsafe_allow_html=True)

# تذييل الصفحة
st.caption("تطوير أستاذ وليد 2026 - جميع الحقوق محفوظة لسلسلة الأبطال")
