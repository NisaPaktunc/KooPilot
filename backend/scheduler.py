import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from services.tools import get_daily_summary, get_stock_forecast
from integrations.whatsapp import send_whatsapp_message

logger = logging.getLogger(__name__)

# Istanbul saat dilimi ayarı
istanbul_tz = timezone("Europe/Istanbul")

# Global scheduler örneği
scheduler = BackgroundScheduler(timezone=istanbul_tz)

def send_daily_report():
    """
    Her sabah yöneticiye özet ve stok tahmini gönderen ana görev.
    """
    logger.info("⏰ Günlük rapor gönderim görevi tetiklendi.")
    
    manager_phone = os.getenv("TWILIO_MANAGER_PHONE")
    if not manager_phone:
        logger.error("❌ TWILIO_MANAGER_PHONE environment değişkeni bulunamadı! Lütfen .env dosyasını kontrol edin.")
        return

    try:
        # services/tools.py'dan verileri çekiyoruz
        summary = get_daily_summary("")
        forecast = get_stock_forecast("")
        
        # Mesajı birleştiriyoruz
        full_message = f"🌅 *KooPilot Günlük Rapor*\n\n{summary}\n\n{forecast}"
        
        # integrations/whatsapp.py üzerinden mesajı gönderiyoruz
        success = send_whatsapp_message(manager_phone, full_message)
        
        if success:
            logger.info(f"✅ Günlük rapor {manager_phone} numarasına başarıyla iletildi.")
        else:
            logger.error("❌ Günlük rapor WhatsApp üzerinden gönderilemedi.")
            
    except Exception as e:
        logger.error(f"❌ Rapor hazırlama sırasında hata oluştu: {e}")

def start_scheduler():
    """
    Scheduler'ı başlatır ve günlük görevi tanımlar.
    """
    if not scheduler.running:
        # Her gün saat 08:00'de çalışacak şekilde ayarla
        scheduler.add_job(
            send_daily_report,
            trigger=CronTrigger(hour=8, minute=0, timezone=istanbul_tz),
            id="daily_summary_report",
            replace_existing=True
        )
        scheduler.start()
        logger.info("📅 Background Scheduler başlatıldı (Her gün 08:00 Europe/Istanbul).")

def stop_scheduler():
    """
    Scheduler'ı güvenli bir şekilde durdurur.
    """
    if scheduler.running:
        scheduler.shutdown()
        logger.info("📅 Background Scheduler durduruldu.")
