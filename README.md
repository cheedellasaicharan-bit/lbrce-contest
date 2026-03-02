# LBRCE Coding Contest Platform

A premium, high-performance coding contest platform engineered for the CSE(AI&ML) department at LBRCE.

## 🚀 Key Features

- **Contest Aesthetic**: A premium design language with glassmorphism and full Dark Mode sync.
- **Assessment Arena**: 3-panel IDE workspace for high-stakes coding challenges.
- **Administrator Portal**: Complete control over problems, test cases, and student results.
- **Global Leaderboard**: Real-time ranking with dynamic podium visualizations.
- **Theme Agility**: Fully tokenized CSS variable system for effortless brand adaptation.

## 🛠️ Deployment

This project is pre-configured for **Render** and **Vercel**.

### Environment Setup

Set the following environment variables in your deployment dashboard:

- `SECRET_KEY`: A robust secret string for session security.
- `ADMIN_USER`: Username for the administrator dashboard.
- `ADMIN_PASS`: Password for the administrator dashboard.
- `JUDGE0_API_KEY`: Your Judge0 CE API key for code execution.
- `DATABASE_URL`: (Optional) PostgreSQL connection string for production scale.

### Local Initialization

```bash
pip install -r requirements.txt
python app.py
```

## 🏗️ Architecture

- **Backend**: Flask / Python
- **Database**: SQLite (Local) / PostgreSQL (Production)
- **Frontend**: HTML5, Vanilla CSS (Themed Tokens), ES6 JavaScript
- **Execution Engine**: Judge0 API

---
*Built for the Department of CSE(AI&ML) — LBRCE.*
