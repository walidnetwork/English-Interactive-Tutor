import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai

# --- 1. الإعدادات الأساسية للواجهة ---
st.set_page_config(page_title="مساعد الإنجليزية الذكي", layout="wide", page_icon="📚")

# --- 2. الربط مع جيميناي (استخدام المفتاح من Secrets) ---
# تأكد من ضبط المسافات هنا بدقة
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # استخدام الموديل الأحدث والأكثر استقراراً
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("⚠️ خطأ: لم يتم العثور على المفتاح السري GEMINI_API_KEY في إعدادات Streamlit.")
    st.stop()

# --- 3. تعريف مسار الكتاب ---
# تأكد أن الملف موجود في هذا المسار في حسابك على GitHub
TEST_BOOK_PATH = "data/test_books/primary6_t2.pdf"

# --- 4. دالة استخراج النص من الـ PDF ---
def get_pdf_text(path, p_num):
    try:
        doc = fitz.open(path)
        if 1 <= p_num <= len(doc):
            page = doc[p_num - 1]
            text = page.get_text().strip()
            if not text:
                return "⚠️ هذه الصفحة قد تكون صورة فقط. يرجى تجربة صفحة أخرى تحتوي على نص."
            return text
        else:
            return f"❌ رقم الصفحة غير موجود. الكتاب يحتوي على {len(doc)} صفحة."
    except Exception as e:
        return f"❌ خطأ أثناء فتح الملف: {str(e)}"

# --- 5. تصميم واجهة المستخدم ---
st.title("📚 نظام التدريبات التفاعلي الذكي")
st.subheader("مساعد ذكي لشرح أسئلة اللغة الإنجليزية - إعداد الأستاذ وليد")
st.markdown("---")

# القائمة الجانبية (Sidebar)
with st.sidebar:
    st.header("🔍 إعدادات البحث")
    page_num = st.number_input("أدخل رقم الصفحة من الكتاب:", min_value=1, step=1, value=1)
    st.markdown("---")
    submit_btn = st.button("🚀 تحميل وشرح الأسئلة")

# --- 6. المنطق الرئيسي عند الضغط على الزر ---
if submit_btn:
    with st.spinner("⏳ جاري استخراج الأسئلة وتحليلها..."):
        # استخراج النص
        extracted_text = get_pdf_text(TEST_BOOK_PATH, page_num)
        
        if not extracted_text.startswith("❌") and not extracted_text.startswith("⚠️"):
            st.success(f"✅ تم قراءة الصفحة {page_num} بنجاح!")
            
            # صياغة الأمر لجيميناي
            prompt = f"""
            أنت معلم لغة إنجليزية خبير. قم بتحليل النص التالي المستخرج من كتاب مدرسي:
            ---
            {extracted_text}
            ---
            المطلوب منك:
            1. ابدأ بتحية تشجيعية للطالب.
            2. استخرج أسئلة الاختيار من متعدد الموجودة.
            3. لكل سؤال: اذكر الإجابة الصحيحة بخط عريض، واشرح السبب باللغة العربية البسيطة.
            4. اجعل التنسيق جميلاً باستخدام Markdown.
            """
            
            try:
                # توليد الشرح
                response = model.generate_content(prompt)
                st.markdown("---")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"❌ حدث خطأ في الاتصال بالذكاء الاصطناعي: {str(e)}")
        else:
            st.error(extracted_text)

# تذييل الصفحة
st.markdown("---")
st.caption("تم التطوير بواسطة الأستاذ وليد - 2026")
                
