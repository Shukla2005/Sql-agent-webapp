import os
import tempfile
from typing import Literal

import streamlit as st
from dotenv import load_dotenv
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import AIMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

# Local .env is useful for development. Streamlit Cloud values are read from
# st.secrets below; Streamlit secrets are not automatically environment vars.
load_dotenv()

st.set_page_config(page_title="SQL Agent", page_icon="🗄️", layout="wide")


def get_groq_api_key() -> str | None:
    """Read the Groq key from Streamlit Cloud secrets or a local environment."""
    try:
        secret_key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        # st.secrets raises when no secrets file exists (normal local setup).
        secret_key = None

    key = secret_key or os.getenv("GROQ_API_KEY")
    if not key:
        return None

    key = str(key).strip().strip('"').strip("'")
    # Do not treat the old placeholder from a copied .env file as a real key.
    if not key or key in {"gsk-your-actual-key", "your-actual-key"}:
        return None
    return key


def missing_key_message() -> str:
    return (
        "Groq API key is not configured. Add `GROQ_API_KEY` in Streamlit Cloud "
        "under Settings → Secrets, or set it in a local `.env` file, then "
        "restart the app."
    )


def initialize_agent(db_path: str):
    """Initialize the SQL agent with an uploaded SQLite database."""
    api_key = get_groq_api_key()
    if not api_key:
        raise RuntimeError(missing_key_message())

    db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
    model = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=api_key,
    )

    toolkit = SQLDatabaseToolkit(db=db, llm=model)
    tools = toolkit.get_tools()
    list_tables_tool = next(t for t in tools if t.name == "sql_db_list_tables")
    get_schema_tool = next(t for t in tools if t.name == "sql_db_schema")
    run_query_tool = next(t for t in tools if t.name == "sql_db_query")

    def list_tables(state: MessagesState):
        tool_call = {
            "name": "sql_db_list_tables",
            "args": {},
            "id": "list_tables_call",
            "type": "tool_call",
        }
        tool_call_message = AIMessage(content="", tool_calls=[tool_call])
        tool_message = list_tables_tool.invoke(tool_call)
        return {"messages": [tool_call_message, tool_message]}

    def call_get_schema(state: MessagesState):
        response = model.bind_tools([get_schema_tool], tool_choice="any").invoke(
            state["messages"]
        )
        return {"messages": [response]}

    def generate_query(state: MessagesState):
        system_message = {
            "role": "system",
            "content": f"""You are a SQL expert.

Create a {db.dialect} query to answer the user's question.
Rules:
1. Use only tables and columns that exist in the database.
2. Limit results to 5 unless the user specifies otherwise.
3. Only query relevant columns.
4. Do not modify the database.
5. Only generate SELECT queries or read-only SQL.
6. If the question cannot be answered from the database, explain why.""",
        }
        response = model.bind_tools([run_query_tool]).invoke(
            [system_message] + state["messages"]
        )
        return {"messages": [response]}

    def should_continue(state: MessagesState) -> Literal[END, "run_query"]:
        return "run_query" if state["messages"][-1].tool_calls else END

    builder = StateGraph(MessagesState)
    builder.add_node("list_tables", list_tables)
    builder.add_node("call_get_schema", call_get_schema)
    builder.add_node("get_schema", ToolNode([get_schema_tool]))
    builder.add_node("generate_query", generate_query)
    builder.add_node("run_query", ToolNode([run_query_tool]))
    builder.add_edge(START, "list_tables")
    builder.add_edge("list_tables", "call_get_schema")
    builder.add_edge("call_get_schema", "get_schema")
    builder.add_edge("get_schema", "generate_query")
    builder.add_conditional_edges("generate_query", should_continue)
    builder.add_edge("run_query", "generate_query")
    return builder.compile(checkpointer=MemorySaver()), db


st.title("🗄️ SQL Agent Assistant")
st.caption("Upload your database and ask questions in natural language")

for key, default in {
    "messages": [], "agent": None, "db": None, "db_path": None, "db_name": None
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

with st.sidebar:
    st.header("Database Setup")
    uploaded_file = st.file_uploader(
        "Choose a SQLite database file (.db, .sqlite, .sqlite3)",
        type=["db", "sqlite", "sqlite3"],
        help="Upload your SQLite database file to query",
    )
    if uploaded_file is not None and st.session_state.db_name != uploaded_file.name:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            st.session_state.db_path = tmp_file.name
        st.session_state.db_name = uploaded_file.name
        st.session_state.db = None
        st.session_state.agent = None
        st.session_state.messages = []
        st.success(f"Uploaded: {uploaded_file.name}")

    if not get_groq_api_key():
        st.warning("Groq API key is not configured.")
        st.caption("Set GROQ_API_KEY in Streamlit Cloud → Settings → Secrets.")

    if st.session_state.db:
        st.subheader("Database Info")
        st.write(f"**Name:** {st.session_state.db_name}")
        st.write(f"**Dialect:** {st.session_state.db.dialect}")
        tables = st.session_state.db.get_usable_table_names()
        with st.expander("Available Tables", expanded=True):
            for number, table in enumerate(tables, 1):
                st.write(f"{number}. `{table}`")
        if tables:
            with st.expander("Sample Data"):
                selected_table = st.selectbox("Select table to preview:", tables)
                try:
                    st.code(
                        st.session_state.db.run(
                            f'SELECT * FROM "{selected_table}" LIMIT 3'
                        ),
                        language="text",
                    )
                except Exception as exc:
                    st.error(f"Error: {exc}")

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    if st.session_state.db and st.button("🔄 Reset Database", use_container_width=True):
        for key in ("db", "agent", "db_path", "db_name"):
            st.session_state[key] = None
        st.session_state.messages = []
        st.rerun()

if not st.session_state.db_path:
    st.info("Please upload a SQLite database file from the sidebar to get started.")
else:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question about your database..."):
        if st.session_state.agent is None:
            with st.spinner("Initializing agent..."):
                try:
                    st.session_state.agent, st.session_state.db = initialize_agent(
                        st.session_state.db_path
                    )
                except Exception as exc:
                    st.error(str(exc))
                    st.stop()

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""
            sql_queries = []
            try:
                config = {"configurable": {"thread_id": "streamlit_session"}}
                for step in st.session_state.agent.stream(
                    {"messages": [{"role": "user", "content": prompt}]},
                    config,
                    stream_mode="values",
                ):
                    if "messages" not in step:
                        continue
                    last_message = step["messages"][-1]
                    for tool_call in getattr(last_message, "tool_calls", []):
                        if tool_call["name"] == "sql_db_query":
                            query = tool_call["args"].get("query", "")
                            if query and query not in sql_queries:
                                sql_queries.append(query)
                                st.caption("Generated SQL Query:")
                                st.code(query, language="sql")
                    if isinstance(last_message, AIMessage) and last_message.content:
                        full_response = (
                            last_message.content
                            if isinstance(last_message.content, str)
                            else str(last_message.content)
                        )
                full_response = full_response or "I couldn't generate an answer."
                placeholder.markdown(full_response)
            except Exception as exc:
                full_response = f"Error: {exc}"
                placeholder.error(full_response)
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )
