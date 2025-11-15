# GitHub Deployment Rehberi

Bu rehber, Meeting Planner Assistant projesini GitHub'a yükleme ve Azure'a deploy etme adımlarını içerir.

## 📦 GitHub'a Yükleme

### 1. Git Repository Oluşturma

```bash
# Git'i başlat
git init

# .gitignore dosyası zaten mevcut
# Dosyaları stage'e ekle
git add .

# İlk commit
git commit -m "Initial commit: Meeting Planner Assistant"
```

### 2. GitHub'da Repository Oluştur

1. [GitHub](https://github.com) → **New Repository**
2. Repository adı: `meeting-planner-assistant`
3. **Public** veya **Private** seçin
4. **README eklemeden** oluşturun

### 3. Remote Ekle ve Push Et

```bash
# Remote ekle (YOUR_USERNAME yerine kendi kullanıcı adınızı yazın)
git remote add origin https://github.com/YOUR_USERNAME/meeting-planner-assistant.git

# Main branch'e push
git branch -M main
git push -u origin main
```

## 🚀 Azure App Service'e Deploy

### Yöntem 1: GitHub Actions (Önerilen)

#### Adım 1: Azure App Service Oluştur

```bash
# Azure CLI ile
az login

# Resource group oluştur
az group create --name meeting-planner-rg --location westeurope

# App Service plan oluştur
az appservice plan create --name meeting-planner-plan --resource-group meeting-planner-rg --sku B1 --is-linux

# Web app oluştur
az webapp create --resource-group meeting-planner-rg --plan meeting-planner-plan --name meeting-planner-api --runtime "PYTHON:3.11"
```

#### Adım 2: Publish Profile Al

```bash
# Publish profile'ı indir
az webapp deployment list-publishing-profiles --name meeting-planner-api --resource-group meeting-planner-rg --xml
```

Çıktıyı kopyalayın.

#### Adım 3: GitHub Secrets Ekle

1. GitHub repository → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** tıklayın
3. Secret ekleyin:
   - Name: `AZURE_WEBAPP_PUBLISH_PROFILE`
   - Value: Kopyaladığınız XML içeriği

#### Adım 4: Environment Variables Ekle (Opsiyonel)

Production mode için:

```bash
az webapp config appsettings set --resource-group meeting-planner-rg --name meeting-planner-api --settings \
  USE_MOCK_API=False \
  CLIENT_ID="your_client_id" \
  CLIENT_SECRET="your_secret" \
  TENANT_ID="your_tenant_id"
```

Mock mode için:

```bash
az webapp config appsettings set --resource-group meeting-planner-rg --name meeting-planner-api --settings \
  USE_MOCK_API=True
```

#### Adım 5: Deploy

Push yapın veya manuel trigger:

```bash
git add .
git commit -m "Update configuration"
git push origin main
```

GitHub Actions otomatik çalışacak ve deploy edecek.

### Yöntem 2: Azure "Deploy to Azure" Button

1. GitHub repository'de `README_GITHUB.md` dosyasındaki butona tıklayın
2. Azure Portal'da form doldur:
   - Subscription seçin
   - Resource group oluştur/seç
   - Region seçin
   - Mock mode: `true` (test için)
3. **Create** tıklayın

### Yöntem 3: Docker Container ile Deploy

```bash
# Docker image build et
docker build -t meeting-planner-api .

# Azure Container Registry'e push
az acr create --resource-group meeting-planner-rg --name meetingplanneracr --sku Basic
az acr login --name meetingplanneracr
docker tag meeting-planner-api meetingplanneracr.azurecr.io/meeting-planner-api:latest
docker push meetingplanneracr.azurecr.io/meeting-planner-api:latest

# Web app'i container ile oluştur
az webapp create --resource-group meeting-planner-rg --plan meeting-planner-plan --name meeting-planner-api --deployment-container-image-name meetingplanneracr.azurecr.io/meeting-planner-api:latest
```

## 🔒 Güvenlik Ayarları

### 1. API Key Ekle (Opsiyonel)

```bash
az webapp config appsettings set --resource-group meeting-planner-rg --name meeting-planner-api --settings \
  API_KEY="your_secure_api_key"
```

### 2. HTTPS Zorla

```bash
az webapp update --resource-group meeting-planner-rg --name meeting-planner-api --https-only true
```

### 3. CORS Ayarları

```bash
az webapp cors add --resource-group meeting-planner-rg --name meeting-planner-api --allowed-origins \
  "https://make.powerapps.com" \
  "https://make.powerautomate.com" \
  "https://*.copilotstudio.microsoft.com"
```

## 🔍 Monitoring ve Logs

### Application Insights Ekle

```bash
# Application Insights oluştur
az monitor app-insights component create --app meeting-planner-insights --location westeurope --resource-group meeting-planner-rg

# Instrumentation key al
INSTRUMENTATION_KEY=$(az monitor app-insights component show --app meeting-planner-insights --resource-group meeting-planner-rg --query instrumentationKey -o tsv)

# Web app'e ekle
az webapp config appsettings set --resource-group meeting-planner-rg --name meeting-planner-api --settings \
  APPINSIGHTS_INSTRUMENTATIONKEY=$INSTRUMENTATION_KEY
```

### Log Stream

```bash
# Real-time logs
az webapp log tail --resource-group meeting-planner-rg --name meeting-planner-api
```

## 🧪 Deployment Test

```bash
# Health check
curl https://meeting-planner-api.azurewebsites.net/health

# API test
curl -X POST https://meeting-planner-api.azurewebsites.net/api/find-meeting-times \
  -H "Content-Type: application/json" \
  -d '{
    "startDate": "2025-11-18",
    "endDate": "2025-11-22",
    "timeRange": "09:00-17:00",
    "participants": ["user1@example.com"],
    "duration": 60
  }'
```

## 🔄 Continuous Deployment

`.github/workflows/deploy.yml` dosyası ile otomatik deployment aktif:

- ✅ Her `main` branch'e push
- ✅ Manuel workflow dispatch
- ✅ Otomatik test çalıştırma
- ✅ Azure'a deploy

## 📊 Kullanım İstatistikleri

Azure Portal'da:
1. App Service'i aç
2. **Monitoring** → **Metrics**
3. CPU, Memory, Request Count grafikleri

## 🔧 Troubleshooting

### Deployment Başarısız

```bash
# Deployment logs kontrol et
az webapp log deployment show --resource-group meeting-planner-rg --name meeting-planner-api
```

### Application Hatası

```bash
# Application logs
az webapp log download --resource-group meeting-planner-rg --name meeting-planner-api
```

### Restart

```bash
az webapp restart --resource-group meeting-planner-rg --name meeting-planner-api
```

## 💰 Maliyet Optimizasyonu

### Free Tier (F1)
- 1 GB disk
- 60 dakika/gün CPU
- Test ve development için

### Basic Tier (B1)
- $13/ay
- 1.75 GB RAM
- Always-on destekler
- Production için önerilen

### Scale

```bash
# Scale up
az appservice plan update --name meeting-planner-plan --resource-group meeting-planner-rg --sku B2

# Scale down
az appservice plan update --name meeting-planner-plan --resource-group meeting-planner-rg --sku F1
```

## 📞 Destek

- 📧 GitHub Issues: Sorun bildirmek için
- 📖 Wiki: Detaylı dokümantasyon
- 💬 Discussions: Soru-cevap

## 🎉 Sonuç

Deployment tamamlandı! API'niz artık:

✅ GitHub'da versiyon kontrol altında
✅ Azure'da production'da çalışıyor
✅ CI/CD ile otomatik deploy ediliyor
✅ Power Platform'dan erişilebilir
✅ Copilot Studio'da kullanıma hazır

**API URL:** `https://meeting-planner-api.azurewebsites.net`
