# 🧞 Genie AI | Luxury Databricks Intelligence

An enterprise-grade Microsoft Teams integration that transforms Databricks Genie into a rich, visual intelligence dashboard. This application bridges the gap between raw data and decision-making through a premium, AI-driven chat experience.

---

## ✨ Features

### 💎 Luxury BI Experience
- **Premium UI**: High-end glassmorphism design with Tailwind CSS and Inter typography.
- **Dynamic Visuals**: Automatic conversion of Databricks SQL results into Interactive Bar, Doughnut, and Line charts via **Chart.js**.
- **UX Excellence**: Synthetic streamdown effects, syntax-highlighted SQL blocks, and one-click copy functionality.

### 🛡️ Enterprise-Grade Security
- **Auth0 Integration**: Secure OAuth2 authentication flow requiring enterprise identity verification.
- **Session Management**: Signed, HTTP-only cookies for secure session persistence.
- **Environment Aware**: Strict configuration schema using Pydantic for robust deployment.

### 🤝 Teams Integration
- **Personal Tab**: A full-screen analytics dashboard directly inside Microsoft Teams.
- **Conversational Bot**: Interactive messaging handling activities and adaptive responses.

---

## 📂 Project Structure

```text
genie-teams-app/
├── backend/                # FastAPI server (Python)
│   ├── main.py             # API entry point & Auth routes
│   ├── genie_client.py     # Databricks Genie API wrapper
│   ├── auth0_client.py     # OAuth2 & Identity logic
│   ├── bot.py              # MS Teams Bot implementation
│   └── config.py           # Environment configuration
├── frontend/               # Dashboard UI (HTML/JS/CSS)
│   ├── index.html          # Main application shell
│   ├── login.html          # Secure entry point
│   └── app.js              # State management & visualization
├── teams-manifest/         # MS Teams deployment package
└── docker-compose.yml      # Container orchestration
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Databricks Workspace**: Access to a Genie Space and a SQL Warehouse.
- **Auth0 Account**: A configured Regular Web Application with `http://localhost:8000/auth/callback` as a valid callback URL.
- **ngrok**: (Optional) For exposing the local server to Microsoft Teams.

### 2. Configure Environment
Create a `.env` file in the `backend/` directory with the following:

```env
# Databricks Configuration
DATABRICKS_HOST=https://your-workspace.databricks.com
DATABRICKS_TOKEN=dapi...
GENIE_SPACE_ID=...

# Auth0 Configuration
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_CLIENT_ID=...
AUTH0_CLIENT_SECRET=...
AUTH0_CALLBACK_URL=http://localhost:8000/auth/callback

# Security
APP_SECRET_KEY=generate-a-long-random-string
```

### 3. Execution

#### Local Development
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
Visit `http://localhost:8000` to access the dashboard.

#### Docker (Production-ready)
```bash
docker-compose up --build
```

---

## 🛠️ Tech Stack

- **Server**: FastAPI, Python 3.14, Pydantic, Requests.
- **UI**: Vanilla JS (ES6+), Tailwind CSS v3, Chart.js, Lucide Icons.
- **Identity**: Auth0 (OpenID Connect / OAuth2).
- **Intelligence**: Databricks Genie & SQL Execution APIs.
- **Integration**: Microsoft Bot Framework SDK.

---

© 2026 Databricks Genie AI Team. Precision data intelligence for modern enterprises.
