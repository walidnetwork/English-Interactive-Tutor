import streamlit as st

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="مساعد الإنجليزية - الحلول الذكية", layout="wide")

# 2. إضافة CSS مخصص لتحسين الخطوط واتجاه النصوص (العربي والإنجليزي)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
    }
    
    .arabic-container {
        direction: rtl;
        text-align: right;
        padding: 15px;
        background-color: #f9f9f9;
        border-radius: 10px;
        border-right: 5px solid #2ecc71;
        margin-bottom: 20px;
    }
    
    .english-container {
        direction: ltr;
        text-align: left;
        padding: 15px;
        background-color: #eef2f7;
        border-radius: 10px;
        border-left: 5px solid #3498db;
        margin-bottom: 10px;
        font-weight: 500;
    }

    .highlight {
        color: #e74c3c;
        font-weight: bold;
        text-decoration: underline;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. واجهة المستخدم (Header)
st.markdown('<div style="text-align: center; direction: rtl;"><h1>الحلول الذكية 📝</h1></div>', unsafe_allow_html=True)
st.write("---")

# 4. دالة لعرض الأسئلة بتنسيق احترافي (تمنع تداخل اللغات)
def display_question(q_num, en_text, ar_explanation, en_explanation):
    st.markdown(f'<div class="english-container">{q_num}. {en_text}</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="arabic-container">
        <b>الشرح بالعربي:</b> {ar_explanation}<br>
        <small style="color: #7f8c8d;">English Explanation: {en_explanation}</small>
    </div>
    """, unsafe_allow_html=True)

# 5. دالة لعرض كلمات "المطابقة" (Vocabulary)
def display_vocabulary(letter, definition, word, translation):
    st.markdown(f'<div class="english-container"><b>{letter}.</b> {definition}</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="arabic-container">
        الكلمة الصحيحة: <span class="highlight">{word}</span><br>
        <b>المعنى:</b> {translation}
    </div>
    """, unsafe_allow_html=True)

# --- تنفيذ المحتوى ---

# السؤال الأول
display_question(
    "1", 
    "Have you ever used a gadget or a tool to make something? What was it?",
    "السؤال يطلب منك ذكر مثال لأداة أو جهاز استخدمته لصنع شيء ما.",
    "The question requires extracting an example of using a tool or device to make something."
)

st.subheader("Match each word with its correct meaning:")

# الفقرات (a, b, c, d)
display_vocabulary(
    "a", 
    "Detailed plan or drawing for making something", 
    "Blueprint", 
    "المخطط التفصيلي أو الرسم الهندسي لصنع شيء ما."
)

display_vocabulary(
    "b", 
    "To put parts together to make a whole", 
    "Assemble", 
    "تجميع الأجزاء معاً لتكوين شيء كامل."
)

display_vocabulary(
    "c", 
    "To make something better, or more effective", 
    "Improve", 
    "تحسين الشيء لجعله أفضل أو أكثر كفاءة."
)

display_vocabulary(
    "d", 
    "Things used to fix, build, or make something", 
    "Tools / Gadgets", 
    "الأدوات أو الأجهزة المستخدمة للإصلاح أو البناء."
)

# 6. زر التحكم السفلي
st.write("---")
if st.button("Manage App"):
    st.balloons()
    st.info("App is running smoothly!")
