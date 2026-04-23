import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai

# --- 1. الإعدادات الأساسية للواجهة ---
st.set_page_config(page_title="مساعد الإنجليزية الذكي", layout="wide", page_icon="📚")

# --- 2. الربط مع جيميناي (استخدام المفتاح من Secrets) ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # التعديل الأهم: استخدام اسم الموديل بدون أي إضافات لضمان التوافق
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("⚠️ خطأ: لم يتم العثور على المفتاح السري GEMINI_API_KEY في إعدادات Streamlit.")
    st.stop()

# --- 3. تعريف مسارات الكتب ---
TEST_BOOK_PATH = "data/test_books/primary6_t2.pdf"

# --- 4. دالة استخراج النص من الـ PDF ---
def get_pdf_text(path, p_num):
    try:
        doc = fitz.open(path)
        if 1 <= p_num <= len(doc):
            page = doc[p_num - 1]
            text = page.get_text().strip()
            if not text:
                return "⚠️ هذه الصفحة تبدو فارغة أو تحتوي على صور فقط. يرجى تجربة صفحة أخرى."
            return text
        else:
            return f"❌ رقم الصفحة غير موجود. الكتاب يحتوي على {len(doc)} صفحة فقط."
    except Exception as e:
        return f"❌ خطأ أثناء فتح الملف: {str(e)}"

# --- 5. تصميم واجهة المستخدم ---
st.title("📚 نظام التدريبات التفاعلي الذكي")
st.subheader("مساعد ذكي لشرح أسئلة اللغة الإنجليزية - الأستاذ وليد")
st.markdown("---")

# القائمة الجانبية
with st.sidebar:
    st.header("🔍 إعدادات الصفحة")
    page_num = st.number_input("أدخل رقم الصفحة من كتاب التقييمات:", min_value=1, step=1, value=1)
    st.markdown("---")
    submit_btn = st.button("🚀 تحليل الصفحة وشرح الأسئلة")

# --- 6. المنطق الرئيسي عند الضغط على الزر ---
if submit_btn:
    with st.spinner("⏳ جاري تحليل الأسئلة بواسطة الذكاء الاصطناعي..."):
        extracted_text = get_pdf_text(TEST_BOOK_PATH, page_num)
        
        if not extracted_text.startswith("❌") and not extracted_text.startswith("⚠️"):
            st.success(f"✅ تم قراءة الصفحة {page_num} بنجاح!")
            
            prompt = f"""
            أنت معلم لغة إنجليزية خبير. قم بتحليل النص التالي المستخرج من كتاب مدرسي:
            ---
            {extracted_text}
            ---
            المطلوب:
            1. استخراج أسئلة الاختيار من متعدد.
            2. عرض السؤال مع الإجابة الصحيحة بخط عريض.
            3. شرح "لماذا" هذه هي الإجابة باللغة العربية بأسلوب تربوي ممتع.
            
            نسق الإجابة باستخدام Markdown واستخدم الرموز التعبيرية.
            """
            
            try:
                response = model.generate_content(prompt)
                st.markdown("---")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"❌ حدث خطأ في الاتصال: {str(e)}")
                st.info("تأكد من تحديث ملف requirements.txt إلى الإصدار google-generativeai>=0.5.0")
        else:
            st.error(extracted_text)

st.markdown("---")
st.caption("تطوير أستاذ وليد - 2026")
            
