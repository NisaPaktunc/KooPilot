import { useState, useEffect } from "react"
import { useNotifications } from "../hooks/useNotifications"

const API = "http://127.0.0.1:8000"

// --- Icons (Inline SVGs to avoid external dependencies) ---
const Icon = {
  Layout: () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="14" y="3" rx="1"/><rect width="7" height="7" x="14" y="14" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/></svg>,
  Package: () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg>,
  Boxes: () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>,
  Chart: () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>,
  Bell: () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>,
  Sparkles: () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>,
  Msg: () => <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>,
  Search: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>,
  Clock: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>,
  Truck: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="15" height="10" x="3" y="8" rx="2"/><path d="M18 8h3a1 1 0 0 1 1 1v5h-4z"/><circle cx="7.5" cy="18.5" r="1.5"/><circle cx="17.5" cy="18.5" r="1.5"/></svg>,
  Check: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>,
  Alert: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>,
  Wallet: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a8 8 0 0 1-5 7.96V16a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v5.96A8 8 0 0 1 3 15V9a2 2 0 0 1 2-2h14z"/></svg>,
  Trophy: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/></svg>,
  Folder: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></svg>,
  Pie: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>,
}

// --- Status & Helpers ---
const STATUS_LABELS = {
  beklemede: "Beklemede",
  hazirlaniyor: "Hazırlanıyor",
  kargoda: "Kargoda",
  teslim_edildi: "Teslim Edildi",
  iptal: "İptal",
}

function StatusPill({ status }) {
  return <span className={`pill pill-${status}`}>{STATUS_LABELS[status] || status}</span>
}

// --- Components ---
function BarRow({ label, value, pct, colorCls }) {
  return (
    <div className="bar-row">
      <div className="bar-row-head">
        <span className="bar-row-label">{label}</span>
        <span className="bar-row-value">{value}</span>
      </div>
      <div className="bar-track">
        <div className={`bar-fill ${colorCls}`} style={{ width: `${Math.max(2, pct)}%` }} />
      </div>
    </div>
  )
}

