# Koopilot AI - WhatsApp Integration

Koopilot, küçük işletmeler ve kooperatifler için geliştirilmiş yapay zeka destekli bir operasyon asistanıdır.
Yeni eklenen **WhatsApp AI Entegrasyonu** sayesinde kullanıcılar doğrudan WhatsApp üzerinden siparişlerini sorgulayabilir, kargo durumlarını takip edebilir ve yapay zeka ile doğal dilde iletişim kurabilir.

## 🚀 Kurulum ve Çalıştırma

### 1. Ortam Değişkenleri (.env)
Aşağıdaki değişkenleri `backend/.env` dosyanıza ekleyin:

```env
GEMINI_API_KEY=your_gemini_api_key
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

### 2. Twilio WhatsApp Sandbox Kurulumu
Twilio üzerinden WhatsApp API'sini kullanmak için Sandbox ortamı gereklidir:

1. [Twilio Console](https://console.twilio.com/) üzerinde bir hesap oluşturun.
2. Messaging -> Try it out -> Send a WhatsApp message menüsüne gidin.
3. Kendi telefonunuzdan Twilio Sandbox numarasına (örn: `+14155238886`) ekrandaki özel kodu (örn: `join whatever-word`) göndererek Sandbox'a katılın.

### 3. Local Test ve ngrok Kullanımı
WhatsApp entegrasyonunu kendi bilgisayarınızda test etmek için yerel sunucunuzu dışarı açmanız gerekir:

1. Backend sunucusunu başlatın:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```
2. Başka bir terminalde `ngrok` ile 8000 portunu dışa açın:
   ```bash
   ngrok http 8000
   ```
3. ngrok'un size verdiği URL'i (örn: `https://abcd-12-34.ngrok.io`) kopyalayın.
4. Twilio Console > WhatsApp Sandbox ayarlarında, "WHEN A MESSAGE COMES IN" alanına şu Webhook URL'sini yapıştırın:
   ```text
   https://abcd-12-34.ngrok.io/webhook/whatsapp
   ```
5. Kaydedin ve WhatsApp'tan Sandbox numarasına mesaj atarak test edin!

### 4. Production Deployment (Railway)
Proje Railway üzerinden tek tıkla yayınlanmaya (deploy) hazırdır. 

1. Projeyi GitHub'a yükleyin.
2. Railway'de yeni bir proje oluşturup GitHub deponuzu bağlayın.
3. **Önemli:** Railway projesinin "Root Directory" ayarını `/backend` olarak belirleyin veya Railway'in `backend/Procfile` dosyasını gördüğünden emin olun.
4. Railway ortam değişkenlerine (Variables) `.env` dosyanızdaki `GEMINI_API_KEY`, `TWILIO_ACCOUNT_SID` vb. değerleri girin.
5. Railway'in ürettiği public URL'yi alın (örn: `https://koopilot.up.railway.app`).
6. Twilio Sandbox veya Production WhatsApp Sender ayarlarında Webhook URL'yi bu adrese göre güncelleyin:
   ```text
   https://koopilot.up.railway.app/webhook/whatsapp
   ```

## 🛠️ Mimari Notlar
- WhatsApp mesajları FastAPI `BackgroundTasks` kullanılarak asenkron olarak işlenir, böylece Twilio'nun timeout süresine takılmazsınız.
- Yapay zeka (Gemini 2.5 Flash), kullanıcının telefon numarasını `session_id` olarak kullanarak konuşma geçmişini (memory) hatırlar.
- AI, stok sorgusu (`check_stock`), sipariş (`get_order_status`) ve kargo durumu (`get_cargo_status`) tool'larını otomatik olarak kullanabilir.
