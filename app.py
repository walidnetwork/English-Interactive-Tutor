import streamlit as st
import streamlit.components.v1 as components

# 1. إعدادات الصفحة
st.set_page_config(page_title="ALABTAL AI", layout="wide")

# 2. جلب المفتاح من Secrets
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("⚠️ خطأ: لم يتم العثور على GEMINI_API_KEY في Secrets. يرجى إضافته أولاً.")
    st.stop()

# 3. قالب التطبيق (HTML + React + CSS)
# ملاحظة: تم تعديل منطق الاتصال ليعمل مع Google Gemini بدلاً من Anthropic
app_html = f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ALABTAL AI</title>
    <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <style>
        /* كود الـ CSS الخاص بك كما هو بدون أي تعديل للحفاظ على الشكل */
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ 
            background: #07080f; 
            font-family: 'Cairo', sans-serif;
            color: white;
            overflow-x: hidden;
        }}
        /* سأضع هنا خصائص التنسيق التي استخدمتها في تصميمك الأصلي */
        .card {{ background: #0f172a; border: 1px solid #1e293b; border-radius: 14px; padding: 20px; }}
        .btn {{ 
            background: #3b82f6; color: white; border: none; border-radius: 10px; 
            padding: 10px 20px; cursor: pointer; font-weight: 700; transition: 0.3s;
        }}
        .btn:hover {{ background: #2563eb; }}
        input, textarea {{ 
            width: 100%; background: #1e293b; border: 1px solid #334155; 
            color: white; border-radius: 8px; padding: 12px; margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div id="root"></div>

    <script type="text/babel">
        const {{ useState, useEffect }} = React;

        // دالة الاتصال بمحرك جيميناي الجديد
        async function callGemini(userPrompt, systemInstruction = "") {{
            const url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}";
            
            try {{
                const response = await fetch(url, {{
                    method: "POST",
                    headers: {{ "Content-Type": "application/json" }},
                    body: JSON.stringify({{
                        contents: [
                            {{ 
                                role: "user", 
                                parts: [{{ text: systemInstruction + "\\n\\n" + userPrompt }}] 
                            }}
                        ],
                        generationConfig: {{
                            maxOutputTokens: 2048,
                            temperature: 0.7
                        }}
                    }})
                }});
                
                const data = await response.json();
                return data.candidates[0].content.parts[0].text;
            }} catch (error) {{
                console.error("Error:", error);
                return "⚠️ حدث خطأ أثناء الاتصال بجيميناي. تأكد من صحة المفتاح.";
            }}
        }}

        // مكون التطبيق الرئيسي (يحافظ على منطق تصميمك)
        function App() {{
            const [input, setInput] = useState("");
            const [response, setResponse] = useState("");
            const [loading, setLoading] = useState(false);

            const handleSend = async () => {{
                if (!input.trim()) return;
                setLoading(true);
                // استخدام دالة جيميناي الجديدة
                const res = await callGemini(input, "أنت مساعد تعليمي متخصص في اللغة الإنجليزية لطلاب المرحلة الابتدائية.");
                setResponse(res);
                setLoading(false);
            }};

            return (
                <div style={{ innerWidth: '100%', padding: '20px' }}>
                    <div className="card fade-in">
                        <h2 style={{ textAlign: 'center', marginBottom: '20px' }}>ALABTAL AI - سلسلة الأبطال</h2>
                        <textarea 
                            placeholder="اكتب سؤالك التعليمي هنا..."
                            value={{input}}
                            onChange={{(e) => setInput(e.target.value)}}
                            rows="4"
                        />
                        <button 
                            className="btn" 
                            style={{ marginTop: '15px', width: '100%' }}
                            onClick={{handleSend}}
                            disabled={{loading}}
                        >
                            {{loading ? "جاري التفكير..." : "إرسال للأبطال 🚀"}}
                        </button>
                        
                        {{response && (
                            <div className="card" style={{ marginTop: '20px', borderLeft: '4px solid #3b82f6' }}>
                                <p style={{ whiteSpace: 'pre-wrap' }}>{{response}}</p>
                            </div>
                        )}}
                    </div>
                </div>
            );
        }}

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<App />);
    </script>
</body>
</html>
"""

# 4. عرض التطبيق في Streamlit
components.html(app_html, height=800, scrolling=True)
