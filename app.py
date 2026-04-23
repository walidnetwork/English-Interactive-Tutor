import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai

# --- 1. الإعدادات الأساسية للواجهة ---
st.set_page_config(page_title="مساعد الإنجليزية الذكي", layout="wide", page_icon="📚")

# --- 2. الربط مع جيميناي (استخدام المفتاح من Secrets) ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # استخدام الموديل Flash لسرعته في معالجة النصوص المستخرجة
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("⚠️ خطأ: لم يتم العثور على المفتاح السري GEMINI_API_KEY في إعدادات Streamlit.")
    st.stop()

# --- 3. تعريف مسارات الكتب (تأكد من وجود المجلدات في GitHub) ---
# المسار بناءً على ما ظهر في لقطات الشاشة الخاصة بك
TEST_BOOK_PATH = "data/test_books/primary6_t2.pdf"

# --- 4. دالة استخراج النص من الـ PDF ---
def get_pdf_text(path, p_num):
    try:
        doc = fitz.open(path)
        if 1 <= p_num <= len(doc):
            # استخراج النص من الصفحة المطلوبة
            page = doc[p_num - 1]
            text = page.get_text().strip()
            if not text:
                return "⚠️ هذه الصفحة تبدو فارغة أو تحتوي على صور فقط (Scanner). يرجى تجربة صفحة أخرى."
            return text
        else:
            return f"❌ رقم الصفحة غير موجود. الكتاب يحتوي على {len(doc)} صفحة فقط."
    except Exception as e:
        return f"❌ خطأ أثناء فتح الملف: {str(e)}"

# --- 5. تصميم واجهة المستخدم ---
st.title("📚 نظام التدريبات التفاعلي الذكي")
st.subheader("مساعد ذكي لشرح أسئلة اللغة الإنجليزية لطلاب السادس الابتدائي")
st.markdown("---")

# القائمة الجانبية (Sidebar)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3426/3426653.png", width=100)
    st.header("🔍 إعدادات الصفحة")
    term = st.radio("الترم الدراسي:", ("الترم الأول", "الترم الثاني"), index=1)
    page_num = st.number_input("أدخل رقم الصفحة من كتاب التقييمات:", min_value=1, step=1, value=1)
    
    st.markdown("---")
    submit_btn = st.button("🚀 تحليل الصفحة وشرح الأسئلة")

# --- 6. المنطق الرئيسي عند الضغط على الزر ---
if submit_btn:
    with st.spinner("⏳ جاري استخراج النص وتحليله بواسطة الذكاء الاصطناعي..."):
        # الخطوة 1: قراءة النص من ملف الـ PDF
        extracted_text = get_pdf_text(TEST_BOOK_PATH, page_num)
        
        # التأكد من عدم وجود خطأ في الاستخراج
        if not extracted_text.startswith("❌") and not extracted_text.startswith("⚠️"):
            st.success(f"✅ تم قراءة الصفحة {page_num} بنجاح!")
            
            # الخطوة 2: صياغة الأمر (Prompt) لجيميناي
            prompt = f"""
            أنت معلم لغة إنجليزية خبير وودود. لقد استخرجت النص التالي من صفحة في كتاب تقييمات الطالب:
            ---
            {extracted_text}
            ---
            المطلوب منك:
            1. ابدأ بتحية الطالب بعبارة تشجيعية.
            2. استخرج أسئلة الاختيار من متعدد الموجودة في النص.
            3. لكل سؤال: 
               - اذكر السؤال بوضوح.
               - حدد الإجابة الصحيحة بخط عريض.
               - اشرح "لماذا" هذه هي الإجابة الصحيحة باللغة العربية البسيطة (قاعدة الجرامر أو معنى الكلمة).
            4. إذا كانت هناك كلمات صعبة في الصفحة، ترجمها في جدول بسيط.
            
            نسق الإجابة باستخدام Markdown لتكون مريحة للعين، واستخدم الرموز التعبيرية (Emojis).
            """
            
            # الخطوة 3: إرسال الطلب لجيميناي وعرض النتيجة
            try:
                response = model.generate_content(prompt)
                st.markdown("---")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء الاتصال بالذكاء الاصطناعي: {str(e)}")
                st.info("نصيحة: تأكد من تحديث مكتبة google-generativeai في ملف requirements.txt")
        else:
            # عرض رسالة الخطأ في حال فشل استخراج النص
            st.error(extracted_text)
            st.info(f"تأكد من وجود ملف الكتاب في هذا المسار داخل GitHub:\n`{TEST_BOOK_PATH}`")

# تذييل الصفحة
st.markdown("---")
st.caption("تم التطوير بواسطة أستاذ وليد - مساعد الإنجليزية الذكي 2026")
            
