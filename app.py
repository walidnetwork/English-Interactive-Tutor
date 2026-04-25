import { useState, useRef, useEffect, useCallback } from "react";

/* ─── GRADE DATA ─── */
const GRADES = [
  { id:"p1", label:"الصف الأول الابتدائي",   short:"أول ابتدائي",  level:"primary", color:"#4ecdc4" },
  { id:"p2", label:"الصف الثاني الابتدائي",  short:"ثاني ابتدائي", level:"primary", color:"#45b7d1" },
  { id:"p3", label:"الصف الثالث الابتدائي",  short:"ثالث ابتدائي", level:"primary", color:"#96ceb4" },
  { id:"p4", label:"الصف الرابع الابتدائي",  short:"رابع ابتدائي", level:"primary", color:"#88d8b0" },
  { id:"p5", label:"الصف الخامس الابتدائي", short:"خامس ابتدائي",  level:"primary", color:"#6bcb77" },
  { id:"p6", label:"الصف السادس الابتدائي", short:"سادس ابتدائي",  level:"primary", color:"#4d9de0" },
  { id:"m1", label:"الصف الأول الإعدادي",    short:"أول إعدادي",   level:"middle",  color:"#e15554" },
  { id:"m2", label:"الصف الثاني الإعدادي",   short:"ثاني إعدادي",  level:"middle",  color:"#e1bc29" },
  { id:"m3", label:"الصف الثالث الإعدادي",   short:"ثالث إعدادي",  level:"middle",  color:"#f7971e" },
];

/* ─── PDF.JS CDN ─── */
const PDFJS_CDN = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js";
const PDFJS_WORKER = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";

/* ─── CLAUDE API ─── */
async function callClaude(messages, systemPrompt = "") {
  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1000,
      system: systemPrompt,
      messages,
    }),
  });
  const data = await res.json();
  return data.content?.map(b => b.text || "").join("") || "";
}

/* ─── UTILS ─── */
function fileToBase64(file) {
  return new Promise((res, rej) => {
    const r = new FileReader();
    r.onload = () => res(r.result.split(",")[1]);
    r.onerror = rej;
    r.readAsDataURL(file);
  });
}

async function loadPdfJs() {
  if (window.pdfjsLib) return window.pdfjsLib;
  await new Promise((res, rej) => {
    const s = document.createElement("script");
    s.src = PDFJS_CDN;
    s.onload = res; s.onerror = rej;
    document.head.appendChild(s);
  });
  window.pdfjsLib.GlobalWorkerOptions.workerSrc = PDFJS_WORKER;
  return window.pdfjsLib;
}

async function renderPdfPage(pdfFile, pageNum) {
  const pdfjsLib = await loadPdfJs();
  const ab = await pdfFile.arrayBuffer();
  const pdf = await pdfjsLib.getDocument({ data: ab }).promise;
  if (pageNum < 1 || pageNum > pdf.numPages) return null;
  const page = await pdf.getPage(pageNum);
  const vp = page.getViewport({ scale: 1.8 });
  const canvas = document.createElement("canvas");
  canvas.width = vp.width;
  canvas.height = vp.height;
  await page.render({ canvasContext: canvas.getContext("2d"), viewport: vp }).promise;
  return { dataUrl: canvas.toDataURL("image/png"), totalPages: pdf.numPages };
}

async function extractPageText(pdfFile, pageNum) {
  const pdfjsLib = await loadPdfJs();
  const ab = await pdfFile.arrayBuffer();
  const pdf = await pdfjsLib.getDocument({ data: ab }).promise;
  if (pageNum < 1 || pageNum > pdf.numPages) return "";
  const page = await pdf.getPage(pageNum);
  const tc = await page.getTextContent();
  return tc.items.map(i => i.str).join(" ");
}

