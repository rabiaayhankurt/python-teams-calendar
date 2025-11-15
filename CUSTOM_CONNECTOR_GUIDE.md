# Custom Connector ile Copilot Studio Entegrasyonu

Bu rehber, Meeting Planner Assistant API'sini Power Platform Custom Connector kullanarak Copilot Studio'ya entegre etmeyi gösterir.

## 📋 Ön Hazırlık

### 1. API'yi Deploy Edin

API'nizin internetten erişilebilir olması gerekiyor:

**Seçenek A: Azure App Service** (Önerilen)
```powershell
# Azure'da App Service oluştur
az webapp create --resource-group myResourceGroup `
    --plan myAppServicePlan `
    --name meeting-planner-api `
    --runtime "PYTHON:3.11"

# Environment variables ayarla
az webapp config appsettings set --resource-group myResourceGroup `
    --name meeting-planner-api `
    --settings CLIENT_ID="xxx" CLIENT_SECRET="xxx" TENANT_ID="xxx"

# Deploy et
az webapp up --resource-group myResourceGroup --name meeting-planner-api
```

**Seçenek B: ngrok** (Test için)
```powershell
# API'yi lokal başlat
python app.py

# Yeni terminal'de ngrok başlat
ngrok http 5000
```

URL'inizi not alın: `https://your-app.azurewebsites.net` veya `https://xxx.ngrok-free.app`

## 🔌 Adım 1: Custom Connector Oluşturma

### Power Platform'da Connector Oluştur

