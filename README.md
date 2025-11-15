# Toplantı Planlama Yardımcısı (Meeting Planner Assistant)

Microsoft Graph API kullanarak katılımcıların takvimlerini analiz eden ve en uygun toplantı zamanlarını öneren bir yardımcı servis.

> 💡 **Microsoft Graph erişiminiz yok mu?** Endişelenmeyin! Mock Mode ile sistemi tam olarak test edebilirsiniz. [Mock Mode Rehberi](MOCK_MODE_GUIDE.md) için tıklayın.

## 🎯 Özellikler

- ✅ Katılımcıların takvim uygunluğunu sorgulama
- ✅ Belirtilen tarih ve saat aralığında en uygun zamanları bulma
- ✅ En yüksek katılım oranına sahip 3-5 zaman dilimi önerisi
- ✅ Teams toplantısı otomatik oluşturma
- ✅ REST API ile Copilot Studio entegrasyonu

## 📋 Gereksinimler

- Python 3.8+
- Microsoft 365 hesabı
- Azure AD App Registration (Client ID, Client Secret, Tenant ID)

## 🚀 Kurulum

### Hızlı Başlangıç (Mock Mode - Graph API Gerektirmez)

```powershell
# 1. Bağımlılıkları yükle
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. .env dosyası oluştur
Copy-Item .env.template .env

# 3. .env dosyasında USE_MOCK_API=True olduğundan emin ol
# (Varsayılan olarak zaten True)

# 4. Hemen çalıştır!
python app.py
```

✅ Mock mode ile **Graph API credentials olmadan** çalışır!
📚 Detaylı bilgi: [MOCK_MODE_GUIDE.md](MOCK_MODE_GUIDE.md)

---

### Production Kurulum (Gerçek Graph API ile)

### 1. Bağımlılıkları Yükleyin

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Azure AD App Registration Oluşturun

