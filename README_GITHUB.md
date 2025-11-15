# Meeting Planner Assistant

Toplantı planlama ve katılımcı uygunluk kontrolü için Microsoft Graph API tabanlı REST API servisi.

[![Deploy to Azure](https://img.shields.io/badge/Deploy%20to-Azure-0078D4?style=flat&logo=microsoft-azure)](https://portal.azure.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🌟 Özellikler

- 🎭 **Mock Mode** - Graph API olmadan test
- 📅 **Akıllı Takvim Analizi** - En uygun zamanları bulma
- 🔗 **Teams Entegrasyonu** - Otomatik toplantı oluşturma
- 🤖 **Copilot Studio Ready** - Custom Connector desteği
- 🐳 **Docker Support** - Containerized deployment
- 🔒 **CORS Enabled** - Power Platform uyumlu

## 🚀 Hızlı Başlangıç

### Local Deployment

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/meeting-planner-assistant.git
cd meeting-planner-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env file

# Run server
python app.py
```

### Docker Deployment

```bash
docker build -t meeting-planner-api .
docker run -p 5000:5000 --env-file .env meeting-planner-api
```

### Azure Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FYOUR_USERNAME%2Fmeeting-planner-assistant%2Fmain%2Fazuredeploy.json)

## 📖 Documentation

- [Installation Guide](README.md)
- [Mock Mode Guide](MOCK_MODE_GUIDE.md)
- [Custom Connector Setup](CUSTOM_CONNECTOR_GUIDE.md)
- [Copilot Studio Integration](COPILOT_STUDIO_GUIDE.md)
- [API Reference](swagger.json)

## 🔧 Configuration

### Environment Variables

```env
# Mock Mode (no Graph API needed)
USE_MOCK_API=True

# Production Mode
USE_MOCK_API=False
CLIENT_ID=your_azure_ad_client_id
CLIENT_SECRET=your_client_secret
TENANT_ID=your_tenant_id
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/find-meeting-times` | POST | Find available meeting times |
| `/api/create-meeting` | POST | Create Teams meeting |
| `/api/check-availability` | POST | Check participant availability |

## 🧪 Testing

```bash
# Run test suite
python test_api.py

# Or use pytest
pytest -v
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Microsoft Graph API
- Microsoft Copilot Studio
- Flask Framework

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

Made with ❤️ for better meeting planning
