import { useState, useRef, useEffect } from "react"
import Markdown from "react-markdown"
import remarkGfm from "remark-gfm"
import AdminDashboard from "./pages/AdminDashboard"
import "./index.css"

const API = "http://127.0.0.1:8000"
const page = new URLSearchParams(window.location.search).get("page") === "admin" ? "admin" : "chat"

const TOOL_LABELS = {
  check_stock:               "Stok kontrol edildi",
  get_order_status:          "Sipariş sorgulandı",
  get_cargo_status:          "Kargo takip edildi",
  send_manager_notification: "Yönetici bilgilendirildi",
  get_daily_summary:         "Günlük özet alındı",
  list_all_products:         "Ürünler listelendi",
  get_sales_analytics:       "Satış analizi yapıldı",
  get_stock_forecast:        "Stok tahmini yapıldı",
  run_smart_analysis:        "Akıllı analiz yapıldı",
}

const STORAGE_SESSION = "koopilot_session_id"
const STORAGE_MSGS    = "koopilot_messages"

function loadSession() {
  try {
    const sid = localStorage.getItem(STORAGE_SESSION)
    const msgs = localStorage.getItem(STORAGE_MSGS)
    return { sessionId: sid || "session-" + Date.now(), messages: msgs ? JSON.parse(msgs) : [] }
  } catch { return { sessionId: "session-" + Date.now(), messages: [] } }
}
function saveSession(sid, msgs) {
  try { localStorage.setItem(STORAGE_SESSION, sid); localStorage.setItem(STORAGE_MSGS, JSON.stringify(msgs)) } catch {}
}

const SUGGESTIONS = [
  "ORD-128 nerede?", "Organik Bal var mı?", "Domates stoğu nedir?",
  "Bugünkü sipariş durumu", "Satış analizi göster",
  "Hangi ürünler tükenecek?", "Sebze kategorisindeki ürünler",
]

/* ── SVG icons (inline, no dependency needed) ─────────────────────────── */
const Icon = {
  Sparkles: () => <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>,
  Send: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m22 2-7 20-4-9-9-4z"/><path d="M22 2 11 13"/></svg>,
  Bot: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg>,
  User: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>,
  Plus: () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>,
  Layout: () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="14" y="3" rx="1"/><rect width="7" height="7" x="14" y="14" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/></svg>,
  MsgSquare: () => <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>,
}

function ChatMarkdown({ content }) {
  return (
    <Markdown remarkPlugins={[remarkGfm]} components={{
      p: ({ children }) => <p>{children}</p>,
      strong: ({ children }) => <strong>{children}</strong>,
      code: ({ children, inline }) => inline !== false
        ? <code>{children}</code>
        : <pre><code>{children}</code></pre>,
      table: ({ children }) => <table>{children}</table>,
      th: ({ children }) => <th>{children}</th>,
      td: ({ children }) => <td>{children}</td>,
    }}>{content}</Markdown>
  )
}

function CustomerChat() {
  const stored = useRef(loadSession())
  const [messages, setMessages] = useState(stored.current.messages)
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [toolCalls, setToolCalls] = useState([])
  const sessionId = useRef(stored.current.sessionId)
  const bottomRef = useRef(null)

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }) }, [messages, loading])
  useEffect(() => { saveSession(sessionId.current, messages) }, [messages])

  const startNew = () => { const s = "session-" + Date.now(); sessionId.current = s; setMessages([]); setInput(""); saveSession(s, []) }

  const send = async (text) => {
    const t = (text || input).trim(); if (!t || loading) return
    setInput(""); setMessages(m => [...m, { sender: "user", text: t }]); setLoading(true); setToolCalls([])
    try {
      const res = await fetch(`${API}/chat`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message: t, session_id: sessionId.current }) })
      const data = await res.json()
      if (data.session_id) sessionId.current = data.session_id
      setToolCalls(data.tools_used || [])
      setMessages(m => [...m, { sender: "bot", text: data.response, toolsUsed: data.tools_used || [] }])
    } catch { setMessages(m => [...m, { sender: "bot", text: "Bağlantı hatası. Backend çalışıyor mu?" }]) }
    finally { setLoading(false) }
  }

  return (
    <div className="chat-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1>Koopilot AI</h1>
          <p>Gemini destekli operasyon asistanı</p>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div className="ai-badge"><span className="ai-badge-dot" /> AI Aktif</div>
          <button className="btn-secondary" onClick={startNew}><Icon.Plus /> Yeni Sohbet</button>
          <a href="/?page=admin" className="btn-secondary" style={{ textDecoration: "none" }}><Icon.Layout /> Yönetici Paneli</a>
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-empty">
            <div className="chat-empty-icon"><Icon.Sparkles /></div>
            <h2>Merhaba! Ben Koopilot.</h2>
            <p>Sipariş, stok, kargo ve satış analizi sorularınızı yanıtlıyorum.</p>
            <div className="chat-chips">
              {SUGGESTIONS.map(s => <button key={s} className="chip" onClick={() => send(s)}>{s}</button>)}
            </div>
          </div>
        ) : (
          <div className="chat-thread">
            {messages.map((msg, i) => (
              <div key={i} className={`chat-row ${msg.sender}`}>
                <div className={`chat-avatar ${msg.sender === "user" ? "user" : "bot"}`}>
                  {msg.sender === "user" ? <Icon.User /> : <Icon.Bot />}
                </div>
                <div className={`chat-bubble ${msg.sender === "user" ? "user" : "bot"}`}>
                  {msg.sender === "bot" ? <ChatMarkdown content={msg.text} /> : msg.text}
                  {msg.toolsUsed?.length > 0 && (
                    <div style={{ marginTop: 8, display: "flex", gap: 6, flexWrap: "wrap" }}>
                      {msg.toolsUsed.map((t, j) => <span key={j} className="tool-badge">{TOOL_LABELS[t] || t}</span>)}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="chat-row">
                <div className="chat-avatar bot"><Icon.Bot /></div>
                <div className="chat-bubble bot">
                  {toolCalls.length === 0
                    ? <span style={{ fontSize: 13, color: "var(--muted)", display: "flex", gap: 4, alignItems: "center" }}>
                        Düşünüyor <span className="dot">●</span><span className="dot" style={{animationDelay:"0.2s"}}>●</span><span className="dot" style={{animationDelay:"0.4s"}}>●</span>
                      </span>
                    : <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                        {toolCalls.map((t, i) => <span key={i} className="tool-badge">{TOOL_LABELS[t] || t}</span>)}
                      </div>
                  }
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <div className="chat-input-area">
        <form className="chat-input-form" onSubmit={e => { e.preventDefault(); send() }}>
          <input className="input" style={{ flex: 1 }} value={input} onChange={e => setInput(e.target.value)} placeholder="Mesajınızı yazın… (örn: ORD-128 nerede?)" disabled={loading} />
          <button className="btn-primary" type="submit" disabled={!input.trim() || loading}><Icon.Send /> Gönder</button>
        </form>
        {messages.length > 0 && (
          <div className="chat-chips" style={{ marginTop: 12 }}>
            {SUGGESTIONS.map(s => <button key={s} className="chip" onClick={() => send(s)}>{s}</button>)}
          </div>
        )}
      </div>
    </div>
  )
}

export default function App() {
  if (page === "admin") return <AdminDashboard />
  return <CustomerChat />
}