> **Not:** Mock Mode kullanıyorsanız bu adımı atlayabilirsiniz. [Hızlı Başlangıç](#hızlı-başlangıç-mock-mode---graph-api-gerektirmez) bölümüne bakın.

1. [Azure Portal](https://portal.azure.com) → **Azure Active Directory** → **App registrations** → **New registration**
2. Uygulama adı: `Meeting Planner Assistant`
3. Supported account types: `Accounts in this organizational directory only`
4. **Register** butonuna tıklayın

### 3. API İzinlerini Ayarlayın

App Registration sayfasında:
1. **API permissions** → **Add a permission** → **Microsoft Graph** → **Application permissions**
2. Şu izinleri ekleyin:
   - `Calendars.Read`
   - `Calendars.ReadWrite`
   - `User.Read.All`
3. **Grant admin consent** butonuna tıklayın

### 4. Client Secret Oluşturun

1. **Certificates & secrets** → **New client secret**
2. Description: `Meeting Planner Secret`
3. Expires: Uygun süreyi seçin
4. **Add** → Secret'ı kopyalayın (bir daha göremezsiniz!)

### 5. Ortam Değişkenlerini Ayarlayın

`.env.template` dosyasını `.env` olarak kopyalayın ve bilgilerinizi girin:

```powershell
Copy-Item .env.template .env
```

`.env` dosyasını düzenleyin:

```env
# Mock Mode - Test için (Graph API gerektirmez)
USE_MOCK_API=True

# Production Mode - Gerçek Graph API kullanımı için
# USE_MOCK_API=False
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here
TENANT_ID=your_tenant_id_here

FLASK_PORT=5000
FLASK_DEBUG=True
```

**Değerleri bulmak için:**
- `CLIENT_ID`: App Registration → Overview → Application (client) ID
- `TENANT_ID`: App Registration → Overview → Directory (tenant) ID
- `CLIENT_SECRET`: Adım 4'te kopyaladığınız değer

## 💻 Kullanım

### Servisi Başlatın

```powershell
python app.py
```

**Mock Mode'da:**
```
⚠️  Running in MOCK MODE - No real Graph API calls will be made
Starting Meeting Planner Assistant API on port 5000
```

**Production Mode'da:**
```
Configuration validated successfully
Starting Meeting Planner Assistant API on port 5000
```

Servis `http://localhost:5000` adresinde çalışacaktır.

### Mode Kontrolü

API'nin hangi modda çalıştığını kontrol edin:
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/health"
```

Yanıt `"mode": "MOCK"` veya `"mode": "PRODUCTION"` döner.

### API Endpoint'leri

#### 1. Uygun Toplantı Zamanlarını Bulma

**Endpoint:** `POST /api/find-meeting-times`

**Request Body:**
```json
{
  "startDate": "2025-11-18",
  "endDate": "2025-11-22",
  "timeRange": "09:00-17:00",
  "participants": [
    "user1@company.com",
    "user2@company.com",
    "user3@company.com"
  ],
  "duration": 60
}
```

**Response:**
```json
{
  "success": true,
  "suggestions": [
    {
      "start_time": "2025-11-19T10:00:00+03:00",
      "end_time": "2025-11-19T11:00:00+03:00",
      "available_count": 3,
      "total_participants": 3,
      "availability_percentage": 100.0,
      "available_participants": [
        "user1@company.com",
        "user2@company.com",
        "user3@company.com"
      ],
      "busy_participants": [],
      "formatted": "19 Kasım 2025, 10:00 - 11:00 (3/3 katılımcı uygun, %100)"
    }
  ],
  "total_slots_analyzed": 45
}
```

**PowerShell Örneği:**
```powershell
$body = @{
    startDate = "2025-11-18"
    endDate = "2025-11-22"
    timeRange = "09:00-17:00"
    participants = @(
        "user1@company.com",
        "user2@company.com"
    )
    duration = 60
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/find-meeting-times" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

#### 2. Toplantı Oluşturma

**Endpoint:** `POST /api/create-meeting`

**Request Body:**
```json
{
  "subject": "Proje Toplantısı",
  "startTime": "2025-11-19T10:00:00",
  "endTime": "2025-11-19T11:00:00",
  "attendees": [
    "user1@company.com",
    "user2@company.com"
  ],
  "body": "Proje durumu ve sonraki adımlar hakkında konuşacağız."
}
```

**Response:**
```json
{
  "success": true,
  "meeting": {
    "id": "AAMkAGI...",
    "webLink": "https://outlook.office365.com/...",
    "onlineMeeting": {
      "joinUrl": "https://teams.microsoft.com/l/meetup-join/..."
    },
    "subject": "Proje Toplantısı",
    "start": {
      "dateTime": "2025-11-19T10:00:00",
      "timeZone": "Europe/Istanbul"
    },
    "end": {
      "dateTime": "2025-11-19T11:00:00",
      "timeZone": "Europe/Istanbul"
    }
  }
}
```

**PowerShell Örneği:**
```powershell
$body = @{
    subject = "Proje Toplantısı"
    startTime = "2025-11-19T10:00:00"
    endTime = "2025-11-19T11:00:00"
    attendees = @("user1@company.com", "user2@company.com")
    body = "Toplantı detayları"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/create-meeting" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

#### 3. Belirli Zaman Dilimi için Uygunluk Kontrolü

**Endpoint:** `POST /api/check-availability`

**Request Body:**
```json
{
  "participants": [
    "user1@company.com",
    "user2@company.com"
  ],
  "startTime": "2025-11-19T10:00:00",
  "endTime": "2025-11-19T11:00:00"
}
```

**Response:**
```json
{
  "success": true,
  "availability": {
    "available_count": 2,
    "total_participants": 2,
    "availability_percentage": 100.0,
    "available_participants": [
      "user1@company.com",
      "user2@company.com"
    ],
    "busy_participants": []
  }
}
```

## 🤖 Copilot Studio Entegrasyonu

### 1. Custom Action Oluşturma

Copilot Studio'da:

1. **Topics** → **Add Action** → **Create from blank**
2. Action tipi: **HTTP Request**
3. Yapılandırma:

**Toplantı Zamanı Bulma Action:**
```
Name: FindMeetingTimes
Method: POST
URL: http://your-server:5000/api/find-meeting-times
Headers:
  Content-Type: application/json
Body:
{
  "startDate": "{{Topic.StartDate}}",
  "endDate": "{{Topic.EndDate}}",
  "timeRange": "{{Topic.TimeRange}}",
  "participants": {{Topic.Participants}},
  "duration": {{Topic.Duration}}
}
```

**Toplantı Oluşturma Action:**
```
Name: CreateMeeting
Method: POST
URL: http://your-server:5000/api/create-meeting
Headers:
  Content-Type: application/json
Body:
{
  "subject": "{{Topic.Subject}}",
  "startTime": "{{Topic.StartTime}}",
  "endTime": "{{Topic.EndTime}}",
  "attendees": {{Topic.Attendees}},
  "body": "{{Topic.Body}}"
}
```

### 2. Topic Oluşturma

**Örnek Konuşma Akışı:**

```
User: Önümüzdeki hafta için toplantı ayarlamak istiyorum
Bot: Tabii! Şu bilgilere ihtiyacım var:
     - Tarih aralığı (örn. 2025-11-18 ile 2025-11-22)
     - Saat aralığı (örn. 09:00-17:00)
     - Katılımcıların e-posta adresleri
     - Toplantı süresi (dakika)

User: 18-22 Kasım, 09:00-17:00, user1@company.com ve user2@company.com, 60 dakika
Bot: [FindMeetingTimes Action çağrılır]
     Uygun zamanları buldum:
     1. 19 Kasım 2025, 10:00 - 11:00 (2/2 katılımcı uygun, %100)
     2. 19 Kasım 2025, 14:00 - 15:00 (2/2 katılımcı uygun, %100)
     3. 20 Kasım 2025, 11:00 - 12:00 (2/2 katılımcı uygun, %100)
     
     Hangi zamanı seçmek istersiniz?

User: Birinci seçenek
Bot: Toplantı konusu ne olsun?
User: Proje Değerlendirme
Bot: [CreateMeeting Action çağrılır]
     Toplantınız oluşturuldu! Teams linki: [link]
```

### 3. Değişken Mapping

Copilot Studio'da değişkenleri şöyle tanımlayın:

| Değişken | Tip | Açıklama |
|----------|-----|----------|
| `StartDate` | String | Başlangıç tarihi (YYYY-MM-DD) |
| `EndDate` | String | Bitiş tarihi (YYYY-MM-DD) |
| `TimeRange` | String | Saat aralığı (HH:MM-HH:MM) |
| `Participants` | Array | E-posta adresleri listesi |
| `Duration` | Number | Toplantı süresi (dakika) |
| `Subject` | String | Toplantı konusu |
| `StartTime` | String | Seçilen başlangıç zamanı |
| `EndTime` | String | Seçilen bitiş zamanı |

## 🔧 Production Deployment

### Azure App Service'e Deploy

1. **Azure App Service Oluşturun:**
```powershell
az webapp create --resource-group myResourceGroup `
    --plan myAppServicePlan `
    --name meeting-planner-api `
    --runtime "PYTHON:3.11"
```

2. **Environment Variables Ayarlayın:**
```powershell
az webapp config appsettings set --resource-group myResourceGroup `
    --name meeting-planner-api `
    --settings CLIENT_ID="your_id" CLIENT_SECRET="your_secret" TENANT_ID="your_tenant"
```

3. **Deploy Edin:**
```powershell
az webapp up --resource-group myResourceGroup `
    --name meeting-planner-api
```

### Docker ile Deployment

Dockerfile oluşturun:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

Build ve Run:
```powershell
docker build -t meeting-planner .
docker run -p 5000:5000 --env-file .env meeting-planner
```

## 📊 Nasıl Çalışır?

1. **Takvim Sorgusu**: Microsoft Graph API'nin `getSchedule` endpoint'i kullanılarak katılımcıların uygunluk durumu alınır
2. **Analiz**: Her zaman dilimi için katılım sayısı hesaplanır (0=Boş, 1=Geçici, 2=Meşgul)
3. **Sıralama**: En yüksek katılım oranına sahip zamanlar öne çıkarılır
4. **Öneri**: En iyi 3-5 zaman dilimi döndürülür
5. **Oluşturma**: Onay sonrası Teams toplantısı otomatik oluşturulur

## 🛠️ Troubleshooting

### "Authentication failed" hatası
- Azure AD'de uygulama izinlerinin verildiğinden emin olun
- Admin consent'in grant edildiğini kontrol edin
- Client Secret'ın doğru ve süresi dolmamış olduğunu doğrulayın

### "Insufficient privileges" hatası
- API Permissions'da gerekli tüm izinlerin eklendiğinden emin olun
- Application permissions (değil Delegated permissions) kullandığınızdan emin olun

### Katılımcı takvimi görünmüyor
- Kullanıcıların Exchange Online lisansı olduğundan emin olun
- Takvim paylaşım ayarlarını kontrol edin

## 📝 Lisans

MIT License

## 🤝 Katkıda Bulunma

Pull request'ler kabul edilir. Büyük değişiklikler için lütfen önce bir issue açın.

## 📧 İletişim

Sorularınız için issue açabilirsiniz.
