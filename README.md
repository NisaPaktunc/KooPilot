# Koopilot AI 🚀

Koopilot, KOBİ'ler (Küçük ve Orta Büyüklükteki İşletmeler) ve kooperatifler için geliştirilmiş, tam kapsamlı ve **Yapay Zeka Destekli bir İşletme Yönetim Platformudur**. 

Bu proje, geleneksel bir yönetim panelini (React) alıp, arka planda çalışan zeki bir yapay zeka asistanı (Gemini AI) ve WhatsApp Webhook (Twilio) entegrasyonu ile birleştirir. İşletme sahibi, stok durumunu, sipariş analizlerini ve finansal özetleri doğrudan WhatsApp üzerinden yapay zekaya sorabilir ve platform otonom olarak veritabanına bağlanıp işlemleri gerçekleştirir.

---

## ✨ Öne Çıkan Özellikler

- **Gelişmiş Yönetim Paneli (React):** Ürün, Sipariş ve Tedarikçi yönetimi için dinamik, modern ve tam CRUD destekli arayüz.
- **WhatsApp İşletme Asistanı:** Müşterilerin sipariş/kargo sorguladığı, yöneticilerin ise WhatsApp üzerinden satış analizi alabildiği otonom asistan.
- **Yapay Zeka (Function Calling):** Gemini AI, doğal dildeki soruları anlar ve arka planda `check_stock`, `get_sales_analytics`, `get_stock_forecast` gibi Python fonksiyonlarını otonom olarak tetikler.
- **Veri Analitiği ve Sağlık Skoru:** İşletmenin veritabanındaki (SQLite/SQLAlchemy) finansal durumu analiz edilerek anlık kar optimizasyon raporları oluşturulur.
- **Tam Senkronizasyon:** WhatsApp üzerinden yapılan işlemler, anlık olarak Admin Dashboard'a yansır.

---

## 🏗️ Sistem Mimarisi

KooPilot, ölçeklenebilir ve modern bir tam yığın (full-stack) mimarisi üzerine inşa edilmiştir. Sistem 4 ana katmandan oluşur:

1. **İstemci (Frontend) Katmanı:**
   - **React & Vite:** Yüksek performanslı ve modüler kullanıcı arayüzü (UI).
   - Tam CRUD (Create, Read, Update, Delete) operasyonları ile ürün, stok, sipariş ve tedarikçi yönetimi.
2. **Sunucu (Backend) Katmanı:**
   - **FastAPI (Python):** Asenkron yapısı sayesinde yüksek hızlı RESTful API hizmeti sağlar.
   - **BackgroundTasks:** Twilio Webhook zaman aşımlarını (timeout) önlemek için yapay zeka analizlerini arka planda işler.
3. **Veri (Database) Katmanı:**
   - **SQLAlchemy & SQLite:** Siparişler, ürünler, stok eşikleri ve konuşma geçmişleri ilişkisel (relational) bir veritabanı şemasında tutulur. Pydantic ile veri doğrulaması (validation) yapılır.
4. **Yapay Zeka ve İletişim (AI & Comm) Katmanı:**
   - **Google Gemini API:** `Function Calling` yeteneği sayesinde doğal dilden gelen istekleri analiz eder ve Python fonksiyonlarını tetikler (Otonom Agent).
   - **Twilio API:** WhatsApp üzerinden gelen mesajları Webhook aracılığıyla sisteme iletir ve AI'ın ürettiği yanıtları kullanıcıya döndürür.

**🔄 İşlem Akışı (Data Flow):**  
`Kullanıcı (WhatsApp) ➡️ Twilio Webhook ➡️ FastAPI ➡️ Gemini AI (Niyet Analizi) ➡️ Function Call (DB Sorgusu) ➡️ Gemini (Yanıt Üretimi) ➡️ Twilio ➡️ Kullanıcı`

---

## 🧠 Yapay Zeka Yaklaşımı (AI Approach)

KooPilot, basit bir Soru-Cevap (Q&A) botu yerine, proaktif ve aksiyon alabilen bir **Agentic AI (Ajan Yapay Zeka)** yaklaşımı kullanır:

