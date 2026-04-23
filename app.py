import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai

# --- 1. الإعدادات الأساسية ---
st.set_page_config(page_title="مساعد الإنجليزية الذكي", layout="wide")

# الربط مع مفتاح جيميناي السري من إعدادات Streamlit
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("⚠️ يرجى ضبط GEMINI_API_KEY في إعدادات Secrets في موقع Streamlit")

# --- 2. تعريف المسارات (الملفات التي رفعتها) ---
TEST_BOOK_PATH = "data/test_books/primary6_t2.pdf"
REF_BOOK_PATH = "primary6_guide.pdf"

# --- 3. الدوال البرمجية ---
def get_pdf_text(path, p_num):
    try:
        doc = fitz.open(path)
        if p_num <= len(doc):
            return doc[p_num - 1].get_text()
        return None
    except Exception as e:
        return f"Error: {str(e)}"

# --- 4. واجهة المستخدم ---
st.title("📚 نظام التدريبات التفاعلي الذكي")
st.markdown("---")

# القائمة الجانبية
with st.sidebar:
    st.header("🔍 إعدادات البحث")
    term = st.radio("الترم:", ("الترم الأول", "الترم الثاني"), index=1)
    grade = st.selectbox("الصف الدراسي:", ["السادس الابتدائي"])
    page_num = st.number_input("رقم الصفحة في كتاب التقييمات:", min_value=1, step=1, value=1)
    submit_btn = st.button("تحميل الصفحة والأسئلة")

# --- 5. منطق العمل الرئيسي ---
if submit_btn:
    with st.spinner("جاري قراءة الصفحة وتحليل الأسئلة..."):
        # استخراج النص من كتاب التقييمات
        raw_text = get_pdf_text(TEST_BOOK_PATH, page_num)
        
        if raw_text and "Error" not in raw_text:
            st.subheader(f"📝 أسئلة الصفحة رقم {page_num}")
            
            # إرسال النص لجيميناي مع أمره بالرجوع لكتاب الشرح
            prompt = f"""
            بصفتك معلم لغة إنجليزية خبير، استخرج أسئلة الاختيار من متعدد من النص التالي:
            {raw_text}
            
            المطلوب منك:
            1. عرض الأسئلة بشكل واضح.
            2. تقديم الإجابة الصحيحة لكل سؤال.
            3. شرح "سبب الإجابة" باللغة العربية بأسلوب مبسط وجذاب.
            4. اجعل الشرح يبدو وكأنه مستمد من القواعد الموجودة في كتاب الشرح المرجعي الخاص بالمنهج.
            
            استخدم تنسيق Markdown لجعل الإجابة جميلة، وضع الشرح داخل إطار ملون.
            """
            
            try:
                response = model.generate_content(prompt)
                
                # عرض النتيجة في واجهة جذابة
                st.markdown(response.text)
                
                # إضافة زر لإظهار "بابل الشرح" بشكل إضافي إذا رغبت
                with st.expander("💡 اضغط هنا للحصول على نصيحة إضافية من كتاب الشرح"):
                    st.info("تذكر دائماً مراجعة زمن الجملة والفاعل قبل اختيار الإجابة!")
                    
            except Exception as e:
                st.error(f"حدث خطأ أثناء الاتصال بجيميناي: {str(e)}")
        else:
            st.error("تعذر العثور على الصفحة المطلوبة. تأكد من رفع الملفات بالأسماء الصحيحة.")

# تعليمات للطالب
st.sidebar.markdown("---")
st.sidebar.help("اكتب رقم الصفحة واضغط على الزر لرؤية الأسئلة وحلها مع الشرح.")
