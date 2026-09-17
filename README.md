# 🗄️ SQL Agent - AI Powered Natural Language SQL Assistant

<p align="center">
Transform Natural Language into SQL Queries using AI.
</p>

<p align="center">

<a href="https://sql-agent-webapp-aaw6ztvpelygdtxk2gt5qp.streamlit.app/">
<img src="https://img.shields.io/badge/🚀_Live_Demo-Streamlit-success?style=for-the-badge">
</a>

<a href="https://github.com/Shukla2005">
<img src="https://img.shields.io/badge/GitHub-Repository-black?style=for-the-badge&logo=github">
</a>

<a href="https://www.linkedin.com/in/shuklaarjun28/">
<img src="https://img.shields.io/badge/LinkedIn-Arjun%20Shukla-blue?style=for-the-badge&logo=linkedin">
</a>

</p>

---

# 🚀 Live Demo

👉 https://sql-agent-webapp-aaw6ztvpelygdtxk2gt5qp.streamlit.app/

---

# 📌 Overview

SQL Agent is an AI-powered web application that allows users to interact with SQLite databases using natural language instead of writing SQL manually.

Simply upload a SQLite database, ask questions in plain English, and the AI automatically:

- Understands your question
- Generates optimized SQL queries
- Executes them
- Returns human-friendly answers along with the generated SQL

Built using **LangGraph**, **LangChain**, **Streamlit**, and **SQLite**, this project demonstrates how Large Language Models can simplify database analytics for everyone.

---

# ✨ Features

- 📤 Upload SQLite Databases
- 💬 Ask Questions in Natural Language
- 🤖 AI Generated SQL Queries
- 📊 Database Explorer
- 👀 View Generated SQL
- ⚡ Fast Streamlit Interface
- 🔒 Secure Local Database Processing
- 🌐 Deployable on Streamlit Cloud

---

# 🛠️ Tech Stack

### Frontend
- Streamlit

### Backend
- Python

### AI Framework
- LangChain
- LangGraph

### Database
- SQLite
- SQLAlchemy

### LLM
- OpenAI / Anthropic

---

# 🏗️ Architecture

## Technology Stack

| Layer | Technology |
|--------|------------|
| Frontend | Streamlit (Python Web Framework) |
| Agent Framework | LangGraph |
| LLM Integration | LangChain |
| Database | SQLite (SQLAlchemy) |
| State Management | LangGraph MemorySaver |

---

## How It Works

```text
┌─────────────────┐
│  User Question  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LangGraph      │
│  Agent          │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────┐
│ List   │ │ Get      │
│ Tables │ │ Schema   │
└────┬───┘ └────┬─────┘
     │          │
     └────┬─────┘
          ▼
    ┌───────────┐
    │ Generate  │
    │ SQL Query │
    └─────┬─────┘
          │
          ▼
    ┌───────────┐
    │ Execute   │
    │ Query     │
    └─────┬─────┘
          │
          ▼
    ┌───────────┐
    │ Format    │
    │ Response  │
    └─────┬─────┘
          │
          ▼
    ┌───────────┐
    │ Display   │
    │ to User   │
    └───────────┘
```

---

## Agent Workflow

### 1️⃣ List Tables
Retrieve all available tables from the uploaded SQLite database.

### 2️⃣ Get Schema
Fetch the schema and column information of the required tables.

### 3️⃣ Generate SQL Query
The LLM analyzes the user's question and generates an optimized SQL query.

### 4️⃣ Execute Query
The generated SQL query is executed against the SQLite database.

### 5️⃣ Format Response
The query results are converted into an easy-to-understand natural language response before being displayed to the user.

---

## Project Structure

```text
sql-agent-webapp/
│
├── app.py                  # Main Streamlit Application
├── requirements.txt        # Python Dependencies
├── .env.example            # Environment Variables
├── .gitignore              # Git Ignore Rules
├── README.md               # Project Documentation
│
└── .streamlit/
      └── config.toml       # Streamlit Configuration
```

---

# 📸 Screenshots

> Add screenshots of your application here.

```
screenshots/
├── Home.png
├── Upload.png
├── Query.png
└── Results.png
```

---

# 🚀 Installation

```bash
git clone https://github.com/Shukla2005/Sql-agent-webapp.git

cd Sql-agent-webapp

pip install -r requirements.txt

streamlit run app.py
```

---

# 📈 Future Improvements

- Support MySQL
- Support PostgreSQL
- Export Query Results to CSV
- Query History
- Voice Input
- Authentication
- Multi-Database Support
- Charts & Visualizations

---

# 👨‍💻 Developer

## Arjun Shukla

📧 **Email**

shuklaarjun101@gmail.com

🔗 **LinkedIn**

https://www.linkedin.com/in/shuklaarjun28/

💻 **GitHub**

https://github.com/Shukla2005

---

## ⭐ If you found this project useful, don't forget to give it a Star on GitHub!