/* ════════════════════════════════════════════
   MAIN APP
════════════════════════════════════════════ */
export default function App() {
  const [view, setView] = useState("student"); // student | teacher
  const [files, setFiles] = useState({}); // { [gradeId]: { term1: {book, ref}, term2: {book, ref} } }

  return (
    <div dir="rtl" style={{ minHeight:"100vh", fontFamily:"'Cairo',sans-serif", background:"#0d1117" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
        *{box-sizing:border-box;margin:0;padding:0;}
        ::-webkit-scrollbar{width:6px;} ::-webkit-scrollbar-track{background:#161b22;} ::-webkit-scrollbar-thumb{background:#30363d;border-radius:3px;}
        .fade-in{animation:fadeIn .4s ease both;} @keyframes fadeIn{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
        .slide-in{animation:slideIn .3s ease both;} @keyframes slideIn{from{opacity:0;transform:translateX(20px)}to{opacity:1;transform:translateX(0)}}
        .pulse{animation:pulse 2s infinite;} @keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
        .btn{border:none;border-radius:12px;font-family:'Cairo',sans-serif;font-weight:700;cursor:pointer;transition:all .2s;display:inline-flex;align-items:center;gap:6px;}
        .btn:active{transform:scale(.97);}
        .btn-gold{background:linear-gradient(135deg,#f7971e,#ffd200);color:#1a1a1a;}
        .btn-gold:hover{box-shadow:0 6px 20px rgba(247,151,30,.4);transform:translateY(-1px);}
        .btn-teal{background:linear-gradient(135deg,#43cea2,#185a9d);color:#fff;}
        .btn-teal:hover{box-shadow:0 6px 20px rgba(67,206,162,.3);transform:translateY(-1px);}
        .btn-ghost{background:rgba(255,255,255,.08);color:#c9d1d9;border:1px solid rgba(255,255,255,.12);}
        .btn-ghost:hover{background:rgba(255,255,255,.14);}
        .card{background:#161b22;border:1px solid #30363d;border-radius:16px;}
        .grade-chip{padding:10px 16px;border-radius:10px;cursor:pointer;font-size:13px;font-weight:700;transition:all .2s;border:2px solid transparent;}
        .grade-chip:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,.3);}
        .q-item{padding:16px;border-radius:12px;cursor:pointer;transition:all .2s;border:1px solid #30363d;margin-bottom:8px;background:#0d1117;}
        .q-item:hover{border-color:#58a6ff;background:#161b22;}
        .q-item.active{border-color:#f7971e;background:#1a1500;}
        .bubble-btn{padding:8px 14px;border-radius:20px;font-size:13px;font-weight:700;border:none;cursor:pointer;transition:all .2s;font-family:'Cairo',sans-serif;}
        .bubble-btn:hover{transform:scale(1.05);}
        .tab-btn{padding:10px 20px;border-radius:10px;font-size:14px;font-weight:700;border:none;cursor:pointer;transition:all .2s;font-family:'Cairo',sans-serif;}
        .info-box{border-radius:12px;padding:14px 16px;margin-bottom:10px;}
        input[type=number]{background:#0d1117;border:1px solid #30363d;border-radius:10px;color:#e6edf3;font-family:'Cairo',sans-serif;font-size:20px;font-weight:700;padding:14px;width:100%;outline:none;text-align:center;transition:border .2s;}
        input[type=number]:focus{border-color:#f7971e;}
        select{background:#0d1117;border:1px solid #30363d;border-radius:10px;color:#e6edf3;font-family:'Cairo',sans-serif;font-size:14px;padding:10px 14px;outline:none;cursor:pointer;}
      `}</style>

      {/* TOP NAV */}
      <div style={{ background:"#161b22", borderBottom:"1px solid #30363d", padding:"14px 24px", display:"flex", alignItems:"center", justifyContent:"space-between", position:"sticky", top:0, zIndex:50 }}>
        <div style={{ display:"flex", alignItems:"center", gap:10 }}>
          <span style={{ fontSize:24 }}>📚</span>
          <div>
            <div style={{ color:"#e6edf3", fontWeight:900, fontSize:17 }}>معلمي الذكي</div>
            <div style={{ color:"#8b949e", fontSize:11 }}>منصة الحلول التعليمية المصرية</div>
          </div>
        </div>
        <div style={{ display:"flex", gap:8 }}>
          <button className={`tab-btn ${view==="student"?"btn-gold":"btn-ghost"}`} onClick={()=>setView("student")}>🎓 الطالب</button>
          <button className={`tab-btn ${view==="teacher"?"btn-gold":"btn-ghost"}`} onClick={()=>setView("teacher")}>🏫 المعلم</button>
        </div>
      </div>

      {view === "teacher"
        ? <TeacherPanel files={files} setFiles={setFiles} />
        : <StudentView files={files} />
      }
    </div>
  );
}

/* ════════════════════════════════════════════
   TEACHER PANEL
════════════════════════════════════════════ */
function TeacherPanel({ files, setFiles }) {
  const [selectedGrade, setSelectedGrade] = useState(null);
  const [selectedTerm, setSelectedTerm] = useState(1);
  const [uploadStatus, setUploadStatus] = useState("");

  const getFile = (gradeId, term, type) => files[gradeId]?.[`term${term}`]?.[type];

  const setFile = (gradeId, term, type, file) => {
    setFiles(prev => ({
      ...prev,
      [gradeId]: {
        ...prev[gradeId],
        [`term${term}`]: {
          ...(prev[gradeId]?.[`term${term}`] || {}),
          [type]: file,
        }
      }
    }));
    setUploadStatus(`✅ تم رفع ${type === "book" ? "كتاب التقييمات" : "مرجع الشرح"} بنجاح`);
    setTimeout(() => setUploadStatus(""), 3000);
  };

  const countUploaded = () => {
    let count = 0;
    GRADES.forEach(g => {
      [1,2].forEach(t => {
        if (files[g.id]?.[`term${t}`]?.book) count++;
        if (files[g.id]?.[`term${t}`]?.ref) count++;
      });
    });
    return count;
  };

  return (
    <div style={{ maxWidth:900, margin:"0 auto", padding:"24px 20px" }}>
      {/* Stats */}
      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:12, marginBottom:24 }} className="fade-in">
        {[
          { label:"إجمالي الصفوف", value: GRADES.length, icon:"🏫" },
          { label:"ملفات مرفوعة", value: countUploaded(), icon:"📂" },
          { label:"الترمان", value:"١ + ٢", icon:"📅" },
        ].map(s => (
          <div key={s.label} className="card" style={{ padding:20, textAlign:"center" }}>
            <div style={{ fontSize:28, marginBottom:6 }}>{s.icon}</div>
            <div style={{ fontSize:24, fontWeight:900, color:"#f7971e" }}>{s.value}</div>
            <div style={{ fontSize:12, color:"#8b949e", marginTop:2 }}>{s.label}</div>
          </div>
        ))}
      </div>

      {uploadStatus && (
        <div style={{ background:"rgba(67,206,162,.15)", border:"1px solid #43cea2", borderRadius:10, padding:"12px 16px", marginBottom:16, color:"#43cea2", fontWeight:700 }} className="fade-in">
          {uploadStatus}
        </div>
      )}

      <div style={{ display:"grid", gridTemplateColumns:"280px 1fr", gap:16 }}>
        {/* Grades list */}
        <div className="card" style={{ padding:16, height:"fit-content" }}>
          <div style={{ color:"#8b949e", fontSize:12, fontWeight:700, marginBottom:12 }}>اختر الصف</div>
          {["primary","middle"].map(level => (
            <div key={level} style={{ marginBottom:12 }}>
              <div style={{ fontSize:11, color: level==="primary"?"#43cea2":"#f7971e", fontWeight:700, marginBottom:8, paddingRight:4 }}>
                {level==="primary"?"▸ ابتدائي":"▸ إعدادي"}
              </div>
              {GRADES.filter(g=>g.level===level).map(g => {
                const t1b = !!files[g.id]?.term1?.book, t1r = !!files[g.id]?.term1?.ref;
                const t2b = !!files[g.id]?.term2?.book, t2r = !!files[g.id]?.term2?.ref;
                const total = [t1b,t1r,t2b,t2r].filter(Boolean).length;
                return (
                  <div key={g.id}
                    onClick={() => setSelectedGrade(g)}
                    style={{
                      padding:"10px 12px", borderRadius:10, cursor:"pointer", marginBottom:4,
                      background: selectedGrade?.id===g.id ? `${g.color}22` : "transparent",
                      border: selectedGrade?.id===g.id ? `1px solid ${g.color}` : "1px solid transparent",
                      transition:"all .2s"
                    }}>
                    <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center" }}>
                      <span style={{ fontSize:13, color:"#e6edf3", fontWeight:600 }}>{g.short}</span>
                      <span style={{ fontSize:11, background: total===4?"rgba(67,206,162,.2)":"rgba(255,255,255,.08)", color: total===4?"#43cea2":"#8b949e", padding:"2px 8px", borderRadius:20, fontWeight:700 }}>
                        {total}/٤
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          ))}
        </div>

        {/* Upload panel */}
        <div>
          {selectedGrade ? (
            <div className="card fade-in" style={{ padding:24 }}>
              <div style={{ display:"flex", alignItems:"center", gap:12, marginBottom:20 }}>
                <div style={{ width:40, height:40, borderRadius:10, background:`${selectedGrade.color}22`, display:"flex", alignItems:"center", justifyContent:"center", fontSize:20 }}>📖</div>
                <div>
                  <div style={{ color:"#e6edf3", fontWeight:900, fontSize:16 }}>{selectedGrade.label}</div>
                  <div style={{ color:"#8b949e", fontSize:12 }}>رفع ملفات PDF للترمين</div>
                </div>
              </div>

              {/* Term tabs */}
              <div style={{ display:"flex", gap:8, marginBottom:20 }}>
                {[1,2].map(t => (
                  <button key={t} className={`tab-btn ${selectedTerm===t?"btn-gold":"btn-ghost"}`} onClick={()=>setSelectedTerm(t)}>
                    الترم {t===1?"الأول":"الثاني"}
                  </button>
                ))}
              </div>

              {/* Upload cards */}
              {[
                { type:"book", icon:"📋", title:"ملف التقييمات", desc:"الكتاب الذي يحتوي على الأسئلة — ستُعرض صفحاته للطالب" },
                { type:"ref",  icon:"📖", title:"مرجع الشرح",    desc:"كتاب الحلول والشرح — يستخدمه الذكاء الاصطناعي للإجابة" },
              ].map(({ type, icon, title, desc }) => {
                const file = getFile(selectedGrade.id, selectedTerm, type);
                const inputRef = React.createRef();
                return (
                  <div key={type} className="card" style={{ padding:18, marginBottom:12, border:`1px solid ${file?"#43cea2":"#30363d"}` }}>
                    <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start" }}>
                      <div style={{ display:"flex", gap:12, alignItems:"flex-start" }}>
                        <span style={{ fontSize:24 }}>{icon}</span>
                        <div>
                          <div style={{ color:"#e6edf3", fontWeight:700, marginBottom:3 }}>{title}</div>
                          <div style={{ color:"#8b949e", fontSize:12, lineHeight:1.6 }}>{desc}</div>
                          {file && <div style={{ color:"#43cea2", fontSize:12, marginTop:6, fontWeight:600 }}>✅ {file.name}</div>}
                        </div>
                      </div>
                      <div>
                        <input type="file" accept=".pdf" ref={inputRef} style={{display:"none"}} onChange={e => { if(e.target.files[0]) setFile(selectedGrade.id, selectedTerm, type, e.target.files[0]); }} />
                        <button className={`btn ${file?"btn-ghost":"btn-teal"}`} style={{ padding:"8px 16px", fontSize:13 }} onClick={()=>inputRef.current.click()}>
                          {file ? "🔄 تغيير" : "➕ رفع"}
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="card" style={{ padding:40, textAlign:"center", color:"#8b949e" }}>
              <div style={{ fontSize:48, marginBottom:12 }}>👈</div>
              <div style={{ fontWeight:700, fontSize:15 }}>اختر صفاً من القائمة لرفع ملفاته</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/* ════════════════════════════════════════════
   STUDENT VIEW
════════════════════════════════════════════ */
function StudentView({ files }) {
  const [step, setStep] = useState("term");       // term | grade | viewer
  const [term, setTerm] = useState(null);
  const [grade, setGrade] = useState(null);
  const [pageNum, setPageNum] = useState("");
  const [pageData, setPageData] = useState(null); // { dataUrl, totalPages }
  const [pageLoading, setPageLoading] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [qLoading, setQLoading] = useState(false);
  const [activeQ, setActiveQ] = useState(null);
  const [answerData, setAnswerData] = useState({}); // { [qIndex]: { answer, explain } }
  const [loadingBubble, setLoadingBubble] = useState(null); // { qIdx, type }
  const [openBubble, setOpenBubble] = useState(null); // { qIdx, type }

  const termKey = `term${term}`;
  const gradeFiles = grade ? files[grade.id]?.[termKey] : null;
  const bookFile = gradeFiles?.book;
  const refFile  = gradeFiles?.ref;

  const reset = () => {
    setStep("term"); setTerm(null); setGrade(null); setPageNum(""); setPageData(null);
    setQuestions([]); setActiveQ(null); setAnswerData({}); setOpenBubble(null);
  };

  /* Load page image */
  const loadPage = async () => {
    if (!bookFile || !pageNum) return;
    setPageLoading(true);
    setQuestions([]); setActiveQ(null); setAnswerData({}); setOpenBubble(null);
    try {
      const result = await renderPdfPage(bookFile, parseInt(pageNum));
      if (!result) { alert("رقم الصفحة غير موجود في الملف!"); setPageLoading(false); return; }
      setPageData(result);
      setStep("viewer");
      extractQuestions(parseInt(pageNum));
    } catch(e) { console.error(e); alert("حدث خطأ في تحميل الصفحة"); }
    setPageLoading(false);
  };

  /* Extract questions via AI */
  const extractQuestions = async (pn) => {
    if (!bookFile) return;
    setQLoading(true);
    try {
      const text = await extractPageText(bookFile, pn);
      if (!text.trim()) { setQuestions([]); setQLoading(false); return; }

      const response = await callClaude([
        { role:"user", content:`النص التالي مأخوذ من صفحة كتاب تقييمات مدرسي مصري. استخرج جميع الأسئلة منه فقط، وأعدها كـ JSON array من الكائنات { "id": رقم, "text": "نص السؤال" }. أعد JSON فقط بدون أي نص إضافي.\n\nالنص:\n${text.substring(0,3000)}`}
      ], "أنت مساعد تعليمي متخصص في المناهج المصرية. أجب دائماً بـ JSON صحيح فقط.");

      const clean = response.replace(/```json|```/g,"").trim();
      const parsed = JSON.parse(clean);
      setQuestions(Array.isArray(parsed) ? parsed : []);
    } catch(e) {
      console.error("Q extraction error:", e);
      setQuestions([]);
    }
    setQLoading(false);
  };

  /* Get answer/explanation for a question */
  const getAIResponse = async (qIdx, type) => {
    const q = questions[qIdx];
    if (!q) return;
    const key = `${qIdx}-${type}`;
    if (answerData[key]) { setOpenBubble({qIdx,type}); return; }

    setLoadingBubble({qIdx,type});
    try {
      let refText = "";
      if (refFile) {
        try {
          const pn = parseInt(pageNum);
          const pages = [pn-1, pn, pn+1].filter(p=>p>0);
          for (const p of pages) {
            const t = await extractPageText(refFile, p);
            refText += t + " ";
            if (refText.length > 4000) break;
          }
        } catch(e) { console.warn("ref read error", e); }
      }

      const systemPrompt = `أنت مدرس مصري محترف متخصص في المناهج المصرية للمراحل الابتدائية والإعدادية. أجب بالعربية الفصحى البسيطة المناسبة لمستوى الطالب.`;

      const userMsg = type === "answer"
        ? `السؤال: ${q.text}\n\n${refText ? `معلومات من مرجع الشرح:\n${refText.substring(0,2000)}\n\n` : ""}أعطني الإجابة الصحيحة فقط في جملة أو جملتين، بدون شرح.`
        : `السؤال: ${q.text}\n\n${refText ? `معلومات من مرجع الشرح:\n${refText.substring(0,2000)}\n\n` : ""}اشرح الإجابة بطريقة مبسطة ومفيدة للطالب مع ذكر السبب أو التحليل.`;

      const result = await callClaude([{ role:"user", content:userMsg }], systemPrompt);
      setAnswerData(prev => ({ ...prev, [key]: result }));
      setOpenBubble({qIdx,type});
    } catch(e) {
      console.error(e);
      setAnswerData(prev => ({ ...prev, [`${qIdx}-${type}`]: "حدث خطأ، يرجى المحاولة مرة أخرى" }));
      setOpenBubble({qIdx,type});
    }
    setLoadingBubble(null);
  };

  const toggleBubble = (qIdx, type) => {
    if (openBubble?.qIdx===qIdx && openBubble?.type===type) {
      setOpenBubble(nul
