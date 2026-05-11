import { useState, useEffect } from "react"
import { useNotifications } from "../hooks/useNotifications"

const API = "http://127.0.0.1:8000"

// ── Renk yardımcıları ─────────────────────────────────────────────────────────

const STATUS_LABEL = {
  beklemede:      { label: "Beklemede",      color: "#f7a26a", bg: "rgba(247,162,106,0.12)" },
  hazirlaniyor:   { label: "Hazırlanıyor",   color: "#58a6ff", bg: "rgba(88,166,255,0.12)"  },
  kargoda:        { label: "Kargoda 🚚",     color: "#3de6c0", bg: "rgba(61,230,192,0.12)"  },
  teslim_edildi:  { label: "Teslim Edildi ✅",color: "#7ee787", bg: "rgba(126,231,135,0.12)" },
  iptal:          { label: "İptal ❌",        color: "#f76a8a", bg: "rgba(247,106,138,0.12)" },
}

const PRIORITY_COLOR = {
  dusuk:   "#7ee787",
  orta:    "#58a6ff",
  yuksek:  "#f7a26a",
  kritik:  "#f76a8a",
}

// ── Alt bileşenler ────────────────────────────────────────────────────────────

function SummaryCard({ icon, label, value, color, sub }) {
  return (
    <div style={{
      background: "#161b22",
      border: `1px solid ${color}33`,
      borderLeft: `3px solid ${color}`,
      borderRadius: 12,
      padding: "18px 20px",
    }}>
      <div style={{ fontSize: 22, marginBottom: 6 }}>{icon}</div>
      <div style={{ fontSize: 28, fontWeight: 800, color, lineHeight: 1 }}>{value}</div>
      <div style={{ fontSize: 12, color: "#8b949e", marginTop: 4 }}>{label}</div>
      {sub && <div style={{ fontSize: 11, color: "#58a6ff", marginTop: 2 }}>{sub}</div>}
    </div>
  )
}

function NotificationItem({ notif, onRead }) {
  const pColor = PRIORITY_COLOR[notif.priority] || "#58a6ff"
  return (
    <div
      onClick={() => !notif.is_read && onRead(notif.id)}
      style={{
        padding: "12px 16px",
        borderBottom: "1px solid #21262d",
        cursor: notif.is_read ? "default" : "pointer",
        background: notif.is_read ? "transparent" : "rgba(88,166,255,0.04)",
        transition: "background 0.15s",
      }}
    >
      <div style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
        <div style={{
          width: 8, height: 8, borderRadius: "50%",
          background: notif.is_read ? "#30363d" : pColor,
          flexShrink: 0, marginTop: 5,
        }} />
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{
            fontSize: 13, fontWeight: 600,
            color: notif.is_read ? "#8b949e" : "#e1e4e8",
            marginBottom: 2,
          }}>
            {notif.title}
          </div>
          <div style={{ fontSize: 12, color: "#8b949e", lineHeight: 1.4 }}>
            {notif.message}
          </div>
          <div style={{ fontSize: 10, color: "#484f58", marginTop: 4 }}>
            {notif.created_at ? new Date(notif.created_at).toLocaleString("tr-TR") : ""}
            {" · "}
            <span style={{ color: pColor }}>{notif.priority}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

function OrderRow({ order, onStatusChange }) {
  const s = STATUS_LABEL[order.status] || { label: order.status, color: "#8b949e", bg: "transparent" }
  return (
    <tr style={{ borderBottom: "1px solid #21262d" }}>
      <td style={td}>{order.id}</td>
      <td style={td}>{order.customer_name}</td>
      <td style={td}>
        <span style={{
          padding: "3px 10px", borderRadius: 20, fontSize: 11,
          background: s.bg, color: s.color, fontWeight: 600,
        }}>
          {s.label}
        </span>
      </td>
      <td style={td}>{order.total_amount?.toLocaleString("tr-TR")} ₺</td>
      <td style={td}>
        <span style={{ fontFamily: "monospace", fontSize: 12, color: "#8b949e" }}>
          {order.tracking_number || "—"}
        </span>
      </td>
      <td style={td}>
        <select
          defaultValue={order.status}
          onChange={e => onStatusChange(order.id, e.target.value)}
          style={{
            background: "#21262d", color: "#c9d1d9",
            border: "1px solid #30363d", borderRadius: 6,
            padding: "3px 6px", fontSize: 12, cursor: "pointer",
          }}
        >
          {Object.entries(STATUS_LABEL).map(([v, { label }]) => (
            <option key={v} value={v}>{label}</option>
          ))}
        </select>
      </td>
    </tr>
  )
}

const td = { padding: "10px 12px", fontSize: 13, color: "#c9d1d9", verticalAlign: "middle" }

function StockBar({ product }) {
  const pct = Math.min(100, Math.round((product.stock_quantity / (product.low_threshold * 3)) * 100))
  const color = product.stock_quantity === 0 ? "#f76a8a"
    : product.stock_quantity <= product.low_threshold ? "#f7a26a" : "#3de6c0"
  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
        <span style={{ fontSize: 13, color: "#c9d1d9" }}>{product.name}</span>
        <span style={{ fontSize: 12, fontFamily: "monospace", color }}>
          {product.stock_quantity} {product.unit}
        </span>
      </div>
      <div style={{ height: 6, background: "#21262d", borderRadius: 3, overflow: "hidden" }}>
        <div style={{
          height: "100%", width: `${pct}%`,
          background: color, borderRadius: 3,
          transition: "width 0.4s ease",
        }} />
      </div>
      <div style={{ fontSize: 10, color: "#484f58", marginTop: 2 }}>
        Eşik: {product.low_threshold} {product.unit}
        {product.stock_quantity === 0 && " · TÜKENDİ 🔴"}
      </div>
    </div>
  )
}

