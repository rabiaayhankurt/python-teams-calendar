# Mock Mode Kullanım Rehberi

Bu rehber, Microsoft Graph API erişimi olmadan sistemi test etmek için Mock Mode'u nasıl kullanacağınızı gösterir.

## 🎭 Mock Mode Nedir?

Mock Mode, gerçek Microsoft Graph API'ye bağlanmadan sisteminizi test etmenizi sağlar. Sahte (ancak gerçekçi) veriler üretir:
- ✅ Katılımcı uygunluk verileri
- ✅ Toplantı önerileri  
- ✅ Toplantı oluşturma simülasyonu

## 🚀 Hızlı Başlangıç

### 1. Mock Mode'u Aktif Edin

`.env` dosyasını oluşturun:
```powershell
Copy-Item .env.template .env
```

`.env` dosyasını düzenleyin:
```env
# Mock Mode'u aktif et
USE_MOCK_API=True

# Graph API bilgileri gerekmez (mock mode'da)
CLIENT_ID=not_required_in_mock_mode
CLIENT_SECRET=not_required_in_mock_mode
TENANT_ID=not_required_in_mock_mode

FLASK_PORT=5000
FLASK_DEBUG=True
```

### 2. API'yi Başlatın

```powershell
python app.py
```

Şu mesajı göreceksiniz:
```
⚠️  Running in MOCK MODE - No real Graph API calls will be made
⚠️  MOCK MODE: Using simulated data (no real Graph API calls)
Starting Meeting Planner Assistant API on port 5000
```

### 3. Test Edin

```powershell
python test_api.py
```

## 🔄 Mock Mode ↔️ Production Geçişi

### Mock Mode'a Geçiş
```powershell
# .env dosyasında
USE_MOCK_API=True

# Veya environment variable ile
$env:USE_MOCK_API="True"
python app.py
```

### Production Mode'a Geçiş
```powershell
# .env dosyasında
USE_MOCK_API=False
CLIENT_ID=your_actual_client_id
CLIENT_SECRET=your_actual_secret
TENANT_ID=your_actual_tenant_id

# Veya environment variable ile
$env:USE_MOCK_API="False"
python app.py
```

## 📊 Mock Data Davranışı

### Availability (Uygunluk)

Mock mode gerçekçi takvim verileri üretir:
- **%60 Free (Boş)** - Katılımcı uygun
- **%15 Tentative (Geçici)** - Katılımcı muhtemelen uygun
- **%20 Busy (Meşgul)** - Katılımcı müsait değil
- **%5 Out of Office (Ofis Dışı)** - Katılımcı izinde/dışarıda

### Meeting Suggestions (Öneriler)

Mock mode 5 farklı zaman önerisi döner:
- Hafta sonları otomatik atlanır
- Her öneri farklı saatlerde (10:00, 12:00, 14:00, vb.)
- Katılımcı uygunluğu rastgele ancak gerçekçi şekilde dağıtılır

### Meeting Creation (Toplantı Oluşturma)

