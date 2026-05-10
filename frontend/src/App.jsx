import { useState, useRef, useEffect } from "react"

const API_URL = "http://127.0.0.1:8000"

function App() {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    const trimmed = inputMessage.trim()
    if (!trimmed || isLoading) return

    const userMsg = { sender: "user", text: trimmed }
    setMessages((prev) => [...prev, userMsg])
    setInputMessage("")
    setIsLoading(true)

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: trimmed,
          session_id: sessionId,
        }),
      })
      const data = await res.json()

      // Session ID'yi sakla
      if (data.session_id) {
        setSessionId(data.session_id)
      }

      const botMsg = {
        sender: "bot",
        text: data.response,
        toolsUsed: data.tools_used || [],
      }
      setMessages((prev) => [...prev, botMsg])
    } catch (err) {
      console.error("Chat error:", err)
      const errorMsg = { sender: "bot", text: "⚠️ Backend bağlantı hatası." }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.headerLeft}>
          <div style={styles.logoCircle}>K</div>
          <div>
            <h1 style={styles.title}>Koopilot</h1>
            <span style={styles.subtitle}>AI Destekli Operasyon Asistanı</span>
          </div>
        </div>
        <div style={styles.statusBadge}>
          <span style={styles.statusDot}></span>
          Claude AI Aktif
        </div>
      </div>

      {/* Messages Area */}
      <div style={styles.messagesArea}>
        {messages.length === 0 && (
          <div style={styles.emptyState}>
            <div style={styles.emptyIcon}>🤖</div>
            <p style={styles.emptyText}>Merhaba! Ben Koopilot.</p>
            <p style={styles.emptyHint}>
              Stok sorgulamak için bir mesaj yazın.
            </p>
            <div style={styles.suggestionsRow}>
              {[
                "Domates stokta var mı?",
                "Biber stok durumu nedir?",
                "Salatalık kaldı mı?",
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  style={styles.suggestionChip}
                  onClick={() => {
                    setInputMessage(suggestion)
                  }}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              ...styles.messageBubbleRow,
              justifyContent: msg.sender === "user" ? "flex-end" : "flex-start",
            }}
          >
            {msg.sender === "bot" && <div style={styles.botAvatar}>K</div>}
            <div
              style={{
                ...styles.bubble,
                ...(msg.sender === "user" ? styles.userBubble : styles.botBubble),
              }}
            >
              <div style={styles.senderLabel}>
                {msg.sender === "user" ? "Sen" : "Koopilot"}
              </div>
              <div style={styles.messageText}>{msg.text}</div>
              {/* Tool kullanım bilgisi */}
              {msg.toolsUsed && msg.toolsUsed.length > 0 && (
                <div style={styles.toolBadgeRow}>
                  {msg.toolsUsed.map((tool, j) => (
                    <span key={j} style={styles.toolBadge}>
                      🔧 {tool}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div style={{ ...styles.messageBubbleRow, justifyContent: "flex-start" }}>
            <div style={styles.botAvatar}>K</div>
            <div style={{ ...styles.bubble, ...styles.botBubble }}>
              <div style={styles.senderLabel}>Koopilot</div>
              <div style={styles.typingDots}>
                <span style={styles.dot}>●</span>
                <span style={{ ...styles.dot, animationDelay: "0.2s" }}>●</span>
                <span style={{ ...styles.dot, animationDelay: "0.4s" }}>●</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div style={styles.inputArea}>
        <div style={styles.inputWrapper}>
          <input
            id="chat-input"
            type="text"
            style={styles.input}
            placeholder="Mesajınızı yazın... (örn: Domates stokta var mı?)"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
          />
          <button
            id="send-button"
            style={{
              ...styles.sendButton,
              opacity: !inputMessage.trim() || isLoading ? 0.5 : 1,
              cursor: !inputMessage.trim() || isLoading ? "not-allowed" : "pointer",
            }}
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
          >
            Gönder
          </button>
        </div>
      </div>

      {/* Typing animation keyframes injected via style tag */}
      <style>{`
        @keyframes blink {
          0%, 20% { opacity: 0.2; }
          50% { opacity: 1; }
          100% { opacity: 0.2; }
        }
      `}</style>
    </div>
  )
}

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    height: "100vh",
    fontFamily: "'Segoe UI', system-ui, -apple-system, sans-serif",
    backgroundColor: "#0f1117",
    color: "#e1e4e8",
  },
  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "16px 24px",
    borderBottom: "1px solid #21262d",
    backgroundColor: "#161b22",
  },
  headerLeft: {
    display: "flex",
    alignItems: "center",
    gap: "14px",
  },
  logoCircle: {
    width: "40px",
    height: "40px",
    borderRadius: "12px",
    background: "linear-gradient(135deg, #58a6ff, #bc8cff)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "1.1rem",
    fontWeight: 800,
    color: "#fff",
  },
  title: {
    margin: 0,
    fontSize: "1.3rem",
    fontWeight: 700,
    background: "linear-gradient(135deg, #58a6ff, #bc8cff)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
  },
  subtitle: {
    fontSize: "0.75rem",
    color: "#8b949e",
  },
  statusBadge: {
    display: "flex",
    alignItems: "center",
    gap: "6px",
    fontSize: "0.75rem",
    color: "#7ee787",
    backgroundColor: "rgba(126, 231, 135, 0.1)",
    padding: "6px 12px",
    borderRadius: "20px",
    border: "1px solid rgba(126, 231, 135, 0.2)",
  },
  statusDot: {
    width: "6px",
    height: "6px",
    borderRadius: "50%",
    backgroundColor: "#7ee787",
  },
  messagesArea: {
    flex: 1,
    overflowY: "auto",
    padding: "24px",
    display: "flex",
    flexDirection: "column",
    gap: "12px",
  },
  emptyState: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    gap: "8px",
  },
  emptyIcon: {
    fontSize: "3rem",
    marginBottom: "8px",
  },
  emptyText: {
    fontSize: "1.2rem",
    color: "#c9d1d9",
    fontWeight: 500,
  },
  emptyHint: {
    fontSize: "0.9rem",
    color: "#8b949e",
    marginBottom: "16px",
  },
  suggestionsRow: {
    display: "flex",
    gap: "8px",
    flexWrap: "wrap",
    justifyContent: "center",
  },
  suggestionChip: {
    padding: "8px 16px",
    borderRadius: "20px",
    border: "1px solid #30363d",
    backgroundColor: "#21262d",
    color: "#c9d1d9",
    fontSize: "0.85rem",
    cursor: "pointer",
    transition: "all 0.2s",
  },
  messageBubbleRow: {
    display: "flex",
    alignItems: "flex-start",
    gap: "10px",
  },
  botAvatar: {
    width: "32px",
    height: "32px",
    borderRadius: "50%",
    background: "linear-gradient(135deg, #58a6ff, #bc8cff)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "0.85rem",
    fontWeight: 700,
    color: "#fff",
    flexShrink: 0,
    marginTop: "4px",
  },
  bubble: {
    maxWidth: "70%",
    padding: "10px 14px",
    borderRadius: "12px",
    lineHeight: 1.5,
  },
  userBubble: {
    backgroundColor: "#1f6feb",
    borderBottomRightRadius: "4px",
  },
  botBubble: {
    backgroundColor: "#21262d",
    borderBottomLeftRadius: "4px",
    border: "1px solid #30363d",
  },
  senderLabel: {
    fontSize: "0.7rem",
    fontWeight: 600,
    marginBottom: "4px",
    opacity: 0.7,
    textTransform: "uppercase",
    letterSpacing: "0.5px",
  },
  messageText: {
    fontSize: "0.95rem",
    wordBreak: "break-word",
    whiteSpace: "pre-wrap",
  },
  toolBadgeRow: {
    display: "flex",
    gap: "6px",
    marginTop: "8px",
    flexWrap: "wrap",
  },
  toolBadge: {
    fontSize: "0.7rem",
    padding: "3px 8px",
    borderRadius: "12px",
    backgroundColor: "rgba(88, 166, 255, 0.15)",
    color: "#58a6ff",
    border: "1px solid rgba(88, 166, 255, 0.25)",
  },
  typingDots: {
    display: "flex",
    gap: "4px",
    padding: "4px 0",
  },
  dot: {
    fontSize: "0.7rem",
    color: "#8b949e",
    animation: "blink 1.4s infinite",
  },
  inputArea: {
    padding: "16px 24px",
    borderTop: "1px solid #21262d",
    backgroundColor: "#161b22",
  },
  inputWrapper: {
    display: "flex",
    gap: "10px",
    maxWidth: "900px",
    margin: "0 auto",
  },
  input: {
    flex: 1,
    padding: "12px 16px",
    borderRadius: "10px",
    border: "1px solid #30363d",
    backgroundColor: "#0d1117",
    color: "#e1e4e8",
    fontSize: "0.95rem",
    outline: "none",
    transition: "border-color 0.2s",
  },
  sendButton: {
    padding: "12px 24px",
    borderRadius: "10px",
    border: "none",
    background: "linear-gradient(135deg, #1f6feb, #8b5cf6)",
    color: "#fff",
    fontSize: "0.95rem",
    fontWeight: 600,
    transition: "opacity 0.2s, transform 0.1s",
  },
}

export default App