// ── Ana Bileşen ───────────────────────────────────────────────────────────────

export default function AdminDashboard() {
  const [summary, setSummary]       = useState(null)
  const [orders, setOrders]         = useState([])
  const [lowStock, setLowStock]     = useState([])
  const [activeTab, setActiveTab]   = useState("overview")
  const [allProducts, setAllProducts] = useState([])
  const { notifications, unread, markRead, markAllRead } = useNotifications()

  const loadAll = async () => {
    try {
      const [s, o, ls, p] = await Promise.all([
        fetch(`${API}/dashboard/summary`).then(r => r.json()),
        fetch(`${API}/orders?limit=20`).then(r => r.json()),
        fetch(`${API}/products/low-stock`).then(r => r.json()),
        fetch(`${API}/products`).then(r => r.json()),
      ])
      setSummary(s)
      setOrders(o)
      setLowStock(ls)
      setAllProducts(p)
    } catch (e) {
      console.error("Dashboard yüklenemedi:", e)
    }
  }

  useEffect(() => { loadAll() }, [])

  const handleStatusChange = async (orderId, newStatus) => {
    await fetch(`${API}/orders/${orderId}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus }),
    })
    loadAll()
  }

  const tabs = [
    { id: "overview",       label: "📊 Genel Bakış" },
    { id: "orders",         label: "📦 Siparişler" },
    { id: "stock",          label: "🏪 Stok" },
    { id: "notifications",  label: `🔔 Bildirimler${unread > 0 ? ` (${unread})` : ""}` },
  ]

  return (
    <div style={{ minHeight: "100vh", background: "#0f1117", color: "#e1e4e8",
      fontFamily: "'Segoe UI', system-ui, sans-serif" }}>

      {/* Header */}
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "14px 28px", borderBottom: "1px solid #21262d",
        background: "#161b22",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 10,
            background: "linear-gradient(135deg,#7c6af7,#3de6c0)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontWeight: 800, fontSize: 16,
          }}>K</div>
          <div>
            <div style={{ fontWeight: 700, fontSize: 16,
              background: "linear-gradient(135deg,#7c6af7,#3de6c0)",
              WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
              Koopilot
            </div>
            <div style={{ fontSize: 11, color: "#8b949e" }}>Yönetici Paneli</div>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          {unread > 0 && (
            <div style={{
              background: "rgba(247,106,138,0.15)", border: "1px solid rgba(247,106,138,0.3)",
              borderRadius: 20, padding: "4px 12px", fontSize: 12, color: "#f76a8a",
              cursor: "pointer",
            }} onClick={() => setActiveTab("notifications")}>
              🔔 {unread} okunmamış
            </div>
          )}
          <div style={{
            display: "flex", alignItems: "center", gap: 6, fontSize: 12,
            color: "#7ee787", background: "rgba(126,231,135,0.1)",
            border: "1px solid rgba(126,231,135,0.2)",
            padding: "5px 12px", borderRadius: 20,
          }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%",
              background: "#7ee787", display: "inline-block" }} />
            Gemini AI Aktif
          </div>
          <button
            onClick={() => window.location.href = "/"}
            style={{
              background: "#21262d", border: "1px solid #30363d",
              borderRadius: 8, padding: "6px 14px", color: "#c9d1d9",
              cursor: "pointer", fontSize: 12,
            }}
          >
            💬 Chat'e Dön
          </button>
        </div>
      </div>

      {/* Tab Bar */}
      <div style={{ display: "flex", gap: 4, padding: "12px 28px 0",
        borderBottom: "1px solid #21262d", background: "#161b22" }}>
        {tabs.map(t => (
          <button key={t.id} onClick={() => setActiveTab(t.id)}
            style={{
              padding: "8px 16px", borderRadius: "8px 8px 0 0",
              border: "1px solid " + (activeTab === t.id ? "#30363d" : "transparent"),
              borderBottom: activeTab === t.id ? "2px solid #7c6af7" : "none",
              background: activeTab === t.id ? "#0f1117" : "transparent",
              color: activeTab === t.id ? "#e1e4e8" : "#8b949e",
              cursor: "pointer", fontSize: 13, fontWeight: activeTab === t.id ? 600 : 400,
              transition: "all 0.15s",
            }}>
            {t.label}
          </button>
        ))}
      </div>

      {/* İçerik */}
      <div style={{ padding: "24px 28px" }}>

        {/* ── GENEL BAKIŞ ── */}
        {activeTab === "overview" && (
          <div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(180px,1fr))", gap: 16, marginBottom: 28 }}>
              <SummaryCard icon="📦" label="Toplam Sipariş"   value={summary?.total_orders   ?? "…"} color="#7c6af7" />
              <SummaryCard icon="🕐" label="Beklemede"        value={summary?.pending         ?? "…"} color="#f7a26a" />
              <SummaryCard icon="🚚" label="Kargoda"          value={summary?.in_cargo        ?? "…"} color="#3de6c0" />
              <SummaryCard icon="✅" label="Teslim Edildi"    value={summary?.delivered       ?? "…"} color="#7ee787" />
              <SummaryCard icon="⚠️" label="Kritik Stok"     value={summary?.critical_stock  ?? "…"} color="#f7a26a" sub="ürün" />
              <SummaryCard icon="🔔" label="Okunmamış Bildirim" value={summary?.unread_notifs ?? "…"} color="#f76a8a" />
            </div>

            {/* Kritik stoklar özet */}
            {lowStock.length > 0 && (
              <div style={{
                background: "#161b22", border: "1px solid rgba(247,162,106,0.3)",
                borderRadius: 12, padding: 20, marginBottom: 24,
              }}>
                <div style={{ fontWeight: 700, marginBottom: 16, color: "#f7a26a" }}>
                  ⚠️ Kritik Stok Uyarıları ({lowStock.length} ürün)
                </div>
                {lowStock.map(p => <StockBar key={p.id} product={p} />)}
              </div>
            )}

            {/* Son siparişler (5 adet) */}
            <div style={{ background: "#161b22", border: "1px solid #21262d", borderRadius: 12, overflow: "hidden" }}>
              <div style={{ padding: "14px 20px", borderBottom: "1px solid #21262d",
                fontWeight: 700, fontSize: 14 }}>
                📦 Son Siparişler
              </div>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ background: "#0d1117" }}>
                    {["Sipariş No", "Müşteri", "Durum", "Tutar", "Kargo", "İşlem"].map(h => (
                      <th key={h} style={{ padding: "10px 12px", textAlign: "left",
                        fontSize: 11, color: "#8b949e", letterSpacing: "0.5px",
                        textTransform: "uppercase", fontWeight: 600 }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {orders.slice(0, 5).map(o => (
                    <OrderRow key={o.id} order={o} onStatusChange={handleStatusChange} />
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ── SİPARİŞLER ── */}
        {activeTab === "orders" && (
          <div style={{ background: "#161b22", border: "1px solid #21262d", borderRadius: 12, overflow: "hidden" }}>
            <div style={{ padding: "14px 20px", borderBottom: "1px solid #21262d",
              display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontWeight: 700, fontSize: 14 }}>📦 Tüm Siparişler</span>
              <button onClick={loadAll} style={{
                background: "#21262d", border: "1px solid #30363d",
                borderRadius: 6, padding: "5px 12px", color: "#c9d1d9",
                cursor: "pointer", fontSize: 12,
              }}>🔄 Yenile</button>
            </div>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ background: "#0d1117" }}>
                  {["Sipariş No", "Müşteri", "Durum", "Tutar", "Kargo", "Durum Değiştir"].map(h => (
                    <th key={h} style={{ padding: "10px 12px", textAlign: "left",
                      fontSize: 11, color: "#8b949e", letterSpacing: "0.5px",
                      textTransform: "uppercase", fontWeight: 600 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {orders.map(o => (
                  <OrderRow key={o.id} order={o} onStatusChange={handleStatusChange} />
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* ── STOK ── */}
        {activeTab === "stock" && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
            <div style={{ background: "#161b22", border: "1px solid rgba(247,162,106,0.3)",
              borderRadius: 12, padding: 20 }}>
              <div style={{ fontWeight: 700, marginBottom: 16, color: "#f7a26a" }}>
                ⚠️ Kritik Seviyedekiler ({lowStock.length})
              </div>
              {lowStock.length === 0
                ? <div style={{ color: "#8b949e", fontSize: 13 }}>Kritik stok yok ✅</div>
                : lowStock.map(p => <StockBar key={p.id} product={p} />)
              }
            </div>
            <div style={{ background: "#161b22", border: "1px solid #21262d",
              borderRadius: 12, padding: 20 }}>
              <div style={{ fontWeight: 700, marginBottom: 16 }}>
                📦 Tüm Ürünler ({allProducts.length})
              </div>
              {allProducts.map(p => (
                <div key={p.id} style={{
                  display: "flex", justifyContent: "space-between", alignItems: "center",
                  padding: "8px 0", borderBottom: "1px solid #21262d23",
                }}>
                  <div>
                    <div style={{ fontSize: 13, color: "#c9d1d9" }}>{p.name}</div>
                    <div style={{ fontSize: 11, color: "#484f58" }}>{p.id} · {p.category}</div>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <div style={{
                      fontSize: 13, fontFamily: "monospace",
                      color: p.is_critical ? "#f7a26a" : "#7ee787",
                    }}>
                      {p.stock_quantity} {p.unit}
                    </div>
                    <div style={{ fontSize: 11, color: "#484f58" }}>{p.unit_price} ₺</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── BİLDİRİMLER ── */}
        {activeTab === "notifications" && (
          <div style={{ background: "#161b22", border: "1px solid #21262d",
            borderRadius: 12, overflow: "hidden", maxWidth: 700 }}>
            <div style={{ padding: "14px 20px", borderBottom: "1px solid #21262d",
              display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontWeight: 700, fontSize: 14 }}>
                🔔 Bildirimler {unread > 0 && (
                  <span style={{
                    marginLeft: 8, background: "#f76a8a22",
                    color: "#f76a8a", borderRadius: 20, padding: "1px 8px", fontSize: 12,
                  }}>{unread} okunmamış</span>
                )}
              </span>
              {unread > 0 && (
                <button onClick={markAllRead} style={{
                  background: "transparent", border: "1px solid #30363d",
                  borderRadius: 6, padding: "4px 12px", color: "#8b949e",
                  cursor: "pointer", fontSize: 12,
                }}>Tümünü Okundu İşaretle</button>
              )}
            </div>
            {notifications.length === 0
              ? <div style={{ padding: 24, color: "#8b949e", fontSize: 13, textAlign: "center" }}>
                  Bildirim yok
                </div>
              : notifications.map(n => (
                  <NotificationItem key={n.id} notif={n} onRead={markRead} />
                ))
            }
          </div>
        )}

      </div>
    </div>
  )
}
