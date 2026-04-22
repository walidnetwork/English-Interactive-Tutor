import streamlit as st

# إعداد واجهة التطبيق
st.set_page_config(page_title="مساعد الإنجليزية التفاعلي", layout="wide")

st.title("📖 تطبيق التدريبات التفاعلي")

# القائمة الجانبية للاختيارات
with st.sidebar:
    st.header("إعدادات البحث")
    term = st.radio("اختر الفصل الدراسي:", ("الترم الأول", "الترم الثاني"))
    
    grade = st.selectbox("اختر الصف الدراسي:", [
        "الأول الابتدائي", "الثاني الابتدائي", "الثالث الابتدائي",
        "الرابع الابتدائي", "الخامس الابتدائي", "السادس الابتدائي",
        "الأول الإعدادي", "الثاني الإعدادي", "الثالث الإعدادي"
    ])
    
    page_num = st.number_input("رقم الصفحة في كتاب التقييمات:", min_value=1, step=1)

# منطقة العرض الرئيسية
st.info(f"عرض تدريبات: {grade} - {term} - صفحة {page_num}")

# نموذج لسؤال تفاعلي (سوف نربطه لاحقاً بملف الـ PDF الخاص بك)
st.subheader("سؤال تجريبي:")
q_text = "She _______ her homework every day."
options = ["do", "does", "doing", "done"]

choice = st.radio("اختر الإجابة الصحيحة:", options)

if st.button("تحقق من إجابتك"):
    if choice == "does":
        st.success("إجابة صحيحة! أحسنت 🌟")
    else:
        st.error("حاول مرة أخرى.")
    
    # بابل الشرح الجذابة
    with st.chat_message("assistant"):
        st.write("💡 **شرح الإجابة بالعربي:**")
        st.write("استخدمنا **does** لأن الفاعل (She) مفرد، وفي زمن المضارع البسيط نضيف (s/es) للفعل مع المفرد.")
