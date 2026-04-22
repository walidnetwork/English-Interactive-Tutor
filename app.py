import streamlit as st
import fitz  # PyMuPDF للقراءة من الـ PDF
import google.generativeai as genai

# 1. إعداد جيميناي (سيسحب المفتاح من الإعدادات السرية لاحقاً)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-pro')
else:
    st.error("الرجاء ضبط مفتاح Gemini في إعدادات Secrets")

st.set_page_config(page_title="مساعد الإنجليزية الذكي", layout="wide")
st.title("📖 تطبيق التدريبات التفاعلي")

# 2. وضع المسارات (التي سألت عنها)
test_book_path = "primary6_t2.pdf"
ref_book_path = "primary6_guide.pdf"

# 3. واجهة الاختيارات
with st.sidebar:
    st.header("إعدادات البحث")
    grade = st.selectbox("الصف الدراسي:", ["السادس الابتدائي"])
    page_num = st.number_input("رقم الصفحة في الكتاب:", min_value=1, step=1)

# 4. دالة استخراج النص
def get_pdf_text(path, p_num):
    try:
        doc = fitz.open(path)
        return doc[p_num - 1].get_text()
    except:
        return "تعذر العثور على الصفحة"

if st.button("عرض الأسئلة والشرح"):
    text = get_pdf_text(test_book_path, page_num)
    st.info(f"تم قراءة الصفحة {page_num}")
    
    # هنا نطلب من جيميناي تحليل النص وإعطاء الشرح
    prompt = f"حل هذه الأسئلة من النص واشرح السبب بالعربي من كتاب المرجع: {text}"
    response = model.generate_content(prompt)
    st.write(response.text)
