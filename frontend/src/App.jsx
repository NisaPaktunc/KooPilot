import { useState, useRef, useEffect } from "react"
import AdminDashboard from "./pages/AdminDashboard"

const API = "http://127.0.0.1:8000"

// Hangi sayfayı göster
const page =
  new URLSearchParams(window.location.search).get("page") === "admin"
    ? "admin"
    : "chat"

// ── Tool badge etiketleri ─────────────────────────────────────────────────────
const TOOL_LABELS = {
  check_stock:               "📊 Stok kontrol edildi",
  get_order_status:          "📦 Sipariş sorgulandı",
  get_cargo_status:          "🚚 Kargo takip edildi",
  send_manager_notification: "🔔 Yönetici bilgilendirildi",
  get_daily_summary:         "📈 Günlük özet alındı",
}

// ── Müşteri Chat ──────────────────────────────────────────────────────────────
function CustomerChat() {
  const [messages, setMessages]   = useState([])
  const [input, setInput]         = useState("")
  const [loading, setLoading]     = useState(false)
  const [toolCalls, setToolCalls] = useState([])
  const sessionId                 = useRef("session-" + Date.now())
  const bottomRef                 = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, loading, toolCalls])

  const sendMessage = async () => {
    const text = input.trim()
    if (!text || loading) return

    setInput("")
    setMessages(m => [...m, { sender: "user", text }])
    setLoading(true)
    setToolCalls([])

    try {
      const res  = await fetch(`${API}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, session_id: sessionId.current }),
      })
      const data = await res.json()

      if (data.session_id) sessionId.current = data.session_id
      setToolCalls(data.tools_used || [])
      setMessages(m => [...m, {
        sender:    "bot",
        text:      data.response,
        toolsUsed: data.tools_used || [],
      }])
    } catch {
      setMessages(m => [...m, { sender: "bot", text: "⚠️ Backend bağlantı hatası." }])
    } finally {
      setLoading(false)
    }
  }

  const SUGGESTIONS = [
    "ORD-128 nerede?",
    "Organik Bal var mı?",
    "Domates stoğu nedir?",
    "Bugünkü sipariş durumu",
    "ORD-132 kargo durumu",
  ]

  return (
    <div style={S.container}>
      {/* Header */}
      <div style={S.header}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={S.logo}>K</div>
          <div>
            <h1 style={S.title}>Koopilot</h1>
            <span style={S.subtitle}>AI Destekli Operasyon Asistanı</span>
          </div>
        </div>
        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <div style={S.statusBadge}>
            <span style={S.statusDot} />
            Gemini AI Aktif
          </div>
          <a href="/?page=admin" style={{
            background: "#21262d", border: "1px solid #30363d",
            borderRadius: 8, padding: "6px 14px", color: "#c9d1d9",
            textDecoration: "none", fontSize: 12,
          }}>
            📊 Yönetici Paneli
          </a>
        </div>
      </div>

      {/* Mesajlar */}
      <div style={S.messagesArea}>
        {messages.length === 0 && (
          <div style={S.emptyState}>
            <div style={{ fontSize: "3rem", marginBottom: 8 }}>🤖</div>
            <p style={{ fontSize: "1.2rem", color: "#c9d1d9", fontWeight: 500 }}>
              Merhaba! Ben Koopilot.
            </p>
            <p style={{ fontSize: "0.9rem", color: "#8b949e", marginBottom: 16 }}>
              Sipariş, stok ve kargo sorularınızı yanıtlıyorum.
            </p>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", justifyContent: "center" }}>
              {SUGGESTIONS.map(s => (
                <button key={s} onClick={() => setInput(s)} style={S.chip}>{s}</button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} style={{
            ...S.row,
            justifyContent: msg.sender === "user" ? "flex-end" : "flex-start",
          }}>
            {msg.sender === "bot" && <div style={S.avatar}>K</div>}
            <div style={{
              ...S.bubble,
              ...(msg.sender === "user" ? S.userBubble : S.botBubble),
            }}>
              <div style={S.senderLabel}>
                {msg.sender === "user" ? "Sen" : "Koopilot"}
              </div>
              <div style={{ fontSize: "0.95rem", whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
                {msg.text}
              </div>
              {/* Kullanılan tool'lar */}
              {msg.toolsUsed?.length > 0 && (
                <div style={{ marginTop: 8, display: "flex", gap: 6, flexWrap: "wrap" }}>
                  {msg.toolsUsed.map((t, j) => (
                    <span key={j} style={S.toolBadge}>
                      {TOOL_LABELS[t] || `🔧 ${t}`}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Yükleniyor */}
        {loading && (
          <div style={{ ...S.row, justifyContent: "flex-start" }}>
            <div style={S.avatar}>K</div>
            <div style={{ ...S.bubble, ...S.botBubble }}>
              <div style={S.senderLabel}>Koopilot</div>
              {/* Agent thinking göstergesi */}
              {toolCalls.length === 0 ? (
                <div style={{ display: "flex", gap: 4, alignItems: "center",
                  fontSize: 12, color: "#8b949e" }}>
                  <span>🤔 Düşünüyor</span>
                  <span style={S.dot}>●</span>
                  <span style={{ ...S.dot, animationDelay: "0.2s" }}>●</span>
                  <span style={{ ...S.dot, animationDelay: "0.4s" }}>●</span>
                </div>
              ) : (
                <div>
                  {toolCalls.map((t, i) => (
                    <div key={i} style={{
                      fontSize: 12, color: "#7c6af7",
                      background: "rgba(124,106,247,0.1)",
                      border: "1px solid rgba(124,106,247,0.2)",
                      borderRadius: 6, padding: "3px 10px",
                      marginBottom: 4, display: "inline-block",
                    }}>
                      {TOOL_LABELS[t] || `🔧 ${t}`}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={S.inputArea}>
        <div style={S.inputWrapper}>
          <input
            style={S.input}
            placeholder="Mesajınızı yazın... (örn: ORD-128 nerede?)"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && !e.shiftKey && sendMessage()}
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || loading}
            style={{
              ...S.sendBtn,
              opacity: !input.trim() || loading ? 0.5 : 1,
              cursor: !input.trim() || loading ? "not-allowed" : "pointer",
            }}
          >
            Gönder
          </button>
        </div>
        {/* Öneri chips — her zaman göster */}
        {messages.length > 0 && (
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 8, maxWidth: 860, margin: "8px auto 0" }}>
            {SUGGESTIONS.map(s => (
              <button key={s} onClick={() => setInput(s)} style={S.chip}>{s}</button>
            ))}
          </div>
        )}
      </div>

      <style>{`@keyframes blink { 0%,100%{opacity:.2} 50%{opacity:1} }`}</style>
    </div>
  )
}

// ── Styles ────────────────────────────────────────────────────────────────────
const S = {
  container: {
    display: "flex", flexDirection: "column", height: "100vh",
    fontFamily: "'Segoe UI', system-ui, -apple-system, sans-serif",
    backgroundColor: "#0f1117", color: "#e1e4e8",
  },
  header: {
    display: "flex", alignItems: "center", justifyContent: "space-between",
    padding: "14px 24px", borderBottom: "1px solid #21262d",
    backgroundColor: "#161b22",
  },
  logo: {
    width: 38, height: 38, borderRadius: 10,
    background: "linear-gradient(135deg,#7c6af7,#3de6c0)",
    display: "flex", alignItems: "center", justifyContent: "center",
    fontSize: "1.1rem", fontWeight: 800, color: "#fff",
  },
  title: {
    margin: 0, fontSize: "1.25rem", fontWeight: 700,
    background: "linear-gradient(135deg,#7c6af7,#3de6c0)",
    WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
  },
  subtitle: { fontSize: "0.75rem", color: "#8b949e" },
  statusBadge: {
    display: "flex", alignItems: "center", gap: 6, fontSize: "0.75rem",
    color: "#7ee787", background: "rgba(126,231,135,0.1)",
    padding: "5px 12px", borderRadius: 20,
    border: "1px solid rgba(126,231,135,0.2)",
  },
  statusDot: {
    width: 6, height: 6, borderRadius: "50%",
    backgroundColor: "#7ee787", display: "inline-block",
  },
  messagesArea: {
    flex: 1, overflowY: "auto", padding: "20px 24px",
    display: "flex", flexDirection: "column", gap: 12,
  },
  emptyState: {
    flex: 1, display: "flex", flexDirection: "column",
    alignItems: "center", justifyContent: "center", gap: 6,
  },
  row: { display: "flex", alignItems: "flex-start", gap: 10 },
  avatar: {
    width: 30, height: 30, borderRadius: "50%",
    background: "linear-gradient(135deg,#7c6af7,#3de6c0)",
    display: "flex", alignItems: "center", justifyContent: "center",
    fontSize: "0.8rem", fontWeight: 700, color: "#fff",
    flexShrink: 0, marginTop: 4,
  },
  bubble: { maxWidth: "72%", padding: "10px 14px", borderRadius: 12, lineHeight: 1.5 },
  userBubble: { background: "#1f6feb", borderBottomRightRadius: 4 },
  botBubble: {
    background: "#21262d", borderBottomLeftRadius: 4,
    border: "1px solid #30363d",
  },
  senderLabel: {
    fontSize: "0.68rem", fontWeight: 600, marginBottom: 4,
    opacity: 0.65, textTransform: "uppercase", letterSpacing: "0.5px",
  },
  toolBadge: {
    fontSize: "0.7rem", padding: "2px 8px", borderRadius: 12,
    background: "rgba(124,106,247,0.12)", color: "#a08af5",
    border: "1px solid rgba(124,106,247,0.2)",
  },
  chip: {
    padding: "5px 12px", borderRadius: 20, fontSize: "0.8rem",
    border: "1px solid #30363d", background: "#21262d",
    color: "#c9d1d9", cursor: "pointer",
  },
  dot: {
    fontSize: "0.6rem", color: "#8b949e",
    animation: "blink 1.4s infinite", display: "inline-block",
  },
  inputArea: {
    padding: "14px 24px", borderTop: "1px solid #21262d",
    backgroundColor: "#161b22",
  },
  inputWrapper: { display: "flex", gap: 10, maxWidth: 860, margin: "0 auto" },
  input: {
    flex: 1, padding: "11px 16px", borderRadius: 10,
    border: "1px solid #30363d", background: "#0d1117",
    color: "#e1e4e8", fontSize: "0.95rem", outline: "none",
  },
  sendBtn: {
    padding: "11px 24px", borderRadius: 10, border: "none",
    background: "linear-gradient(135deg,#7c6af7,#3de6c0)",
    color: "#fff", fontSize: "0.95rem", fontWeight: 600,
    transition: "opacity 0.15s",
  },
}

// ── Router ────────────────────────────────────────────────────────────────────
export default function App() {
  if (page === "admin") return <AdminDashboard />
  return <CustomerChat />
}
