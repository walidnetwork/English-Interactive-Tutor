import streamlit as st
import fitz
from openai import OpenAI
from PIL import Image
import io

# 1. تنسيق الواجهة الاحترافية
st.set_page_config(page_title="مساعد الإنجليزية الذكي", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Cairo', sans-serif; direction: RTL; text-align: right; }
    .main-question-container { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 2px solid #e9ecef; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .question-text { direction: ltr; text-align: left; font-family: 'Arial', sans-serif; color: #000000; font-size: 1.25em; font-weight: bold; margin-bottom: 15px; padding: 10px; background-color: #f1f3f5; border-radius: 8px; }
    .highlight-answer { color: #d93025; font-weight: 800; text-decoration: underline; }
    details { background: #ffffff; padding: 10px; border-radius: 8px; margin-top: 10px; cursor: pointer; border: 2px solid #28a745; color: #000000; }
    summary { font-weight: bold; color: #155724; font-size: 1.1em; outline: none; }
    .explanation-box { margin-top: 10px; color: #1a1a1a; line-height: 1.6; text-align: right; font-size: 1.1em; }
</style>
""", unsafe_allow_html=True)

# 2. الربط مع ChatGPT
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
else:
    st.error("⚠️ يرجى وضع مفتاح OPENAI_API_KEY في Secrets")
    st.stop()

# 3. وظيفة معالجة الـ PDF
def get_page_image(path, p_num):
    doc = fitz.open(path)
    page = doc[p_num - 1]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    return Image.open(io.BytesIO(pix.tobytes("png")))

# 4. دالة التحليل المعتمدة على مضمون الكتاب
def get_gpt_analysis(text):
    # هذا الأمر (Prompt) يجبره على الالتزام بمضمون الكتاب واللغة العربية
    prompt = f"""
    بصفتك معلم لغة إنجليزية خبير، قم بتحليل النص المستخرج من كتاب الشرح المرفق.
    
    التعليمات الصارمة:
    1. استخرج كل سؤال بالإنجليزية بدقة.
    2. في زر الحل (Answer): ضع الإجابة الصحيحة بالإنجليزية حصراً بناءً على سياق الكتاب.
    3. في زر الشرح (Explanation): اشرح "لماذا" هذه هي الإجابة الصحيحة بناءً على القواعد الموجودة في الكتاب.
    4. لغة الشرح: يجب أن يكون الشرح باللغة العربية البسيطة والمباشرة فقط. (ممنوع منعاً باتاً استخدام الإنجليزية أو أي لغة أخرى في الشرح).
    
    نسق النتيجة بهذا الشكل لكل سؤال:
    <div class="main-question-container">
        <div class="question-text">[السؤال هنا بالإنجليزية]</div>
        <details>
            <summary>🔘 عرض الحل (Answer)</summary>
            <div class="explanation-box" style="direction: ltr; text-align: left;">
                The correct answer is: <span class="highlight-answer">[الإجابة هنا]</span>
            </div>
        </details>
        <details>
            <summary>🔘 عرض شرح المعلم</summary>
            <div class="explanation-box">
                [اكتب هنا الشرح بالعربي فقط بناءً على مضمون الكتاب]
            </div>
        </details>
    </div>
    
    النص المستخرج من الصفحة:
    {text}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "أنت مساعد تعليمي متخصص في المنهج الدراسي المصري، تلتزم بمضمون الكتاب المرفق وتشرح بالعربية فقط."},
                      {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ خطأ في ChatGPT: {e}"

# 5. الواجهة الرئيسية
st.title("📚 نظام التفاعل الذكي (ChatGPT - نسخة الكتاب)")
pdf_path = "data/test_books/primary6_t2.pdf" # تأكد من صحة مسار كتابك

page_num = st.number_input("اختر الصفحة من كتاب الشرح:", min_value=1, value=1, step=1)
btn = st.button("🚀 تحليل الصفحة وعرض الحلول")

if btn:
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.subheader("📄 معاينة الصفحة")
        st.image(get_page_image(pdf_path, page_num), use_container_width=True)
    with col2:
        st.subheader("📝 الشرح والحلول")
        doc = fitz.open(pdf_path)
        raw_text = doc[page_num - 1].get_text()
        with st.spinner("⏳ ChatGPT يقرأ الكتاب ويحلل الأسئلة..."):
            result_html = get_gpt_analysis(raw_text)
            st.markdown(result_html, unsafe_allow_html=True)

st.caption("تطوير أستاذ وليد 2026 - تجربة تعليمية معززة بذكاء GPT-4o")
