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
  MessageCircle: () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>,
  Search: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>,
  Clock: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>,
  Truck: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="15" height="10" x="3" y="8" rx="2"/><path d="M18 8h3a1 1 0 0 1 1 1v5h-4z"/><circle cx="7.5" cy="18.5" r="1.5"/><circle cx="17.5" cy="18.5" r="1.5"/></svg>,
  Check: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>,
  Alert: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>,
  Wallet: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a8 8 0 0 1-5 7.96V16a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v5.96A8 8 0 0 1 3 15V9a2 2 0 0 1 2-2h14z"/></svg>,
  Trophy: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/></svg>,
  Folder: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></svg>,
  Pie: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>,
  Upload: () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>,
  Plus: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>,
  Edit: () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 3a2.85 2.85 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/></svg>,
  Trash: () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>,
  X: () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>,
  Users: () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>,
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

  // Upload State
  const [uploadResult, setUploadResult] = useState(null)
  const [uploadPreview, setUploadPreview] = useState(null)
  const [uploading, setUploading] = useState(false)

  // CRUD State
  const [modal, setModal] = useState(null) // { type: 'product'|'order'|'supplier', mode: 'add'|'edit', data: {} }
  const [suppliers, setSuppliers] = useState([])
  
  // WhatsApp State
  const [waStatus, setWaStatus] = useState(null)
  const [waSessions, setWaSessions] = useState([])

  const refreshData = () => {
    Promise.all([
      fetch(`${API}/dashboard/summary`).then(r => r.json()),
      fetch(`${API}/orders?limit=50`).then(r => r.json()),
      fetch(`${API}/products/low-stock`).then(r => r.json()),
      fetch(`${API}/products`).then(r => r.json()),
      fetch(`${API}/dashboard/analytics`).then(r => r.json()).catch(() => null),
      fetch(`${API}/dashboard/insights`).then(r => r.json()).catch(() => null),
      fetch(`${API}/suppliers`).then(r => r.json()).catch(() => []),
      fetch(`${API}/whatsapp/status`).then(r => r.json()).catch(() => null),
      fetch(`${API}/whatsapp/sessions`).then(r => r.json()).catch(() => [])
    ]).then(([s, o, l, p, a, ins, sup, was, wases]) => {
      setData({ summary: s, orders: o, low_stock: l, products: p, analytics: a, insights: ins })
      setSuppliers(sup)
      setWaStatus(was)
      setWaSessions(wases)
    }).catch(console.error)
  }

  useEffect(() => { refreshData() }, [])

  const apiCall = async (url, method, body) => {
    const res = await fetch(`${API}${url}`, { method, headers: { 'Content-Type': 'application/json' }, body: body ? JSON.stringify(body) : undefined })
    const data = await res.json()
    if (data.success) refreshData()
    return data
  }

  const handleDelete = async (type, id) => {
    if (!confirm('Bu kaydi silmek istediginize emin misiniz?')) return
    await apiCall(`/${type}/${id}`, 'DELETE')
  }

  const filteredOrders = data.orders.filter(o => {
    const name = o.customer_name || o.customer || ''
    const mq = !orderSearch || o.id.toLowerCase().includes(orderSearch.toLowerCase()) || name.toLowerCase().includes(orderSearch.toLowerCase())
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
    { id: "tedarikciler", label: "Tedarikçiler", icon: Icon.Users },
    { id: "analitik", label: "Analitik", icon: Icon.Chart },
    { id: "icgoruler", label: "İçgörüler", icon: Icon.Sparkles },
    { id: "whatsapp", label: "WhatsApp", icon: Icon.MessageCircle },
    { id: "iceaktar", label: "İçe Aktar", icon: Icon.Upload },
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
          <div className="card-header" style={{ gap: 12, flexWrap: 'wrap' }}>
            <div style={{ position: 'relative', flex: 1, minWidth: 200, maxWidth: 400 }}>
              <div className="input-icon"><Icon.Search /></div>
              <input className="input input-with-icon" style={{ width: '100%' }} placeholder="Sipariş no veya müşteri ara..." value={orderSearch} onChange={e=>setOrderSearch(e.target.value)} />
            </div>
            <select className="select" value={orderStatus} onChange={e=>setOrderStatus(e.target.value)}>
              <option value="tumu">Tüm Durumlar</option>
              {Object.entries(STATUS_LABELS).map(([k,v]) => <option key={k} value={k}>{v}</option>)}
            </select>
            <button className="btn-primary" onClick={() => setModal({ type: 'order', mode: 'add', data: { customer_name: '', status: 'beklemede', total_amount: 0 } })}><Icon.Plus /> Sipariş Ekle</button>
          </div>
          <table className="table">
            <thead>
              <tr><th>Sipariş No</th><th>Müşteri</th><th>Durum</th><th className="text-right">Tutar</th><th style={{width:80}}>İşlem</th></tr>
            </thead>
            <tbody>
              {filteredOrders.map(o => (
                <tr key={o.id}>
                  <td className="mono" style={{ color: 'var(--muted)' }}>{o.id}</td>
                  <td style={{ fontWeight: 500 }}>{o.customer_name}</td>
                  <td><StatusPill status={o.status} /></td>
                  <td className="tabular text-right" style={{ fontWeight: 600 }}>₺{o.total_amount}</td>
                  <td>
                    <div style={{ display: 'flex', gap: 4 }}>
                      <button className="btn-icon" title="Düzenle" onClick={() => setModal({ type: 'order', mode: 'edit', data: { ...o } })}><Icon.Edit /></button>
                      <button className="btn-icon btn-icon-danger" title="Sil" onClick={() => handleDelete('orders', o.id)}><Icon.Trash /></button>
                    </div>
                  </td>
                </tr>
              ))}
              {filteredOrders.length === 0 && <tr><td colSpan="5" style={{ textAlign: 'center', padding: 40, color: 'var(--muted)' }}>Sipariş bulunamadı.</td></tr>}
            </tbody>
          </table>
        </div>
      )
    }

    if (activeTab === "stok") {
      return (
        <div className="card">
          <div className="card-header" style={{ gap: 12 }}>
            <div style={{ position: 'relative', flex: 1, maxWidth: 400 }}>
              <div className="input-icon"><Icon.Search /></div>
              <input className="input input-with-icon" style={{ width: '100%' }} placeholder="Ürün ara..." value={stockSearch} onChange={e=>setStockSearch(e.target.value)} />
            </div>
            <button className="btn-primary" onClick={() => setModal({ type: 'product', mode: 'add', data: { name: '', category: 'genel', stock_quantity: 0, low_threshold: 10, unit_price: 0, unit: 'adet' } })}><Icon.Plus /> Ürün Ekle</button>
          </div>
          <table className="table">
            <thead>
              <tr><th>Ürün</th><th>Kategori</th><th className="text-right">Stok</th><th className="text-right">Fiyat</th><th style={{width:80}}>İşlem</th></tr>
            </thead>
            <tbody>
              {filteredStock.map(p => (
                <tr key={p.id}>
                  <td style={{ fontWeight: 500 }}>{p.name} <span className="mono" style={{ color: 'var(--muted)', fontSize: 11, marginLeft: 8 }}>{p.id}</span></td>
                  <td>{p.category}</td>
                  <td className="tabular text-right" style={{ color: p.is_critical ? 'var(--destructive)' : 'var(--success)', fontWeight: 700 }}>{p.stock_quantity} {p.unit}</td>
                  <td className="tabular text-right">₺{p.unit_price}</td>
                  <td>
                    <div style={{ display: 'flex', gap: 4 }}>
                      <button className="btn-icon" title="Düzenle" onClick={() => setModal({ type: 'product', mode: 'edit', data: { ...p } })}><Icon.Edit /></button>
                      <button className="btn-icon btn-icon-danger" title="Sil" onClick={() => handleDelete('products', p.id)}><Icon.Trash /></button>
                    </div>
                  </td>
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

    if (activeTab === "iceaktar") {
      const handleFile = async (file) => {
        if (!file) return
        setUploading(true)
        setUploadResult(null)
        setUploadPreview(null)
        // Preview
        const fd1 = new FormData()
        fd1.append('file', file)
        try {
          const prev = await fetch(`${API}/upload/preview`, { method: 'POST', body: fd1 }).then(r => r.json())
          setUploadPreview(prev)
        } catch { setUploadPreview(null) }
        setUploading(false)
      }

      const handleImport = async (file, dataType) => {
        if (!file) return
        setUploading(true)
        const fd = new FormData()
        fd.append('file', file)
        if (dataType) fd.append('data_type', dataType)
        try {
          const res = await fetch(`${API}/upload`, { method: 'POST', body: fd }).then(r => r.json())
          setUploadResult(res)
          // Reload dashboard data
          Promise.all([
            fetch(`${API}/dashboard/summary`).then(r => r.json()),
            fetch(`${API}/orders?limit=50`).then(r => r.json()),
            fetch(`${API}/products/low-stock`).then(r => r.json()),
            fetch(`${API}/products`).then(r => r.json()),
          ]).then(([s, o, l, p]) => {
            setData(prev => ({ ...prev, summary: s, orders: o, low_stock: l, products: p }))
          })
        } catch (e) { setUploadResult({ success: false, errors: ['Yukleme hatasi: ' + e.message] }) }
        setUploading(false)
      }

      const TYPE_LABELS = { products: 'Urunler', orders: 'Siparisler', suppliers: 'Tedarikciler' }
      let fileRef = null

      return (
        <div className="space-y">
          {/* Upload Area */}
          <div className="card" style={{ padding: 40, textAlign: 'center' }}>
            <div style={{ marginBottom: 16 }}>
              <div style={{ width: 56, height: 56, borderRadius: 14, background: 'var(--primary-light)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: 12 }}>
                <Icon.Upload />
              </div>
              <h2 style={{ fontSize: 18, fontWeight: 700 }}>Excel veya CSV Dosyasi Yukle</h2>
              <p style={{ fontSize: 13, color: 'var(--muted)', marginTop: 6, maxWidth: 400, margin: '6px auto 0' }}>Urunler, siparisler veya tedarikci verilerini toplu olarak iceride aktarin. Sistem kolon basliklarindan veri tipini otomatik tespit eder.</p>
            </div>
            <input type="file" accept=".xlsx,.xls,.csv" id="file-upload" style={{ display: 'none' }} onChange={e => { fileRef = e.target.files[0]; handleFile(e.target.files[0]) }} />
            <label htmlFor="file-upload" className="btn-primary" style={{ cursor: 'pointer', display: 'inline-flex' }}>
              <Icon.Upload /> Dosya Sec (.xlsx, .csv)
            </label>
          </div>

          {/* Preview */}
          {uploadPreview && uploadPreview.headers.length > 0 && (
            <div className="card">
              <div className="card-header">
                <h2>Onizleme ({uploadPreview.total_rows} satir)</h2>
                <span className="pill pill-hazirlaniyor">Tespit: {TYPE_LABELS[uploadPreview.detected_type] || uploadPreview.detected_type}</span>
              </div>
              <div style={{ overflowX: 'auto' }}>
                <table className="table">
                  <thead><tr>{uploadPreview.headers.map((h, i) => <th key={i}>{h}</th>)}</tr></thead>
                  <tbody>
                    {uploadPreview.rows.map((row, i) => (
                      <tr key={i}>{row.map((c, j) => <td key={j}>{c != null ? String(c) : ''}</td>)}</tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div style={{ padding: 16, display: 'flex', gap: 10, justifyContent: 'flex-end', borderTop: '1px solid var(--border)' }}>
                <button className="btn-primary" disabled={uploading} onClick={() => {
                  const input = document.getElementById('file-upload')
                  if (input.files[0]) handleImport(input.files[0], uploadPreview.detected_type)
                }}>
                  {uploading ? 'Yukleniyor...' : `${uploadPreview.total_rows} Satiri Ice Aktar`}
                </button>
              </div>
            </div>
          )}

          {/* Result */}
          {uploadResult && (
            <div className="card" style={{ borderColor: uploadResult.success ? 'rgba(22,163,74,0.3)' : 'rgba(239,68,68,0.3)', borderWidth: 2 }}>
              <div className="card-body">
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{ width: 40, height: 40, borderRadius: 10, background: uploadResult.success ? 'var(--primary-light)' : 'rgba(239,68,68,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    {uploadResult.success ? <Icon.Check /> : <Icon.Alert />}
                  </div>
                  <div>
                    <div style={{ fontSize: 16, fontWeight: 700 }}>{uploadResult.success ? 'Basariyla aktarildi!' : 'Hata olustu'}</div>
                    <div style={{ fontSize: 13, color: 'var(--muted)' }}>
                      {TYPE_LABELS[uploadResult.data_type] || uploadResult.data_type} | {uploadResult.imported} kayit aktarildi{uploadResult.skipped > 0 ? `, ${uploadResult.skipped} atlandi` : ''}
                    </div>
                  </div>
                </div>
                {uploadResult.errors?.length > 0 && (
                  <div style={{ marginTop: 12, padding: 10, background: 'rgba(239,68,68,0.05)', borderRadius: 8, fontSize: 12, color: 'var(--destructive)' }}>
                    {uploadResult.errors.map((e, i) => <div key={i}>{e}</div>)}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Instructions */}
          <div className="grid-3">
            <div className="card" style={{ padding: 20 }}>
              <div className="kpi-label" style={{ marginBottom: 8 }}>Urunler</div>
              <p style={{ fontSize: 12, color: 'var(--muted)', lineHeight: 1.6 }}>Kolonlar: <strong>id, ad, kategori, stok, esik, fiyat, birim, tedarikci_id</strong></p>
            </div>
            <div className="card" style={{ padding: 20 }}>
              <div className="kpi-label" style={{ marginBottom: 8 }}>Siparisler</div>
              <p style={{ fontSize: 12, color: 'var(--muted)', lineHeight: 1.6 }}>Kolonlar: <strong>id, musteri, telefon, email, durum, tutar, kargo_takip, kargo_firma</strong></p>
            </div>
            <div className="card" style={{ padding: 20 }}>
              <div className="kpi-label" style={{ marginBottom: 8 }}>Tedarikciler</div>
              <p style={{ fontSize: 12, color: 'var(--muted)', lineHeight: 1.6 }}>Kolonlar: <strong>id, ad, email, telefon</strong></p>
            </div>
          </div>
        </div>
      )
    }

    if (activeTab === "tedarikciler") {
      return (
        <div className="card">
          <div className="card-header" style={{ gap: 12 }}>
            <h2><Icon.Users /> Tedarikçiler ({suppliers.length})</h2>
            <button className="btn-primary" onClick={() => setModal({ type: 'supplier', mode: 'add', data: { name: '', email: '', phone: '' } })}><Icon.Plus /> Tedarikçi Ekle</button>
          </div>
          <table className="table">
            <thead><tr><th>Kod</th><th>Firma</th><th>E-posta</th><th>Telefon</th><th className="text-right">Ürün</th><th style={{width:80}}>İşlem</th></tr></thead>
            <tbody>
              {suppliers.map(s => (
                <tr key={s.id}>
                  <td className="mono" style={{ color: 'var(--muted)' }}>{s.id}</td>
                  <td style={{ fontWeight: 600 }}>{s.name}</td>
                  <td style={{ fontSize: 13 }}>{s.email || '-'}</td>
                  <td style={{ fontSize: 13 }}>{s.phone || '-'}</td>
                  <td className="tabular text-right">{s.product_count}</td>
                  <td>
                    <div style={{ display: 'flex', gap: 4 }}>
                      <button className="btn-icon" title="Düzenle" onClick={() => setModal({ type: 'supplier', mode: 'edit', data: { ...s } })}><Icon.Edit /></button>
                      <button className="btn-icon btn-icon-danger" title="Sil" onClick={() => handleDelete('suppliers', s.id)}><Icon.Trash /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )
    }

    if (activeTab === "whatsapp") {
      return (
        <div className="space-y">
          <div className="card" style={{ padding: 24, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
              <div style={{ width: 48, height: 48, borderRadius: 12, background: 'rgba(37,211,102,0.1)', color: '#25D366', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Icon.MessageCircle />
              </div>
              <div>
                <h2 style={{ fontSize: 18, marginBottom: 4 }}>WhatsApp Entegrasyonu</h2>
                <div style={{ fontSize: 14, color: 'var(--muted)', display: 'flex', alignItems: 'center', gap: 8 }}>
                  Durum: 
                  {waStatus?.is_connected ? (
                    <span style={{ color: 'var(--success)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 4 }}><div style={{ width:8, height:8, borderRadius:'50%', background:'var(--success)' }}></div> Bağlı</span>
                  ) : (
                    <span style={{ color: 'var(--destructive)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 4 }}><div style={{ width:8, height:8, borderRadius:'50%', background:'var(--destructive)' }}></div> Bağlantı Bekleniyor</span>
                  )}
                </div>
              </div>
            </div>
            {waStatus?.phone && (
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: 12, color: 'var(--muted)', marginBottom: 4 }}>Bağlı Numara</div>
                <div className="mono" style={{ fontSize: 16, fontWeight: 600 }}>{waStatus.phone}</div>
              </div>
            )}
          </div>

          <div className="card">
            <div className="card-header">
              <h2><Icon.MessageCircle /> Aktif Görüşmeler ({waSessions.length})</h2>
            </div>
            <table className="table">
              <thead>
                <tr>
                  <th>Müşteri Numarası</th>
                  <th>Son Mesaj Tarihi</th>
                  <th>İşlem</th>
                </tr>
              </thead>
              <tbody>
                {waSessions.map(s => (
                  <tr key={s.session_id}>
                    <td className="mono" style={{ fontWeight: 600 }}>{s.phone}</td>
                    <td>{s.last_message ? new Date(s.last_message).toLocaleString('tr-TR') : '-'}</td>
                    <td>
                      <button className="btn-secondary" onClick={() => window.open(`http://127.0.0.1:8000/chat/history/${s.session_id}`, '_blank')}>
                        Geçmişi Gör
                      </button>
                    </td>
                  </tr>
                ))}
                {waSessions.length === 0 && (
                  <tr>
                    <td colSpan="3" style={{ textAlign: 'center', padding: 40, color: 'var(--muted)' }}>Henüz WhatsApp görüşmesi bulunmuyor.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          
          <div className="card" style={{ padding: 20 }}>
            <h3 style={{ fontSize: 15, marginBottom: 12 }}>Kurulum Bilgisi</h3>
            <p style={{ fontSize: 13, color: 'var(--muted)', lineHeight: 1.6, marginBottom: 12 }}>
              WhatsApp botunu test etmek için Twilio Sandbox kullanıyorsanız, <strong>Twilio Console &gt; Messaging &gt; Settings &gt; WhatsApp Sandbox Settings</strong> sayfasına gidip "When a message comes in" alanına aşağıdaki Webhook URL'sini yapıştırmalısınız.
            </p>
            <div style={{ display: 'flex', gap: 12 }}>
              <input readOnly value={waStatus?.webhook_url || "POST /webhook/whatsapp"} className="input mono" style={{ flex: 1, fontSize: 13, color: 'var(--primary)' }} />
            </div>
            <p style={{ fontSize: 12, color: 'var(--muted)', marginTop: 12 }}>Not: Localhost'ta test ediyorsanız ngrok kullanarak bu URL'yi internete açmanız gerekir (örn: <code>https://&lt;id&gt;.ngrok.app/webhook/whatsapp</code>).</p>
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

      {/* CRUD Modal */}
      {modal && <CrudModal modal={modal} setModal={setModal} apiCall={apiCall} />}
    </div>
  )
}


// ── CRUD Modal Component ─────────────────────────────────────────────────────

function CrudModal({ modal, setModal, apiCall }) {
  const [form, setForm] = useState(modal.data)
  const [saving, setSaving] = useState(false)

  const set = (k, v) => setForm(prev => ({ ...prev, [k]: v }))

  const handleSave = async () => {
    setSaving(true)
    const t = modal.type === 'product' ? 'products' : modal.type === 'order' ? 'orders' : 'suppliers'
    if (modal.mode === 'add') {
      await apiCall(`/${t}`, 'POST', form)
    } else {
      await apiCall(`/${t}/${form.id}`, 'PUT', form)
    }
    setSaving(false)
    setModal(null)
  }

  const title = modal.mode === 'add' ? 'Yeni Ekle' : 'Düzenle'
  const inputStyle = { width: '100%', padding: '10px 14px', border: '1px solid var(--border)', borderRadius: 10, fontSize: 14, background: 'var(--bg)', color: 'var(--text)' }
  const labelStyle = { fontSize: 12, fontWeight: 600, color: 'var(--muted)', marginBottom: 4, display: 'block' }

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }} onClick={() => setModal(null)}>
      <div style={{ background: 'var(--card)', borderRadius: 16, padding: 28, width: '100%', maxWidth: 480, maxHeight: '90vh', overflowY: 'auto', boxShadow: '0 20px 60px rgba(0,0,0,0.3)' }} onClick={e => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
          <h2 style={{ fontSize: 18, fontWeight: 700 }}>{title}</h2>
          <button className="btn-icon" onClick={() => setModal(null)}><Icon.X /></button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {modal.type === 'product' && <>
            <div><label style={labelStyle}>Ürün Adı *</label><input style={inputStyle} value={form.name || ''} onChange={e => set('name', e.target.value)} /></div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div><label style={labelStyle}>Kategori</label><input style={inputStyle} value={form.category || ''} onChange={e => set('category', e.target.value)} /></div>
              <div><label style={labelStyle}>Birim</label><input style={inputStyle} value={form.unit || ''} onChange={e => set('unit', e.target.value)} /></div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
              <div><label style={labelStyle}>Stok</label><input style={inputStyle} type="number" value={form.stock_quantity ?? 0} onChange={e => set('stock_quantity', +e.target.value)} /></div>
              <div><label style={labelStyle}>Kritik Eşik</label><input style={inputStyle} type="number" value={form.low_threshold ?? 10} onChange={e => set('low_threshold', +e.target.value)} /></div>
              <div><label style={labelStyle}>Fiyat (TL)</label><input style={inputStyle} type="number" step="0.01" value={form.unit_price ?? 0} onChange={e => set('unit_price', +e.target.value)} /></div>
            </div>
          </>}

          {modal.type === 'order' && <>
            <div><label style={labelStyle}>Müşteri Adı *</label><input style={inputStyle} value={form.customer_name || ''} onChange={e => set('customer_name', e.target.value)} /></div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div><label style={labelStyle}>Telefon</label><input style={inputStyle} value={form.customer_phone || ''} onChange={e => set('customer_phone', e.target.value)} /></div>
              <div><label style={labelStyle}>E-posta</label><input style={inputStyle} value={form.customer_email || ''} onChange={e => set('customer_email', e.target.value)} /></div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div><label style={labelStyle}>Durum</label>
                <select style={inputStyle} value={form.status || 'beklemede'} onChange={e => set('status', e.target.value)}>
                  <option value="beklemede">Beklemede</option><option value="hazirlaniyor">Hazırlanıyor</option>
                  <option value="kargoda">Kargoda</option><option value="teslim_edildi">Teslim Edildi</option><option value="iptal">İptal</option>
                </select>
              </div>
              <div><label style={labelStyle}>Tutar (TL)</label><input style={inputStyle} type="number" step="0.01" value={form.total_amount ?? 0} onChange={e => set('total_amount', +e.target.value)} /></div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div><label style={labelStyle}>Kargo Takip No</label><input style={inputStyle} value={form.tracking_number || ''} onChange={e => set('tracking_number', e.target.value)} /></div>
              <div><label style={labelStyle}>Kargo Firması</label><input style={inputStyle} value={form.cargo_company || ''} onChange={e => set('cargo_company', e.target.value)} /></div>
            </div>
            <div><label style={labelStyle}>Not</label><input style={inputStyle} value={form.notes || ''} onChange={e => set('notes', e.target.value)} /></div>
          </>}

          {modal.type === 'supplier' && <>
            <div><label style={labelStyle}>Firma Adı *</label><input style={inputStyle} value={form.name || ''} onChange={e => set('name', e.target.value)} /></div>
            <div><label style={labelStyle}>E-posta</label><input style={inputStyle} value={form.email || ''} onChange={e => set('email', e.target.value)} /></div>
            <div><label style={labelStyle}>Telefon</label><input style={inputStyle} value={form.phone || ''} onChange={e => set('phone', e.target.value)} /></div>
          </>}
        </div>

        <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end', marginTop: 24 }}>
          <button className="btn-secondary" onClick={() => setModal(null)}>İptal</button>
          <button className="btn-primary" disabled={saving} onClick={handleSave}>{saving ? 'Kaydediliyor...' : 'Kaydet'}</button>
        </div>
      </div>
    </div>
  )
}
