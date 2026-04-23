import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai

# --- 1. الإعدادات الأساسية ---
st.set_page_config(page_title="مساعد الإنجليزية الذكي", layout="wide")

# الربط مع مفتاح جيميناي السري
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # التعديل الجذري هنا: استخدم هذا الاسم لضمان التوافق التام
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("⚠️ يرجى ضبط GEMINI_API_KEY في إعدادات Secrets في موقع Streamlit")

# --- 2. تعريف المسارات (تأكد أن المجلدات مطابقة لـ GitHub) ---
TEST_BOOK_PATH = "data/test_books/primary6_t2.pdf"
REF_BOOK_PATH = "primary6_guide.pdf"

# --- 3. الدوال البرمجية ---
def get_pdf_text(path, p_num):
    try:
        doc = fitz.open(path)
        if p_num <= len(doc):
            # استخراج النص مع تنظيفه من المسافات الزائدة
            text = doc[p_num - 1].get_text().strip()
            return text if text else "الصفحة فارغة أو عبارة عن صورة فقط."
        return "رقم الصفحة يتجاوز عدد صفحات الكتاب."
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
        raw_text = get_pdf_text(TEST_BOOK_PATH, page_num)
        
        if raw_text and not raw_text.startswith("Error"):
            st.subheader(f"📝 أسئلة الصفحة رقم {page_num}")
            
            # أمر الذكاء الاصطناعي (Prompt) المطور
            prompt = f"""
            بصفتك معلم لغة إنجليزية خبير، حلل النص التالي المستخرج من كتاب مدرسي:
            {raw_text}
            
            المطلوب منك:
            1. استخراج أسئلة الاختيار من متعدد (MCQs) فقط.
            2. عرض كل سؤال وبجانبه الإجابة الصحيحة بخط عريض.
            3. شرح "سبب الإجابة" باللغة العربية بأسلوب تربوي مبسط للطالب.
            4. أضف لمسة تشجيعية للطالب في نهاية كل إجابة.
            
            استخدم تنسيق Markdown بشكل جذاب، واجعل الشرح في "اقتباس" (Blockquote).
            """
            
            try:
                # محاولة الاتصال بجيميناي
                response = model.generate_content(prompt)
                st.markdown(response.text)
                
                with st.expander("💡 نصيحة تعليمية إضافية"):
                    st.info("تذكر مراجعة الكلمات الدالة (Key Words) في الجملة قبل اختيار الإجابة!")
                    
            except Exception as e:
                # إذا ظهر خطأ 404 هنا، فهذا يعني أن المكتبة تحتاج لتحديث
                st.error(f"عذراً، جيميناي يواجه صعوبة في الاتصال حالياً. تأكد من تحديث ملف requirements.txt")
                st.write(f"تفاصيل الخطأ التقني: {str(e)}")
        else:
            st.warning(f"⚠️ تنبيه: {raw_text}")
            st.info("تأكد من أن ملف PDF موجود في المسار: data/test_books/primary6_t2.pdf")

# تعليمات للطالب
st.sidebar.markdown("---")
st.sidebar.help("اكتب رقم الصفحة واضغط على الزر لرؤية الأسئلة وحلها مع الشرح.")