Mock mode simüle edilmiş toplantı oluşturur:
- Benzersiz `MOCK_EVENT_` ID'si
- Sahte Teams linki (https://teams.microsoft.com/l/meetup-join/mock/...)
- Tüm attendee ve metadata bilgileri dahil
- **ÖNEMLİ:** Gerçek toplantı oluşturulmaz, sadece API yanıtı döner

## 🧪 Test Senaryoları

### Örnek 1: Toplantı Zamanı Bulma

```powershell
$body = @{
    startDate = "2025-11-18"
    endDate = "2025-11-22"
    timeRange = "09:00-17:00"
    participants = @(
        "user1@example.com",
        "user2@example.com",
        "user3@example.com"
    )
    duration = 60
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/find-meeting-times" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

**Mock Yanıt:**
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
      "formatted": "19 Kasım 2025, 10:00 - 11:00 (3/3 katılımcı uygun, %100)"
    }
  ]
}
```

### Örnek 2: Toplantı Oluşturma

```powershell
$body = @{
    subject = "Test Toplantısı"
    startTime = "2025-11-19T10:00:00"
    endTime = "2025-11-19T11:00:00"
    attendees = @("user1@example.com")
    body = "Bu bir test toplantısıdır"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/create-meeting" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

**Mock Yanıt:**
```json
{
  "success": true,
  "meeting": {
    "id": "MOCK_EVENT_123456",
    "webLink": "https://outlook.office365.com/calendar/item/mock/MOCK_EVENT_123456",
    "onlineMeeting": {
      "joinUrl": "https://teams.microsoft.com/l/meetup-join/mock/MOCK_MEETING_789012"
    }
  }
}
```

## 🎯 Copilot Studio ile Kullanım

Mock mode Copilot Studio entegrasyonunu test etmek için idealdir:

1. **API'yi mock mode'da başlatın**
2. **Custom Connector'ı API URL'iniz ile yapılandırın**
3. **Copilot Studio'da topic'leri test edin**
4. **Tüm akışı doğrulayın**

Mock mode'da:
- ✅ Connector bağlantıları çalışır
- ✅ API yanıtları dönülür
- ✅ Conversation flow'lar test edilir
- ✅ Adaptive Card'lar görüntülenir
- ❌ Gerçek takvimler sorgulanmaz
- ❌ Gerçek toplantılar oluşturulmaz

## 📝 Health Check ile Mode Kontrolü

API'nin hangi modda çalıştığını kontrol edin:

```powershell
Invoke-RestMethod -Uri "http://localhost:5000/health"
```

**Mock Mode Yanıtı:**
```json
{
  "status": "healthy",
  "service": "Meeting Planner Assistant",
  "mode": "MOCK",
  "timestamp": "2025-11-15T10:30:00"
}
```

**Production Mode Yanıtı:**
```json
{
  "status": "healthy",
  "service": "Meeting Planner Assistant",
  "mode": "PRODUCTION",
  "timestamp": "2025-11-15T10:30:00"
}
```

## 🔧 Mock Data Özelleştirme

`mock_graph_client.py` dosyasını düzenleyerek mock verileri özelleştirebilirsiniz:

### Uygunluk Oranlarını Değiştirme

```python
def _generate_mock_availability(self, length: int) -> str:
    # Daha fazla boş zaman için:
    if rand < 0.80:  # %80 free (varsayılan %60)
        availability.append('0')
```

### Daha Fazla Öneri Üretme

```python
def find_meeting_times(...):
    for i in range(10):  # Varsayılan 5 yerine 10 öneri
        ...
```

## ⚡ Performance

Mock mode son derece hızlıdır:
- **No network calls** - API istekleri yok
- **No authentication** - Token alımı yok
- **Instant responses** - Anında yanıtlar

Gerçek Graph API'ye göre **~10x daha hızlı**!

## 🐛 Debugging

### Log Mesajları

Mock mode çalışırken detaylı loglar görürsünüz:

```
⚠️  MOCK MODE: Using simulated data (no real Graph API calls)
📅 MOCK: Getting schedule for 3 participants from 2025-11-18T09:00:00 to 2025-11-18T17:00:00
✅ MOCK: Creating meeting 'Test Meeting' with 2 attendees
🔍 MOCK: Finding meeting times for 3 attendees
```

### Verbose Mode

Daha fazla detay için:

```python
# mock_graph_client.py içinde
print(f"DEBUG: Generated availability: {availability}")
print(f"DEBUG: Mock meeting data: {mock_meeting}")
```

## 📦 Production'a Geçiş Checklist

Graph API erişiminiz hazır olduğunda:

- [ ] Azure AD'de App Registration oluştur
- [ ] API permissions ver (Calendars.Read, Calendars.ReadWrite)
- [ ] Client ID, Secret, Tenant ID al
- [ ] `.env` dosyasında `USE_MOCK_API=False` yap
- [ ] Gerçek credentials'ları gir
- [ ] API'yi yeniden başlat
- [ ] Health check ile PRODUCTION modunu doğrula
- [ ] Gerçek test kullanıcılarıyla test et

## 💡 Best Practices

1. **Geliştirme**: Mock mode kullanın
2. **Test**: Karma (hem mock hem real) test yapın
3. **Production**: Real mode kullanın
4. **Demo**: Mock mode ile hızlı demo yapın
5. **CI/CD**: Mock mode ile otomatik testler çalıştırın

## 🎓 Öğrenme

Mock mode şunları öğrenmek için mükemmel:
- API endpoint'lerini anlamak
- Request/response formatlarını görmek
- Copilot Studio entegrasyonunu test etmek
- Conversation flow'ları geliştirmek
- Hata senaryolarını simüle etmek

Graph API'ye erişiminiz olmasa bile **tam fonksiyonel bir sistem** kurabilirsiniz! 🎉