function ChartCard({ title, icon: IconCmp, accent, children }) {
  const textColor = `text-${accent === 'primary' ? 'primary' : accent === 'success' ? 'success' : accent === 'warning' ? 'warning' : 'info'}`
  return (
    <section className="card">
      <header className="card-header">
        <h2 style={{ fontSize: 14 }} className={textColor}><IconCmp /> {title}</h2>
      </header>
      <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        {children}
      </div>
    </section>
  )
}

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState("genel")
  const { notifications, unread, markRead, markAllRead } = useNotifications()
  const [data, setData] = useState({
    summary: { total_orders: 0, pending: 0, in_cargo: 0, delivered: 0, critical_stock: 0 },
    orders: [],
    low_stock: [],
    products: [],
    analytics: null,
    insights: null
  })

  // Tab State Handlers
  const [orderSearch, setOrderSearch] = useState("")
  const [orderStatus, setOrderStatus] = useState("tumu")
  const [stockSearch, setStockSearch] = useState("")

  useEffect(() => {
    Promise.all([
      fetch(`${API}/dashboard/summary`).then(r => r.json()),
      fetch(`${API}/orders?limit=50`).then(r => r.json()),
      fetch(`${API}/products/low-stock`).then(r => r.json()),
      fetch(`${API}/products`).then(r => r.json()),
      fetch(`${API}/dashboard/analytics`).then(r => r.json()).catch(() => null),
      fetch(`${API}/dashboard/insights`).then(r => r.json()).catch(() => null)
    ]).then(([s, o, l, p, a, ins]) => {
      setData({ summary: s, orders: o, low_stock: l, products: p, analytics: a, insights: ins })
    }).catch(console.error)
  }, [])

  const filteredOrders = data.orders.filter(o => {
    const mq = !orderSearch || o.id.toLowerCase().includes(orderSearch.toLowerCase()) || o.customer.toLowerCase().includes(orderSearch.toLowerCase())
    const ms = orderStatus === "tumu" || o.status === orderStatus
    return mq && ms
  })

  const filteredStock = data.products.filter(p =>
    !stockSearch || p.name.toLowerCase().includes(stockSearch.toLowerCase()) || p.category.toLowerCase().includes(stockSearch.toLowerCase())
  )

  const TABS = [
    { id: "genel", label: "Genel Bakış", icon: Icon.Layout },
    { id: "siparisler", label: "Siparişler", icon: Icon.Package },
    { id: "stok", label: "Stok", icon: Icon.Boxes },
    { id: "analitik", label: "Analitik", icon: Icon.Chart },
    { id: "icgoruler", label: "İçgörüler", icon: Icon.Sparkles },
    { id: "bildirimler", label: "Bildirimler", icon: Icon.Bell, badge: unread },
  ]

  const renderContent = () => {
    if (activeTab === "genel") {
      return (
        <div className="space-y">
          <div className="kpi-grid">
            <div className="kpi-card">
              <div className="kpi-icon" style={{ background: "rgba(59,130,246,0.1)", color: "var(--info)" }}><Icon.Package /></div>
              <div className="kpi-label">Toplam Sipariş</div>
              <div className="kpi-value">{data.summary.total_orders}</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-icon" style={{ background: "rgba(245,158,11,0.1)", color: "var(--warning)" }}><Icon.Clock /></div>
              <div className="kpi-label">Beklemede</div>
              <div className="kpi-value">{data.summary.pending || 0}</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-icon" style={{ background: "rgba(59,130,246,0.1)", color: "var(--info)" }}><Icon.Truck /></div>
              <div className="kpi-label">Kargoda</div>
              <div className="kpi-value">{data.summary.in_cargo || 0}</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-icon" style={{ background: "rgba(22,163,74,0.1)", color: "var(--success)" }}><Icon.Check /></div>
              <div className="kpi-label">Teslim Edildi</div>
              <div className="kpi-value">{data.summary.delivered || 0}</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-icon" style={{ background: "rgba(239,68,68,0.1)", color: "var(--destructive)" }}><Icon.Alert /></div>
              <div className="kpi-label">Kritik Stok</div>
              <div className="kpi-value">{data.low_stock.length}</div>
            </div>
          </div>

          <div className="grid-2" style={{ gridTemplateColumns: '1fr 2fr' }}>
            <div className="card" style={{ maxHeight: 500, display: 'flex', flexDirection: 'column' }}>
              <div className="card-header">
                <h2 style={{ color: 'var(--warning)' }}><Icon.Alert /> Kritik Stok ({data.low_stock.length})</h2>
              </div>
              <div className="card-body" style={{ overflowY: 'auto', padding: 0 }}>
                {data.low_stock.slice(0,10).map((p,i) => {
                  const pct = p.low_threshold ? Math.min(100, (p.stock_quantity / p.low_threshold)*100) : 0;
                  return (
                    <div key={i} style={{ padding: 16, borderBottom: '1px solid var(--border)' }}>
                      <div className="flex-between mb-4">
                        <span style={{ fontSize: 14, fontWeight: 500 }}>{p.name}</span>
                        <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--destructive)' }}>{p.stock_quantity} kg</span>
                      </div>
                      <div className="bar-track">
                        <div className="bar-fill bar-fill-warning" style={{ width: `${Math.max(2, pct)}%` }} />
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <h2 style={{ color: 'var(--primary)' }}><Icon.Package /> Son Siparişler</h2>
              </div>
              <div style={{ overflowX: 'auto' }}>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Sipariş No</th><th>Müşteri</th><th>Durum</th><th className="text-right">Tutar</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.orders.slice(0,7).map(o => (
                      <tr key={o.id}>
                        <td className="mono" style={{ color: 'var(--muted)' }}>{o.id}</td>
                        <td style={{ fontWeight: 500 }}>{o.customer}</td>
                        <td><StatusPill status={o.status} /></td>
                        <td className="tabular text-right" style={{ fontWeight: 600 }}>₺{o.amount}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )
    }

    if (activeTab === "siparisler") {
      return (
        <div className="card">
          <div className="card-header" style={{ gap: 16, flexWrap: 'wrap' }}>
            <div style={{ position: 'relative', flex: 1, minWidth: 200, maxWidth: 400 }}>
              <div className="input-icon"><Icon.Search /></div>
              <input className="input input-with-icon" style={{ width: '100%' }} placeholder="Sipariş no veya müşteri ara..." value={orderSearch} onChange={e=>setOrderSearch(e.target.value)} />
            </div>
            <select className="select" value={orderStatus} onChange={e=>setOrderStatus(e.target.value)}>
              <option value="tumu">Tüm Durumlar</option>
              {Object.entries(STATUS_LABELS).map(([k,v]) => <option key={k} value={k}>{v}</option>)}
            </select>
          </div>
          <table className="table">
            <thead>
              <tr><th>Sipariş No</th><th>Müşteri</th><th>Durum</th><th className="text-right">Tutar</th></tr>
            </thead>
            <tbody>
              {filteredOrders.map(o => (
                <tr key={o.id}>
                  <td className="mono" style={{ color: 'var(--muted)' }}>{o.id}</td>
                  <td style={{ fontWeight: 500 }}>{o.customer}</td>
                  <td><StatusPill status={o.status} /></td>
                  <td className="tabular text-right" style={{ fontWeight: 600 }}>₺{o.amount}</td>
                </tr>
              ))}
              {filteredOrders.length === 0 && <tr><td colSpan="4" style={{ textAlign: 'center', padding: 40, color: 'var(--muted)' }}>Sipariş bulunamadı.</td></tr>}
            </tbody>
          </table>
        </div>
      )
    }

    if (activeTab === "stok") {
      return (
        <div className="card">
          <div className="card-header">
            <div style={{ position: 'relative', width: '100%', maxWidth: 400 }}>
              <div className="input-icon"><Icon.Search /></div>
              <input className="input input-with-icon" style={{ width: '100%' }} placeholder="Ürün ara..." value={stockSearch} onChange={e=>setStockSearch(e.target.value)} />
            </div>
          </div>
          <table className="table">
            <thead>
              <tr><th>Ürün</th><th>Kategori</th><th className="text-right">Stok</th><th className="text-right">Fiyat</th></tr>
            </thead>
            <tbody>
              {filteredStock.map(p => (
                <tr key={p.code}>
                  <td style={{ fontWeight: 500 }}>{p.name} <span className="mono" style={{ color: 'var(--muted)', fontSize: 11, marginLeft: 8 }}>{p.code}</span></td>
                  <td>{p.category}</td>
                  <td className="tabular text-right" style={{ color: p.stock_quantity <= p.low_threshold ? 'var(--destructive)' : 'var(--success)', fontWeight: 700 }}>{p.stock_quantity} kg</td>
                  <td className="tabular text-right">₺{p.price}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )
    }

    if (activeTab === "analitik" && data.analytics) {
      const a = data.analytics
      const maxQty = Math.max(...a.top_products.map(p=>p.quantity))
      const maxRev = Math.max(...a.top_revenue.map(p=>p.revenue))
      const maxCat = Math.max(...a.category_data.map(c=>c.revenue))
      
      return (
        <div className="space-y">
          <div className="grid-3">
            <div className="card" style={{ padding: 24, border: '2px solid rgba(22,163,74,0.2)' }}>
              <div className="flex-between mb-4">
                <span className="kpi-label">Toplam Ciro</span>
                <div className="kpi-icon" style={{ background: "var(--primary-light)", color: "var(--primary)", margin: 0 }}><Icon.Wallet /></div>
              </div>
              <div className="kpi-value" style={{ color: "var(--primary)" }}>₺{a.total_revenue.toLocaleString('tr-TR')}</div>
            </div>
            <div className="card" style={{ padding: 24, border: '2px solid rgba(59,130,246,0.2)' }}>
              <div className="flex-between mb-4">
                <span className="kpi-label">Toplam Sipariş</span>
                <div className="kpi-icon" style={{ background: "rgba(59,130,246,0.1)", color: "var(--info)", margin: 0 }}><Icon.Package /></div>
              </div>
              <div className="kpi-value" style={{ color: "var(--info)" }}>{a.total_orders}</div>
            </div>
            <div className="card" style={{ padding: 24, border: '2px solid rgba(245,158,11,0.2)' }}>
              <div className="flex-between mb-4">
                <span className="kpi-label">Ortalama Sipariş</span>
                <div className="kpi-icon" style={{ background: "rgba(245,158,11,0.1)", color: "var(--warning)", margin: 0 }}><Icon.Chart /></div>
              </div>
              <div className="kpi-value" style={{ color: "var(--warning)" }}>₺{a.avg_order.toLocaleString('tr-TR')}</div>
            </div>
          </div>

          <div className="grid-2">
            <ChartCard title="En Çok Satan Ürünler" icon={Icon.Trophy} accent="primary">
              {a.top_products.map(p => <BarRow key={p.name} label={p.name} value={`${p.quantity} kg`} pct={(p.quantity/maxQty)*100} colorCls="bar-fill-primary" />)}
            </ChartCard>
            <ChartCard title="En Çok Gelir Getirenler" icon={Icon.Wallet} accent="success">
              {a.top_revenue.map(p => <BarRow key={p.name} label={p.name} value={`₺${p.revenue.toLocaleString('tr-TR')}`} pct={(p.revenue/maxRev)*100} colorCls="bar-fill-success" />)}
            </ChartCard>
            <ChartCard title="Kategori Bazlı Gelir" icon={Icon.Folder} accent="warning">
              {a.category_data.map(c => <BarRow key={c.category} label={c.category} value={`₺${c.revenue.toLocaleString('tr-TR')}`} pct={(c.revenue/maxCat)*100} colorCls="bar-fill-warning" />)}
            </ChartCard>
            <ChartCard title="Sipariş Durumları" icon={Icon.Pie} accent="info">
              {Object.entries(a.status_counts).map(([k,v]) => <BarRow key={k} label={STATUS_LABELS[k]||k} value={v} pct={(v/a.total_orders)*100} colorCls="bar-fill-info" />)}
            </ChartCard>
          </div>
        </div>
      )
    }

    if (activeTab === "bildirimler") {
      return (
        <div className="card">
          <div className="card-header">
            <h2><Icon.Bell /> Bildirimler ({unread} yeni)</h2>
            <button className="btn-secondary" onClick={markAllRead}>Tümünü Okundu İşaretle</button>
          </div>
          <div>
            {notifications.map(n => (
              <div key={n.id} className="notif-item" onClick={() => !n.is_read && markRead(n.id)}>
                <div className="notif-dot" style={{ background: n.is_read ? 'transparent' : 'var(--primary)' }} />
                <div style={{ flex: 1 }}>
                  <div className="flex-between">
                    <span className="notif-title">{n.title}</span>
                    <span className="priority-badge" style={{
                      background: n.priority === 'yuksek' ? 'rgba(239,68,68,0.1)' : 'rgba(245,158,11,0.1)',
                      color: n.priority === 'yuksek' ? 'var(--destructive)' : 'var(--warning)'
                    }}>{n.priority}</span>
                  </div>
                  <div className="notif-body">{n.message}</div>
                  <div className="notif-time">{new Date(n.created_at).toLocaleString('tr-TR')}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )
    }

    if (activeTab === "icgoruler" && data.insights) {
      const ins = data.insights
      const h = ins.health_score
      const gradeColors = { 'A+': 'var(--success)', 'A': 'var(--success)', 'B': 'var(--info)', 'C': 'var(--warning)', 'D': 'var(--destructive)' }
      const priorityStyles = {
        'ACIL': { bg: 'rgba(239,68,68,0.1)', color: 'var(--destructive)' },
        'YUKSEK': { bg: 'rgba(245,158,11,0.1)', color: 'var(--warning)' },
        'ORTA': { bg: 'rgba(59,130,246,0.1)', color: 'var(--info)' },
      }
      return (
        <div className="space-y">
          {/* Health Score */}
          <div className="card" style={{ padding: 32, textAlign: 'center', border: `2px solid ${gradeColors[h.grade] || 'var(--border)'}` }}>
            <div style={{ fontSize: 64, fontWeight: 800, color: gradeColors[h.grade], lineHeight: 1 }}>{h.score}</div>
            <div style={{ fontSize: 20, fontWeight: 700, marginTop: 4 }}>/ 100 ({h.grade})</div>
            <div className="kpi-label" style={{ marginTop: 12 }}>Isletme Saglik Skoru</div>
            <div style={{ display: 'flex', justifyContent: 'center', gap: 24, marginTop: 20 }}>
              {Object.entries(h.details).map(([k, v]) => (
                <div key={k} style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 20, fontWeight: 700 }}>{v}<span style={{ fontSize: 12, color: 'var(--muted)' }}>/25</span></div>
                  <div style={{ fontSize: 11, color: 'var(--muted)', textTransform: 'capitalize' }}>{k === 'revenue' ? 'Gelir' : k === 'stock' ? 'Stok' : k === 'customer' ? 'Musteri' : 'Operasyon'}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="card">
            <div className="card-header"><h2><Icon.Alert /> Onerilen Aksiyonlar</h2></div>
            <div>
              {ins.actions.map((a, i) => (
                <div key={i} style={{ padding: 16, borderBottom: '1px solid var(--border)', display: 'flex', gap: 12 }}>
                  <span className="priority-badge" style={{ ...(priorityStyles[a.priority] || priorityStyles['ORTA']), padding: '4px 8px', borderRadius: 6, fontSize: 10, fontWeight: 700, flexShrink: 0, height: 'fit-content' }}>{a.priority}</span>
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 600 }}>{a.action}</div>
                    <div style={{ fontSize: 12, color: 'var(--muted)', marginTop: 4 }}>{a.reason}</div>
                    <div style={{ fontSize: 12, color: 'var(--success)', marginTop: 2 }}>Etki: {a.impact}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="grid-2">
            {/* Stock Risks */}
            <div className="card">
              <div className="card-header"><h2><Icon.Alert /> Stok Risk Skorlari</h2></div>
              <div style={{ overflowX: 'auto' }}>
                <table className="table">
                  <thead><tr><th>Urun</th><th className="text-right">Skor</th><th className="text-right">Stok</th><th className="text-right">Gun</th></tr></thead>
                  <tbody>
                    {ins.stock_risks.slice(0, 10).map(s => (
                      <tr key={s.id}>
                        <td style={{ fontWeight: 500 }}>{s.name}</td>
                        <td className="tabular text-right" style={{ color: s.risk_score >= 70 ? 'var(--destructive)' : s.risk_score >= 50 ? 'var(--warning)' : 'var(--success)', fontWeight: 700 }}>{s.risk_score}</td>
                        <td className="tabular text-right">{s.current_stock} {s.unit}</td>
                        <td className="tabular text-right">{s.days_until_empty >= 0 ? s.days_until_empty : '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Customer Segments */}
            <div className="card">
              <div className="card-header"><h2><Icon.Trophy /> Musteri Segmentleri</h2></div>
              <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                {ins.customers.segments.map(seg => {
                  const segColors = { VIP: 'bar-fill-primary', Sadik: 'bar-fill-success', Normal: 'bar-fill-info', Yeni: 'bar-fill-warning' }
                  return <BarRow key={seg.segment} label={`${seg.segment} (${seg.count} musteri)`} value={`${seg.total_revenue.toLocaleString('tr-TR')} TL`} pct={(seg.total_revenue / ins.revenue.total_revenue) * 100} colorCls={segColors[seg.segment] || 'bar-fill-info'} />
                })}
                <div style={{ marginTop: 8, padding: 12, background: 'var(--primary-light)', borderRadius: 10, fontSize: 13 }}>
                  <strong>En Degerli:</strong> {ins.customers.top_customer.name} — {ins.customers.top_customer.total.toLocaleString('tr-TR')} TL ({ins.customers.top_customer.orders} siparis)
                </div>
              </div>
            </div>
          </div>

          {/* Categories */}
          <div className="card">
            <div className="card-header"><h2><Icon.Folder /> Kategori Performansi</h2></div>
            <div style={{ overflowX: 'auto' }}>
              <table className="table">
                <thead><tr><th>Kategori</th><th className="text-right">Ciro</th><th className="text-right">Satis</th><th className="text-right">Urun</th><th className="text-right">Marj</th></tr></thead>
                <tbody>
                  {ins.categories.map(c => (
                    <tr key={c.category}>
                      <td style={{ fontWeight: 600, textTransform: 'capitalize' }}>{c.category}</td>
                      <td className="tabular text-right" style={{ fontWeight: 600 }}>{c.revenue.toLocaleString('tr-TR')} TL</td>
                      <td className="tabular text-right">{c.items_sold} adet</td>
                      <td className="tabular text-right">{c.unique_products}</td>
                      <td className="tabular text-right" style={{ color: 'var(--success)' }}>%{c.margin_estimate.toFixed(0)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )
    }

    return null
  }

  return (
    <div className="admin-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="sidebar-logo">K</div>
          <div>
            <div className="sidebar-title">Koopilot</div>
            <div className="sidebar-subtitle">Yönetici Paneli</div>
          </div>
        </div>
        <nav className="sidebar-nav">
          {TABS.map(t => (
            <button key={t.id} className={`sidebar-link ${activeTab === t.id ? 'active' : ''}`} onClick={() => setActiveTab(t.id)}>
              <span className="sidebar-link-text"><t.icon /> {t.label}</span>
              {t.badge > 0 && <span className="sidebar-badge">{t.badge}</span>}
            </button>
          ))}
        </nav>
        <a href="/" className="sidebar-cta">
          <div className="sidebar-cta-label"><Icon.Sparkles /> Gemini AI</div>
          <div className="sidebar-cta-desc">Operasyon asistanınızla sohbet edin</div>
          <div className="sidebar-cta-btn"><Icon.Msg /> Sohbeti Aç</div>
        </a>
      </aside>

      {/* Main Content */}
      <main className="admin-main">
        <header className="page-header">
          <div>
            <h1>{TABS.find(t=>t.id===activeTab)?.label}</h1>
            <p>Bugünkü operasyon durumunuza genel bakış</p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div className="ai-badge"><span className="ai-badge-dot" /> AI Aktif</div>
          </div>
        </header>
        <div className="admin-content">
          {renderContent()}
        </div>
      </main>
    </div>
  )
}
