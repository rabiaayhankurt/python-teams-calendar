# Copilot Studio Entegrasyon Rehberi

Bu doküman, Meeting Planner Assistant'ı Microsoft Copilot Studio ile entegre etmek için detaylı adımları içerir.

## 📋 Önkoşullar

1. ✅ Meeting Planner API'sinin çalışır durumda olması
2. ✅ API'nin internetten erişilebilir bir URL'de host edilmesi (Azure App Service, ngrok, vs.)
3. ✅ Microsoft Copilot Studio erişimi
4. ✅ Teams admin yetkisi (bot'u yayınlamak için)

## 🔧 Adım 1: API URL'ini Hazırlama

### Geliştirme Ortamı (ngrok ile)

```powershell
# ngrok'u indirin ve kurun: https://ngrok.com/download

# API'nizi başlatın
python app.py

# Yeni bir terminal açın ve ngrok'u başlatın
ngrok http 5000
```

ngrok size şuna benzer bir URL verecek:
```
https://abc123.ngrok-free.app
```

Bu URL'i not alın!

### Production Ortamı

Azure App Service veya başka bir hosting servisi kullanarak API'nizi deploy edin ve URL'i not alın.

## 🤖 Adım 2: Copilot Studio'da Bot Oluşturma

1. [Copilot Studio](https://copilotstudio.microsoft.com/) → **Create** → **New copilot**
2. İsim: `Meeting Planner Assistant`
3. Dil: `Turkish`
4. **Create** butonuna tıklayın

## 📝 Adım 3: Custom Actions Ekleme

### Action 1: Toplantı Zamanlarını Bulma

1. Sol menüden **Actions** → **+ Add an action**
2. **Choose an action** → **Create from blank**

**Yapılandırma:**

```yaml
Name: FindMeetingTimes
Description: Katılımcıların uygun olduğu toplantı zamanlarını bulur

Endpoint:
  Method: POST
  URL: https://YOUR_API_URL/api/find-meeting-times

Headers:
  Content-Type: application/json

Input Parameters:
  - startDate (string, required): Başlangıç tarihi (YYYY-MM-DD)
  - endDate (string, required): Bitiş tarihi (YYYY-MM-DD)
  - timeRange (string, required): Saat aralığı (HH:MM-HH:MM)
  - participants (array, required): Katılımcı e-posta listesi
  - duration (number, optional): Toplantı süresi dakika (default: 60)

Request Body:
{
  "startDate": "{{startDate}}",
  "endDate": "{{endDate}}",
  "timeRange": "{{timeRange}}",
  "participants": {{participants}},
  "duration": {{duration}}
}

Output Variables:
  - success (boolean)
  - suggestions (array)
  - total_slots_analyzed (number)
```

3. **Save** → **Test action** ile test edin

### Action 2: Toplantı Oluşturma

1. **Actions** → **+ Add an action** → **Create from blank**

**Yapılandırma:**

```yaml
Name: CreateMeeting
Description: Teams toplantısı oluşturur

Endpoint:
  Method: POST
  URL: https://YOUR_API_URL/api/create-meeting

Headers:
  Content-Type: application/json

Input Parameters:
  - subject (string, required): Toplantı konusu
  - startTime (string, required): Başlangıç zamanı (ISO 8601)
  - endTime (string, required): Bitiş zamanı (ISO 8601)
  - attendees (array, required): Katılımcı e-posta listesi
  - body (string, optional): Toplantı açıklaması

Request Body:
{
  "subject": "{{subject}}",
  "startTime": "{{startTime}}",
  "endTime": "{{endTime}}",
  "attendees": {{attendees}},
  "body": "{{body}}"
}

Output Variables:
  - success (boolean)
  - meeting (object)
    - id (string)
    - webLink (string)
    - onlineMeeting.joinUrl (string)
```

2. **Save** → **Test action** ile test edin

## 💬 Adım 4: Conversation Topics Oluşturma

### Topic 1: Toplantı Planlama Başlatma

1. **Topics** → **+ Add a topic** → **From blank**
2. İsim: `Plan Meeting`

**Trigger phrases:**
- toplantı planla
- toplantı ayarla
- toplantı zamanı bul
- meeting planla
- uygun zaman bul

**Conversation Flow:**

```
[Bot Message]
Merhaba! Size toplantı planlamada yardımcı olabilirim. 

Lütfen aşağıdaki bilgileri paylaşın:
1. Tarih aralığı (örn. 18-22 Kasım)
2. Saat aralığı (örn. 09:00-17:00)
3. Katılımcıların e-posta adresleri
4. Toplantı süresi (dakika cinsinden)

[Question: StartDate]
Başlangıç tarihini girin (YYYY-MM-DD formatında):
Save response as: Var_StartDate

[Question: EndDate]
Bitiş tarihini girin (YYYY-MM-DD formatında):
Save response as: Var_EndDate

[Question: TimeRange]
Saat aralığını girin (HH:MM-HH:MM formatında):
Save response as: Var_TimeRange

[Question: Participants]
Katılımcıların e-posta adreslerini virgülle ayırarak girin:
Save response as: Var_ParticipantsText

[Power Fx - Parse Participants]
Set(Var_Participants, Split(Var_ParticipantsText, ","))

[Question: Duration]
Toplantı süresi kaç dakika olsun?
Save response as: Var_Duration

[Action Call: FindMeetingTimes]
Input:
  - startDate: Var_StartDate
  - endDate: Var_EndDate
  - timeRange: Var_TimeRange
  - participants: Var_Participants
  - duration: Var_Duration

Output: Var_Suggestions

[Condition: Check Success]
If Var_Suggestions.success = true

  [Bot Message: Show Suggestions]
  Harika! Uygun zamanları buldum:
  
  {ForEach item in Var_Suggestions.suggestions}
    {item.formatted}
  {EndForEach}
  
  Hangi zamanı seçmek istersiniz? (1, 2, 3, vb.)
  
  [Question: Selection]
  Save response as: Var_SelectedIndex
  
  [Power Fx - Get Selected Slot]
  Set(Var_SelectedSlot, Index(Var_Suggestions.suggestions, Var_SelectedIndex))
  
  [Redirect to: Create Meeting Topic]
  
Else

  [Bot Message: Error]
  Üzgünüm, uygun zaman bulamadım. Lütfen farklı bir tarih aralığı deneyin.
  
End If
```

### Topic 2: Toplantı Oluşturma

1. **Topics** → **+ Add a topic** → **From blank**
2. İsim: `Create Meeting`

**Conversation Flow:**

```
[Question: Subject]
Toplantı konusu ne olsun?
Save response as: Var_Subject

[Question: Body]
Toplantı hakkında eklemek istediğiniz bir açıklama var mı? (İsteğe bağlı)
Save response as: Var_Body

[Confirmation]
Toplantıyı oluşturmak istediğinizden emin misiniz?
- Konu: {Var_Subject}
- Zaman: {Var_SelectedSlot.formatted}
- Katılımcılar: {Join(Var_Participants, ", ")}

[If confirmed]

  [Action Call: CreateMeeting]
  Input:
    - subject: Var_Subject
    - startTime: Var_SelectedSlot.start_time
    - endTime: Var_SelectedSlot.end_time
    - attendees: Var_Participants
    - body: Var_Body
  
  Output: Var_MeetingResult
  
  [Condition: Check Success]
  If Var_MeetingResult.success = true
  
    [Bot Message: Success]
    ✅ Toplantınız başarıyla oluşturuldu!
    
    📅 Konu: {Var_Subject}
    🕐 Zaman: {Var_SelectedSlot.formatted}
    👥 Katılımcılar: {Var_SelectedSlot.available_count} kişi
    
    🔗 Teams Linki: {Var_MeetingResult.meeting.onlineMeeting.joinUrl}
    
    Davetler katılımcılara e-posta ile gönderildi.
    
  Else
  
    [Bot Message: Error]
    ❌ Toplantı oluşturulurken bir hata oluştu. Lütfen tekrar deneyin.
    
  End If

End If
```

## 🎨 Adım 5: Adaptive Card Kullanımı (Opsiyonel)

Toplantı önerilerini daha güzel göstermek için Adaptive Card kullanabilirsiniz:

```json
{
  "type": "AdaptiveCard",
  "version": "1.4",
  "body": [
    {
      "type": "TextBlock",
      "text": "Uygun Toplantı Zamanları",
      "weight": "Bolder",
      "size": "Large"
    },
    {
      "type": "ColumnSet",
      "columns": [
        {
          "type": "Column",
          "items": [
            {
              "type": "TextBlock",
              "text": "${formatted}",
              "wrap": true
            }
          ]
        }
      ]
    }
  ],
  "actions": [
    {
      "type": "Action.Submit",
      "title": "Bu Zamanı Seç",
      "data": {
        "action": "select",
        "slot": "${$data}"
      }
    }
  ]
}
```

## 🧪 Adım 6: Test Etme

1. Copilot Studio'da sağ üstteki **Test your copilot** butonuna tıklayın
2. Test konuşmaları yapın:

```
Sen: Toplantı planla
Bot: [Bilgi sorar]
Sen: 2025-11-18
Bot: [Bitiş tarihi sorar]
Sen: 2025-11-22
Bot: [Saat aralığı sorar]
Sen: 09:00-17:00
Bot: [Katılımcılar sorar]
Sen: user1@company.com, user2@company.com
Bot: [Süre sorar]
Sen: 60
Bot: [Öneriler gösterir]
Sen: 1
Bot: [Konu sorar]
Sen: Proje Değerlendirme
Bot: [Toplantıyı oluşturur]
```

## 🚀 Adım 7: Teams'e Yayınlama

1. Sol menüden **Channels** → **Microsoft Teams**
2. **Turn on Teams** butonuna tıklayın
3. Bot ayarlarını yapılandırın:
   - Bot name
   - Bot icon
   - Short description
   - Long description
4. **Submit for approval** (kuruluş yöneticisi onaylamalı)
5. Onay sonrası bot Teams'de kullanılabilir olacak

## 📱 Teams'de Kullanım

Bot yayınlandıktan sonra:

1. Teams'de **Apps** → Şirket uygulamalarınızı arayın
2. `Meeting Planner Assistant` bulun ve **Add** yapın
3. Botu kullanmaya başlayın:

```
Sen: Merhaba
Bot: Merhaba! Size toplantı planlamada yardımcı olabilirim...

Sen: Toplantı planla
Bot: [Akış başlar]
```

## 🔒 Güvenlik Önerileri

1. **API Key Kullanımı**: API'nize authentication ekleyin
2. **Rate Limiting**: API'nize rate limit ekleyin
3. **HTTPS**: Sadece HTTPS kullanın
4. **Environment Variables**: Hassas bilgileri environment variables'da tutun
5. **Access Control**: Bot'u sadece belirli kullanıcılara açın

## 🐛 Troubleshooting

### Action çalışmıyor
- API URL'inin doğru ve erişilebilir olduğunu kontrol edin
- ngrok kullanıyorsanız, her başlatmada URL değişir
- Request/Response formatlarının doğru olduğunu kontrol edin

### Bot yanıt vermiyor
- Topic trigger phrases'leri kontrol edin
- Conversation flow'da hata olup olmadığını test panelinde kontrol edin
- Variables'ın doğru şekilde set edildiğinden emin olun

### Teams'de görünmüyor
- Bot'un publish edildiğinden emin olun
- Admin onayının verildiğini kontrol edin
- Teams cache'ini temizleyin

## 📚 Ek Kaynaklar

- [Copilot Studio Documentation](https://learn.microsoft.com/en-us/microsoft-copilot-studio/)
- [Power Fx Reference](https://learn.microsoft.com/en-us/power-platform/power-fx/formula-reference)
- [Adaptive Cards Designer](https://adaptivecards.io/designer/)

## 💡 İpuçları

1. **Natural Language Processing**: Bot'unuzu daha akıllı yapmak için topic'leri çeşitlendirin
2. **Error Handling**: Her action çağrısı sonrası success kontrolü yapın
3. **User Experience**: Loading mesajları ekleyin ("Takvimler kontrol ediliyor...")
4. **Feedback**: Kullanıcıdan feedback alın ve bot'u geliştirin
5. **Analytics**: Copilot Studio'nun analytics özelliğini kullanarak kullanım istatistiklerini takip edin