1. [Power Platform Admin Center](https://make.powerapps.com/) → **Dataverse** → **Custom Connectors**
2. **+ New custom connector** → **Import an OpenAPI file**
3. `swagger.json` dosyasını yükleyin
4. **Continue** tıklayın

### Connector Ayarlarını Yapın

**General:**
- Connector name: `Meeting Planner Assistant`
- Description: `Toplantı planlama ve katılımcı uygunluk kontrolü`
- Host: API URL'inizi girin (örn: `your-app.azurewebsites.net`)
- Base URL: `/`

**Security:**
- Authentication type: `No authentication` (API Key eklemek isterseniz aşağıya bakın)
- **Create connector** tıklayın

### (Opsiyonel) API Key Güvenliği Ekleyin

API'ye güvenlik eklemek için `app.py` dosyasına ekleyin:

```python
from functools import wraps
from flask import request

API_KEY = os.getenv('API_KEY', 'your-secret-key')

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != API_KEY:
            return jsonify({'success': False, 'error': 'Invalid API Key'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Her endpoint'e ekleyin
@app.route('/api/find-meeting-times', methods=['POST'])
@require_api_key
def find_meeting_times():
    ...
```

Custom Connector'da Security ayarını değiştirin:
- Authentication type: `API Key`
- Parameter label: `API Key`
- Parameter name: `X-API-Key`
- Parameter location: `Header`

## 🤖 Adım 2: Copilot Studio'da Kullanım

### Connection Oluştur

1. Copilot Studio'da copilot'unuzu açın
2. **Settings** → **Connectors** → **+ Add connector**
3. Custom connectors listesinden `Meeting Planner Assistant` seçin
4. Connection oluştur (API Key varsa girin)

### Topic'te Connector Kullanımı

**Örnek 1: Toplantı Zamanı Bulma**

```yaml
Topic: Find Meeting Times

Trigger phrases:
  - toplantı planla
  - uygun zaman bul
  - meeting zamanı

Conversation flow:

[Question Node]
Başlangıç tarihini girin (örn. 2025-11-18):
→ Save as: Topic.StartDate

[Question Node]
Bitiş tarihini girin (örn. 2025-11-22):
→ Save as: Topic.EndDate

[Question Node]
Saat aralığını girin (örn. 09:00-17:00):
→ Save as: Topic.TimeRange

[Question Node]
Katılımcıların e-postalarını virgülle ayırarak girin:
→ Save as: Topic.ParticipantsText

[Question Node]
Toplantı kaç dakika sürsün?
→ Save as: Topic.Duration

[Power Fx Node]
// E-postaları array'e çevir
Set(Topic.ParticipantsArray, Split(Topic.ParticipantsText, ","))

[Action Node - Custom Connector]
Connector: Meeting Planner Assistant
Action: FindMeetingTimes
Inputs:
  startDate: Topic.StartDate
  endDate: Topic.EndDate
  timeRange: Topic.TimeRange
  participants: Topic.ParticipantsArray
  duration: Topic.Duration
Output: Topic.MeetingSuggestions

[Condition Node]
If Topic.MeetingSuggestions.success = true:

  [Message Node - Adaptive Card]
  {
    "type": "AdaptiveCard",
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.4",
    "body": [
      {
        "type": "TextBlock",
        "text": "✨ Uygun Toplantı Zamanları",
        "weight": "Bolder",
        "size": "Large",
        "color": "Accent"
      },
      {
        "type": "TextBlock",
        "text": "${Topic.MeetingSuggestions.total_slots_analyzed} zaman dilimi analiz edildi",
        "isSubtle": true,
        "spacing": "None"
      },
      {
        "type": "Container",
        "separator": true,
        "spacing": "Medium",
        "items": [
          {
            "type": "TextBlock",
            "text": "📅 Öneriler:",
            "weight": "Bolder"
          }
        ]
      },
      {
        "$data": "${Topic.MeetingSuggestions.suggestions}",
        "type": "Container",
        "separator": true,
        "spacing": "Small",
        "items": [
          {
            "type": "ColumnSet",
            "columns": [
              {
                "type": "Column",
                "width": "stretch",
                "items": [
                  {
                    "type": "TextBlock",
                    "text": "${formatted}",
                    "wrap": true
                  }
                ]
              },
              {
                "type": "Column",
                "width": "auto",
                "items": [
                  {
                    "type": "TextBlock",
                    "text": "${available_count}/${total_participants}",
                    "color": "Good",
                    "weight": "Bolder"
                  }
                ]
              }
            ],
            "selectAction": {
              "type": "Action.Submit",
              "data": {
                "action": "select_time",
                "start_time": "${start_time}",
                "end_time": "${end_time}",
                "formatted": "${formatted}"
              }
            }
          }
        ]
      }
    ]
  }
  
  [Question Node]
  Hangi zamanı seçmek istersiniz? (1-5 arası numara)
  → Save as: Topic.SelectedIndex
  
  [Power Fx Node]
  Set(Topic.SelectedSlot, Index(Topic.MeetingSuggestions.suggestions, Topic.SelectedIndex - 1))
  
  [Redirect to Topic: CreateMeeting]
  
Else:
  
  [Message Node]
  ❌ Üzgünüm, uygun zaman bulamadım. Farklı bir tarih aralığı deneyin.
```

**Örnek 2: Toplantı Oluşturma**

```yaml
Topic: Create Meeting

Conversation flow:

[Question Node]
Toplantı konusu ne olsun?
→ Save as: Topic.Subject

[Question Node]
Toplantı hakkında açıklama (isteğe bağlı):
→ Save as: Topic.Body

[Message Node - Confirmation]
📋 **Toplantı Özeti**
- Konu: ${Topic.Subject}
- Zaman: ${Topic.SelectedSlot.formatted}
- Katılımcılar: ${Topic.ParticipantsText}

Onaylıyor musunuz?

[Question Node - Choice]
Choices: Evet, Hayır
→ Save as: Topic.Confirmation

[Condition Node]
If Topic.Confirmation = "Evet":

  [Message Node]
  ⏳ Toplantı oluşturuluyor, lütfen bekleyin...
  
  [Action Node - Custom Connector]
  Connector: Meeting Planner Assistant
  Action: CreateMeeting
  Inputs:
    subject: Topic.Subject
    startTime: Topic.SelectedSlot.start_time
    endTime: Topic.SelectedSlot.end_time
    attendees: Topic.ParticipantsArray
    body: Topic.Body
  Output: Topic.MeetingResult
  
  [Condition Node]
  If Topic.MeetingResult.success = true:
    
    [Message Node - Success]
    ✅ **Toplantı Başarıyla Oluşturuldu!**
    
    📅 **Konu:** ${Topic.Subject}
    🕐 **Zaman:** ${Topic.SelectedSlot.formatted}
    👥 **Katılımcılar:** ${Topic.SelectedSlot.available_count} kişi
    
    🔗 **Teams Linki:**
    ${Topic.MeetingResult.meeting.onlineMeeting.joinUrl}
    
    📧 Davetler katılımcılara gönderildi.
    
  Else:
    
    [Message Node - Error]
    ❌ Toplantı oluşturulurken hata oluştu:
    ${Topic.MeetingResult.error}
    
  End If

Else:
  
  [Message Node]
  Toplantı oluşturma iptal edildi.

End If
```

## 🎨 Adaptive Card Örnekleri

### Toplantı Önerileri Card'ı

Copilot Studio'da **Message** node → **Advanced** → **Adaptive Card** seçin:

```json
{
  "type": "AdaptiveCard",
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "version": "1.4",
  "body": [
    {
      "type": "TextBlock",
      "text": "📅 Toplantı Önerileri",
      "weight": "Bolder",
      "size": "Large"
    },
    {
      "type": "TextBlock",
      "text": "${Topic.MeetingSuggestions.total_slots_analyzed} zaman dilimi analiz edildi",
      "isSubtle": true
    },
    {
      "$data": "${Topic.MeetingSuggestions.suggestions}",
      "type": "Container",
      "separator": true,
      "items": [
        {
          "type": "ColumnSet",
          "columns": [
            {
              "type": "Column",
              "width": "auto",
              "items": [
                {
                  "type": "TextBlock",
                  "text": "✓",
                  "size": "Large",
                  "color": "Good"
                }
              ]
            },
            {
              "type": "Column",
              "width": "stretch",
              "items": [
                {
                  "type": "TextBlock",
                  "text": "${formatted}",
                  "wrap": true,
                  "weight": "Bolder"
                },
                {
                  "type": "TextBlock",
                  "text": "${available_count} katılımcı uygun (%${Int(availability_percentage)})",
                  "isSubtle": true,
                  "spacing": "None"
                }
              ]
            }
          ],
          "selectAction": {
            "type": "Action.Submit",
            "title": "Seç",
            "data": {
              "action": "select",
              "slot": "${$data}"
            }
          }
        }
      ]
    }
  ]
}
```

## 🔍 Test Etme

### Connector Test

1. Custom Connectors → Meeting Planner Assistant → **Test**
2. Connection seçin veya yeni oluşturun
3. Her operation'ı test edin:

**FindMeetingTimes test:**
```json
{
  "startDate": "2025-11-18",
  "endDate": "2025-11-22",
  "timeRange": "09:00-17:00",
  "participants": ["user1@company.com", "user2@company.com"],
  "duration": 60
}
```

### Copilot Test

1. Copilot Studio → Test your copilot
2. Konuşma başlatın:
```
Sen: Toplantı planla
Bot: [Sorular sorar]
Sen: [Bilgileri ver]
Bot: [Öneriler gösterir]
```

## 🚀 Production'a Alma

### 1. Solution Oluştur

```powershell
# Power Platform CLI
pac solution create --name "MeetingPlannerSolution" --publisher "YourCompany"
pac solution add-reference --path "MeetingPlannerSolution" --id "YourConnectorId"
```

### 2. Environment'lar Arası Taşıma

1. **Solutions** → Solution'ınızı seçin
2. **Export** → **Managed**
3. Hedef environment'ta **Import**

### 3. Connection'ları Ayarla

Her environment'ta connection oluşturun:
- Development: Test API URL'i
- Production: Production API URL'i

## 📊 Monitoring ve Debugging

### Custom Connector Run History

1. Custom Connectors → Meeting Planner Assistant → **Run history**
2. Request/Response log'larını inceleyin

### Copilot Analytics

1. Copilot → **Analytics**
2. Topic performance
3. Session details

## 🛠️ Troubleshooting

### Connector bağlanamıyor
```powershell
# API'nin çalıştığını kontrol et
Invoke-RestMethod -Uri "https://your-api/health"

# CORS sorunları için app.py'a ekleyin:
from flask_cors import CORS
CORS(app)
```

### Authentication hatası
- API Key doğru girilmiş mi kontrol edin
- Azure AD credentials'ları doğrulayın

### Timeout sorunları
```python
# app.py'da timeout artırın
from flask import Flask
app = Flask(__name__)
app.config['TIMEOUT'] = 120
```

## 💡 Best Practices

1. **Error Handling**: Her connector action'dan sonra success kontrolü yapın
2. **Loading Messages**: Uzun işlemlerde kullanıcıya bilgi verin
3. **Validation**: Input'ları validate edin (tarih formatı, email formatı)
4. **Caching**: Sık kullanılan verileri cache'leyin
5. **Rate Limiting**: API'nize rate limit ekleyin

## 📚 Ek Kaynaklar

- [Custom Connectors Docs](https://learn.microsoft.com/en-us/connectors/custom-connectors/)
- [Copilot Studio Actions](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-plugin-actions)
- [Adaptive Cards](https://adaptivecards.io/)
