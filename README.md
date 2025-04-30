# **🌤 Weather Monitoring App — Backend**

## 🧭 Overview

This is the **backend** of the Weather Monitoring App. It provides such API:

- 🌤 Get Weather at real time

## 🚀 Getting Started

### 📦 Requirements

- Python **3.12**
- Poetry **≥ 2.0.0**

**Or** use Docker if you prefer running in a containerized environment.

### ▶️ Run Locally (without Docker)

1. Install dependencies:

    ```bash
    poetry install
    ```

2. Start the app:

    ```bash
    poetry run fastapi dev main.py
    ```

### 🐳 Run with Docker

```bash
docker run -d --name weather-backend -p 8080:8080 ebob/weather-backend:latest
```

Then open `http://localhost:8080/docs` in your browser.
