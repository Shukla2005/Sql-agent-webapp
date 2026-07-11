# 🗄️ SQL Agent - Natural Language Database Query Tool

Ask questions about your SQL database in plain English and get instant answers powered by AI!
## 🌟 Features

- 📤 **Upload Any SQLite Database** - Drag and drop your `.db`, `.sqlite`, or `.sqlite3` files
- 💬 **Natural Language Queries** - Ask questions in plain English, no SQL knowledge required
- 🤖 **AI-Powered SQL Generation** - Automatically generates and executes SQL queries
- 👀 **Transparent Process** - See the SQL queries being generated in real-time
- 📊 **Database Explorer** - Browse tables, view schemas, and preview sample data
- 🔒 **Secure & Private** - All processing happens locally, your data never leaves your machine
- ⚡ **Fast & Responsive** - Built with Streamlit for instant feedback
- 🎨 **Clean UI** - Modern, intuitive interface inspired by ChatGPT

## 🚀 Demo

https://sql-agent-webapp-airekgjmyfzyymwuffhyv3.streamlit.app/

**Try asking:**
- "What tables are in this database?"
- "Show me the top 10 customers by total purchases"
- "What is the average order value by country?"
- "Find all products that are out of stock"

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [Configuration](#configuration)
- [Sample Databases](#sample-databases)
- [Deployment](#deployment)
- [Architecture](#architecture)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- OpenAI API key or Anthropic API key (for Claude)

### Step 1: Clone the Repository
```bash
git clone https://github.com/Arjit-Shukla7/Sql-agent-webapp.git
cd sql-agent-webapp
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables
```bash
# Copy the example environment file
cp .env.example .env
```

Edit `.env` and add your API keys:
```bash
# Choose ONE of these:
OPENAI_API_KEY=sk-your-openai-key-here
# OR
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Optional: For LangSmith tracing
LANGCHAIN_API_KEY=your-langchain-key-here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=sql-agent
```

## 🎯 Quick Start

### Run Locally
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### First Steps

1. **Upload a database** - Click "Browse files" in the sidebar
2. **Explore your data** - Check the "Available Tables" section
3. **Ask a question** - Type in the chat input and press Enter
4. **View results** - See the generated SQL and natural language answer

## 📖 Usage Guide

### Uploading a Database

1. Click **"Browse files"** in the sidebar
2. Select your SQLite database file (`.db`, `.sqlite`, `.sqlite3`)
3. Wait for the upload to complete
4. The app will automatically display available tables

### Asking Questions

**General Questions:**
```
- "What tables are available?"
- "Describe the schema of the customers table"
- "How many records are in the orders table?"
```

**Analytical Questions:**
```
- "What are the top 5 selling products?"
- "Show me monthly sales trends"
- "Which customers haven't made a purchase in the last 30 days?"
```

**Comparative Questions:**
```
- "Compare sales between regions"
- "What's the difference in average order value by customer segment?"
```

**Aggregation Questions:**
```
- "What is the total revenue this year?"
- "Calculate average, min, and max order values"
- "Group sales by category and show totals"
```

### Understanding the Output

Each response includes:

1. **🔍 Generated SQL Query** - The actual SQL executed (shown in code block)
2. **💬 Natural Language Answer** - AI-generated explanation of the results
3. **📊 Raw Results** - Data returned from the query

### Database Explorer

**Available Tables:**
- View all tables in your database
- Click on a table name to see its schema

**Sample Data Preview:**
- Select any table from the dropdown
- View the first 3 rows of data
- Useful for understanding data structure

### Managing Sessions

**Clear Chat:**
- Click "🗑️ Clear Chat" to start a new conversation
- Previous queries are removed but database stays connected

**Reset Database:**
- Click "🔄 Reset Database" to disconnect current database
- Upload a new database to analyze different data

## ⚙️ Configuration

### Choosing Your LLM

The app supports multiple LLM providers. Edit `app.py` to switch:

**OpenAI (GPT-4):**
```python
from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="gpt-4", temperature=0)
```

**Anthropic (Claude):**
```python
from langchain_anthropic import ChatAnthropic
model = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0)
```

**Groq (Fast & Free Tier):**
```python
from langchain_groq import ChatGroq
model = ChatGroq(model="mixtral-8x7b-32768", temperature=0)
```

### Customizing Query Limits

In `app.py`, find the `generate_query` function:
```python
system_message = {
    "role": "system",
    "content": f"""You are a SQL expert. Create a {db.dialect} query to answer the question.
    Limit results to 5 unless specified otherwise.  # Change this number
    Only query relevant columns."""
}
```

### Enabling LangSmith Tracing

For debugging and monitoring:
```bash
# In .env file:
LANGCHAIN_API_KEY=your-key-here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=sql-agent
```

View traces at: https://smith.langchain.com

## 📦 Sample Databases

### Download Sample Databases

**1. Chinook (Music Store Database)**
```bash
curl -o Chinook.db https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite
```

Contains: Artists, Albums, Tracks, Customers, Invoices, Employees

**Sample Questions:**
- "Which artist has the most albums?"
- "What are the top 5 selling tracks?"
- "Show me customer purchase history"

---

**2. Northwind (Sales & Inventory)**
```bash
curl -o Northwind.db https://github.com/jpwhite3/northwind-SQLite3/raw/main/dist/northwind.db
```

Contains: Products, Orders, Customers, Suppliers, Categories

**Sample Questions:**
- "What products are low in stock?"
- "Show me sales by category"
- "Which suppliers provide the most products?"

---

**3. Create Your Own**
```python
import sqlite3
import pandas as pd

# Create database
conn = sqlite3.connect('mydata.db')

# Create table from CSV
df = pd.read_csv('your_data.csv')
df.to_sql('your_table', conn, if_exists='replace', index=False)

conn.close()
```

## 🌐 Deployment

### Deploy to Streamlit Cloud (Free!)

**Step 1: Push to GitHub**
```bash
# Make sure .env is in .gitignore
git add .
git commit -m "Ready for deployment"
git push origin main
```

**Step 2: Deploy on Streamlit Cloud**

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Connect your GitHub account
4. Select repository: `Arjit-Shukla7/Sql-agent-webapp`
5. Set main file path: `app.py`
6. Click **"Advanced settings"**

**Step 3: Add Secrets**

In the "Secrets" section, add:
```toml
OPENAI_API_KEY = "sk-your-actual-key-here"
# OR
ANTHROPIC_API_KEY = "sk-ant-your-actual-key-here"

# Optional:
LANGCHAIN_API_KEY = "your-langchain-key"
```

**Step 4: Deploy!**

Click "Deploy" and wait 2-3 minutes. Your app will be live at:
```
https://your-app-name.streamlit.app
```

### Alternative Deployment Options

**Docker:**
```bash
# Coming soon - Dockerfile included
docker build -t sql-agent .
docker run -p 8501:8501 sql-agent
```

**Railway.app:**
- Connect GitHub repo
- Add environment variables
- Deploy with one click

**Render.com:**
- Free tier available
- Auto-deploys from GitHub

## 🏗️ Architecture

### Technology Stack

- **Frontend:** Streamlit (Python web framework)
- **Agent Framework:** LangGraph (workflow orchestration)
- **LLM Integration:** LangChain (tool calling & prompts)
- **Database:** SQLite (via SQLAlchemy)
- **State Management:** LangGraph MemorySaver

### How It Works
```
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

### Agent Workflow

1. **List Tables** - Get all available tables
2. **Get Schema** - Retrieve table structures
3. **Generate Query** - LLM creates SQL based on question
4. **Execute Query** - Run SQL against database
5. **Format Response** - Convert results to natural language

### File Structure
```
sql-agent-webapp/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── README.md             # This file
└── .streamlit/
    └── config.toml       # Streamlit configuration (optional)
```

## 🐛 Troubleshooting

### Common Issues

**1. "Module not found" error**
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**2. "API key not found" error**
```bash
# Solution: Check .env file exists and has correct keys
cat .env
# Make sure you've loaded environment variables
```

**3. "Database file not found"**
```bash
# Solution: Make sure database file is uploaded
# Check the file path in sidebar
```

**4. "SQL execution error"**
```bash
# Solution: 
# - Check if table names are correct
# - Verify database isn't corrupted
# - Try with a sample database first
```

**5. "Rate limit exceeded"**
```bash
# Solution:
# - Check your API key limits
# - Wait a few minutes and try again
# - Consider upgrading your API plan
```

**6. Streamlit won't start**
```bash
# Solution: Check if port 8501 is in use
lsof -ti:8501 | xargs kill -9  # macOS/Linux
# Or use a different port
streamlit run app.py --server.port 8502
```

### Getting Help

- 📖 Check the [LangChain Documentation](https://python.langchain.com/docs)
- 💬 Open an issue on [GitHub Issues](https://github.com/Arjit-Shukla7/Sql-agent-webapp/issues)
- 🐦 Tweet at [@langchainai](https://twitter.com/langchainai)

## 🤝 Contributing

Contributions are welcome! Here's how:

### Reporting Bugs

1. Check if the bug is already reported in [Issues](https://github.com/Arjit-Shukla7/Sql-agent-webapp/issues)
2. If not, create a new issue with:
   - Clear title
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable

### Suggesting Features

1. Open a new issue with the `enhancement` label
2. Describe the feature and why it would be useful
3. Include examples if possible

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Development Setup
```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/Sql-agent-webapp.git

# Create development branch
git checkout -b dev

# Install in development mode
pip install -e .

# Run tests (if added)
pytest tests/
```



This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```
MIT License

Copyright (c) 2025 Arjit Shukla

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```
## 📧 Contact

**Arjit Shukla**
- GitHub: [@Arjit-Shukla7](https://github.com/Arjit-Shukla7)
- Project Link: [https://github.com/Arjit-Shukla7/Sql-agent-webapp](https://github.com/Arjit-Shukla7/Sql-agent-webapp)
MIT License

Copyright (c) 2025 Arjit Shukla

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
