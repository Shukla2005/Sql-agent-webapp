# 🗄️ SQL Agent - AI Powered Natural Language SQL Assistant

This Streamlit app lets you upload a SQLite database (`.db`, `.sqlite`, or `.sqlite3`) and ask questions in natural language. Groq generates read-only SQL queries and the app runs them against the uploaded database.

## Streamlit Cloud deployment

The API key must be configured in the deployed app; uploading a database does not provide an API key. In Streamlit Cloud:

1. Open the app dashboard.
2. Open **Settings → Secrets**.
3. Add the following TOML and replace the value with a real key from [Groq Console](https://console.groq.com/keys):

```toml
GROQ_API_KEY = "gsk_your_real_key"
```

4. Save the secrets and reboot/re-run the app.

The application reads `GROQ_API_KEY` from `st.secrets` on Streamlit Cloud and from `.env` during local development. It now shows a clear configuration message instead of the generic API-key exception. Do not commit real keys to GitHub; the committed `.env` contains no credential.

## Local installation

```bash
git clone https://github.com/Shukla2005/Sql-agent-webapp.git
cd Sql-agent-webapp
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set GROQ_API_KEY
streamlit run app.py
```

## Features

- Upload SQLite databases
- Explore tables and preview sample rows
- Ask natural-language questions
- Display generated read-only SQL
- Deploy on Streamlit Cloud
