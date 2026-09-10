import streamlit as st
from dotenv import load_dotenv
from typing import Literal
import tempfile

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

st.set_page_config(
    page_title="SQL Agent",
    page_icon="🗄️",
    layout="wide"
)

st.markdown("""
    <style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .sql-query {
        background-color: #f0f0f0;
        padding: 1rem;
        border-radius: 0.5rem;
        font-family: monospace;
        margin: 1rem 0;
    }
    .upload-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 2px dashed #dee2e6;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🗄️ SQL Agent Assistant")
st.caption("Upload your database and ask questions in natural language")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = None
if "db" not in st.session_state:
    st.session_state.db = None
if "db_path" not in st.session_state:
    st.session_state.db_path = None
if "db_name" not in st.session_state:
    st.session_state.db_name = None


def initialize_agent(db_path: str):
    """Initialize the SQL agent with an uploaded SQLite database."""

    db = SQLDatabase.from_uri(f"sqlite:///{db_path}")

    # Updated Groq model.
    # qwen/qwen3-32b is no longer available on Groq.
    model = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    toolkit = SQLDatabaseToolkit(db=db, llm=model)
    tools = toolkit.get_tools()

    list_tables_tool = next(
        t for t in tools if t.name == "sql_db_list_tables"
    )
    get_schema_tool = next(
        t for t in tools if t.name == "sql_db_schema"
    )
    run_query_tool = next(
        t for t in tools if t.name == "sql_db_query"
    )

    def list_tables(state: MessagesState):
        tool_call = {
            "name": "sql_db_list_tables",
            "args": {},
            "id": "list_tables_call",
            "type": "tool_call",
        }

        tool_call_message = AIMessage(
            content="",
            tool_calls=[tool_call]
        )

        tool_message = list_tables_tool.invoke(tool_call)

        return {"messages": [tool_call_message, tool_message]}

    def call_get_schema(state: MessagesState):
        llm_with_tools = model.bind_tools(
            [get_schema_tool],
            tool_choice="any"
        )

        response = llm_with_tools.invoke(state["messages"])

        return {"messages": [response]}

    def generate_query(state: MessagesState):
        system_message = {
            "role": "system",
            "content": f"""
You are a SQL expert.

Create a {db.dialect} query to answer the user's question.

Rules:
1. Use only tables and columns that exist in the database.
2. Limit results to 5 unless the user specifies otherwise.
3. Only query relevant columns.
4. Do not modify the database.
5. Only generate SELECT queries or read-only SQL.
6. If the question cannot be answered from the database, explain why.
"""
        }

        llm_with_tools = model.bind_tools(
            [run_query_tool]
        )

        response = llm_with_tools.invoke(
            [system_message] + state["messages"]
        )

        return {"messages": [response]}

    def should_continue(
        state: MessagesState
    ) -> Literal[END, "run_query"]:

        last_message = state["messages"][-1]

        if not last_message.tool_calls:
            return END

        return "run_query"

    get_schema_node = ToolNode([get_schema_tool])
    run_query_node = ToolNode([run_query_tool])

    builder = StateGraph(MessagesState)

    builder.add_node("list_tables", list_tables)
    builder.add_node("call_get_schema", call_get_schema)
    builder.add_node("get_schema", get_schema_node)
    builder.add_node("generate_query", generate_query)
    builder.add_node("run_query", run_query_node)

    builder.add_edge(START, "list_tables")
    builder.add_edge("list_tables", "call_get_schema")
    builder.add_edge("call_get_schema", "get_schema")
    builder.add_edge("get_schema", "generate_query")
    builder.add_conditional_edges(
        "generate_query",
        should_continue
    )
    builder.add_edge("run_query", "generate_query")

    checkpointer = MemorySaver()

    agent = builder.compile(
        checkpointer=checkpointer
    )

    return agent, db


# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.header("Database Setup")

    st.markdown(
        '<div class="upload-section">',
        unsafe_allow_html=True
    )

    st.subheader("📤 Upload Database")

    uploaded_file = st.file_uploader(
        "Choose a SQLite database file (.db, .sqlite, .sqlite3)",
        type=["db", "sqlite", "sqlite3"],
        help="Upload your SQLite database file to query"
    )

    if uploaded_file is not None:

        if st.session_state.db_name != uploaded_file.name:

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".db"
            ) as tmp_file:

                tmp_file.write(
                    uploaded_file.getvalue()
                )

                st.session_state.db_path = tmp_file.name
                st.session_state.db_name = uploaded_file.name
                st.session_state.db = None
                st.session_state.agent = None
                st.session_state.messages = []

            st.success(
                f"Uploaded: {uploaded_file.name}"
            )

            st.info(
                "Start asking questions below!"
            )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

    # Show database information after initialization
    if st.session_state.db:
        st.subheader("Database Info")

        st.write(
            f"**Name:** {st.session_state.db_name}"
        )

        st.write(
            f"**Dialect:** {st.session_state.db.dialect}"
        )

        with st.expander(
            "Available Tables",
            expanded=True
        ):
            tables = (
                st.session_state.db
                .get_usable_table_names()
            )

            for i, table in enumerate(
                tables,
                1
            ):
                st.write(
                    f"{i}. `{table}`"
                )

        with st.expander("Sample Data"):
            selected_table = st.selectbox(
                "Select table to preview:",
                tables,
                key="preview_table"
            )

            if selected_table:
                try:
                    sample_query = (
                        f"SELECT * FROM "
                        f'"{selected_table}" LIMIT 3'
                    )

                    result = (
                        st.session_state.db
                        .run(sample_query)
                    )

                    st.code(
                        result,
                        language="text"
                    )

                except Exception as e:
                    st.error(
                        f"Error: {str(e)}"
                    )

    st.markdown("---")

    st.subheader("Options")

    if st.button(
        "Clear Chat",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.rerun()

    if (
        st.session_state.db
        and st.button(
            "🔄 Reset Database",
            use_container_width=True
        )
    ):
        st.session_state.db = None
        st.session_state.agent = None
        st.session_state.db_path = None
        st.session_state.db_name = None
        st.session_state.messages = []
        st.rerun()


# ---------------- MAIN CONTENT ----------------

if not st.session_state.db_path:

    st.info(
        "Please upload a SQLite database file "
        "from the sidebar to get started"
    )

    st.markdown("### How to use:")

    st.markdown("""
    1. **Upload** your SQLite database file
       (.db, .sqlite, .sqlite3)
    2. **Ask questions** in natural language
    3. **Get answers** - the AI will generate
       and run SQL queries automatically

    ### Example questions:

    - "What tables are in this database?"
    - "Show me the top 10 records from the sales table"
    - "What is the average price by category?"
    - "Find all customers from California"
    """)

else:

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input(
        "Ask a question about your database..."
    ):

        if st.session_state.agent is None:

            with st.spinner(
                "Initializing agent..."
            ):
                try:

                    (
                        st.session_state.agent,
                        st.session_state.db
                    ) = initialize_agent(
                        st.session_state.db_path
                    )

                except Exception as e:
                    st.error(
                        f"Error initializing agent: {str(e)}"
                    )
                    st.stop()

        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):

            message_placeholder = st.empty()
            full_response = ""

            with st.spinner("Thinking..."):

                try:

                    config = {
                        "configurable": {
                            "thread_id":
                            "streamlit_session"
                        }
                    }

                    steps_container = st.container()
                    sql_queries = []

                    for step in st.session_state.agent.stream(
                        {
                            "messages": [
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ]
                        },
                        config,
                        stream_mode="values"
                    ):

                        if "messages" not in step:
                            continue

                        last_message = (
                            step["messages"][-1]
                        )

                        # Display generated SQL
                        if (
                            hasattr(
                                last_message,
                                "tool_calls"
                            )
                            and last_message.tool_calls
                        ):

                            for tool_call in (
                                last_message.tool_calls
                            ):

                                if (
                                    tool_call["name"]
                                    == "sql_db_query"
                                ):

                                    query = (
                                        tool_call["args"]
                                        .get(
                                            "query",
                                            ""
                                        )
                                    )

                                    if (
                                        query
                                        and query
                                        not in sql_queries
                                    ):

                                        sql_queries.append(
                                            query
                                        )

                                        with steps_container:

                                            st.caption(
                                                "Generated SQL Query:"
                                            )

                                            st.code(
                                                query,
                                                language="sql"
                                            )

                        # Capture AI response
                        if (
                            isinstance(
                                last_message,
                                AIMessage
                            )
                            and last_message.content
                        ):

                            # Some models can return
                            # structured content. Convert it
                            # safely to text.
                            if isinstance(
                                last_message.content,
                                str
                            ):
                                full_response = (
                                    last_message.content
                                )
                            else:
                                full_response = str(
                                    last_message.content
                                )

                    if not full_response:
                        full_response = (
                            "I couldn't generate an answer."
                        )

                    message_placeholder.markdown(
                        full_response
                    )

                except Exception as e:

                    error_msg = (
                        f"Error: {str(e)}"
                    )

                    message_placeholder.error(
                        error_msg
                    )

                    full_response = error_msg

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_response
                }
            )

st.markdown("---")
