import streamlit as st
import fitz
import google.generativeai as genai

# 1. إعدادات الصفحة
st.set_page_config(page_title="مساعد الإنجليزية الذكي", layout="wide", page_icon="📚")

# 2. الربط مع Gemini
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # الاسم الصحيح للموديل
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("⚠️ مفتاح GEMINI_API_KEY غير مضبوط")
    st.stop()

# 3. مسار الكتاب
TEST_BOOK_PATH = "data/test_books/primary6_t2.pdf"

# 4. دالة استخراج النص
def get_pdf_text(path, p_num):
    try:
        doc = fitz.open(path)
        if 1 <= p_num <= len(doc):
            page = doc[p_num - 1]
            return page.get_text().strip()
        return "❌ رقم الصفحة غير موجود."
    except Exception as e:
        return f"❌ خطأ في فتح الملف: {str(e)}"

# 5. الواجهة
st.title("📚 نظام التدريبات التفاعلي الذكي")
st.subheader("إعداد الأستاذ وليد - 2026")

with st.sidebar:
    st.header("🔍 البحث")
    page_num = st.number_input("رقم الصفحة:", min_value=1, step=1, value=1)
    submit_btn = st.button("🚀 تحميل وشرح الأسئلة")

# 6. التنفيذ
if submit_btn:
    with st.spinner("⏳ جاري التحليل..."):
        extracted_text = get_pdf_text(TEST_BOOK_PATH, page_num)
        if not extracted_text.startswith("❌"):
            prompt = f"أنت معلم إنجليزي خبير. اشرح الأسئلة التالية بأسلوب ممتع بالعربي وبخط واضح:\n{extracted_text}"
            try:
                response = model.generate_content(prompt)
                st.markdown("---")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"❌ خطأ في الذكاء الاصطناعي: {str(e)}")
        else:
            st.error(extracted_text)
