import { useState, useEffect, useRef } from "react"

const API = "http://127.0.0.1:8000"

export function useNotifications() {
  const [notifications, setNotifications] = useState([])
  const [unread, setUnread] = useState(0)
  const wsRef = useRef(null)

  // İlk yükleme
  const fetchNotifications = async () => {
    try {
      const res = await fetch(`${API}/notifications`)
      const data = await res.json()
      setNotifications(data)
      setUnread(data.filter(n => !n.is_read).length)
    } catch (e) {
      console.error("Bildirimler alınamadı:", e)
    }
  }

  useEffect(() => {
    fetchNotifications()

    // WebSocket bağlantısı
    const connect = () => {
      try {
        const ws = new WebSocket("ws://127.0.0.1:8000/ws/notifications")
        wsRef.current = ws

        ws.onmessage = (e) => {
          try {
            const notif = JSON.parse(e.data)
            if (notif.type === "new_notification") {
              setNotifications(prev => [{
                id:         notif.id,
                title:      notif.title,
                message:    notif.message,
                priority:   notif.priority,
                type:       notif.notif_type || "genel",
                is_read:    false,
                created_at: new Date().toISOString(),
              }, ...prev])
              setUnread(prev => prev + 1)
            }
          } catch {}
        }

        ws.onclose = () => {
          // 3 saniye sonra yeniden bağlan
          setTimeout(connect, 3000)
        }

        ws.onerror = () => ws.close()
      } catch {}
    }

    connect()

    // WebSocket yoksa polling fallback (5sn)
    const interval = setInterval(fetchNotifications, 5000)

    return () => {
      clearInterval(interval)
      wsRef.current?.close()
    }
  }, [])

  const markRead = async (id) => {
    await fetch(`${API}/notifications/${id}/read`, { method: "PATCH" })
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n))
    setUnread(prev => Math.max(0, prev - 1))
  }

  const markAllRead = async () => {
    await fetch(`${API}/notifications/read-all`, { method: "PATCH" })
    setNotifications(prev => prev.map(n => ({ ...n, is_read: true })))
    setUnread(0)
  }

  return { notifications, unread, markRead, markAllRead, refetch: fetchNotifications }
}