1. **Function Calling (Araç Kullanımı):** Yapay zeka modeli sadece metin üretmez; aynı zamanda kullanıcının niyetini anlar (Intent Recognition) ve bizim tanımladığımız Python fonksiyonlarını (`check_stock`, `get_cargo_status` vb.) tetikler.
2. **Doğal Dil ile Veritabanı Etkileşimi:** Kullanıcının "Siparişim nerede?" gibi doğal dildeki soruları, AI tarafından otomatik olarak veri tabanı sorgularına dönüştürülür ve çekilen gerçek veriler anlamlı bir dille kullanıcıya sunulur.
3. **Bağlam Yönetimi (Context & Memory):** Her kullanıcının telefon numarası benzersiz bir `session_id` olarak kabul edilir. AI, konuşma geçmişini hafızasında tutarak diyaloğun bağlamından kopmaz.
4. **Güvenli Veri İşleme:** Veritabanının tamamı modele gönderilmez. Sadece kullanıcının sorduğu konuyla ilgili nokta atışı kayıtlar (örneğin yalnızca bir siparişin detayı) modele iletilir. Bu sayede hem güvenlik sağlanır hem de token tasarrufu yapılır.

---

## 🛠️ Kurulum ve Çalıştırma

### 1. Ortam Değişkenleri (.env)
Projenin çalışması için backend klasörü içerisinde bir `.env` dosyası oluşturmalısınız. (Şifrelerinizi ve API anahtarlarınızı Github'a atmamak için `.gitignore` dosyasında `.env` gizlenmiştir).

`backend/.env` dosyanızı şu formatta oluşturun:

```env
GEMINI_API_KEY=your_gemini_api_key_here
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
TWILIO_MANAGER_PHONE=whatsapp:+905550000000
```

### 2. Sunucuları Başlatma
Projede iki ayrı sunucu bulunur (FastAPI ve Vite). İki farklı terminalde aşağıdaki komutları çalıştırın:

**Backend (Terminal 1):**
```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows için
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend (Terminal 2):**
```bash
cd frontend
npm install
npm run dev
```

### 3. WhatsApp Entegrasyonu (Cloudflare Tüneli)
WhatsApp botunu lokal makinenizde (Localhost) test edebilmek için Twilio'ya dışa açık bir URL (Webhook) sağlamanız gerekir. Bunun için en güvenli yol Cloudflare Tunnel kullanmaktır.

**Terminal 3 (Tünel):**
```bash
npx untun tunnel http://localhost:8000
```
Bu komut size `https://rastgele-kelime.trycloudflare.com` gibi bir adres verecektir.

1. [Twilio Console](https://console.twilio.com/)'a gidin.
2. **Messaging > Try it out > Send a WhatsApp message** sekmesine (Sandbox) girin.
3. "WHEN A MESSAGE COMES IN" kısmına tünelin verdiği adresi yapıştırıp sonuna `/webhook/whatsapp` ekleyin.
   *(Örn: `https://...trycloudflare.com/webhook/whatsapp`)*
4. Kaydedin. WhatsApp üzerinden ekrandaki "join..." kodunu göndererek botu test etmeye başlayın!

---

## 🤖 AI Asistanın Sahip Olduğu Yetenekler (Tools)

WhatsApp'tan aşağıdaki gibi sorular sorduğunuzda AI ilgili fonksiyonu çalıştırır:
* **Stok Durumu (`check_stock`):** "Zeytinyağı stoklarımız ne durumda?"
* **Satış Analitiği (`get_sales_analytics`):** "Bana bugünün satış analitiklerini ve en çok satan 5 ürünü listele."
* **Stok Tahmini (`get_stock_forecast`):** "Hangi ürünlerin stoğu yakında bitecek? Tahmin alabilir miyim?"
* **Kargo Sorgulama (`get_cargo_status`):** "TRK-4891 nolu kargom ne zaman gelir?"
* **Akıllı Analiz (`run_smart_analysis`):** "İşletmenin genel sağlık skoru nasıl, bana eyleme dönüştürülebilir bir analiz yap."

---

## 🔒 Güvenlik Notu (Github'a Yüklerken)
`.env` dosyanız projenin kök dizinindeki `.gitignore` dosyası sayesinde otomatik olarak gizlenmektedir. **Git push** işlemi yaptığınızda kişisel API anahtarlarınız (Twilio, Gemini) GitHub reposuna gönderilmez. Başka geliştiricilerin projeyi kurabilmesi için şifresiz hali `backend/.env.example` dosyasında bırakılmıştır.
