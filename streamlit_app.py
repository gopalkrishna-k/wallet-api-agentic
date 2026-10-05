import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import os
from dotenv import load_dotenv

load_dotenv()

import httpx
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from agent.graph import compile_graph, create_checkpointer

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(
    page_title="Wallet AI Agent",
    page_icon="💳",
    layout="wide"
)


# Helper function to run async coroutines safely in Streamlit
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


# Session State Initialization
if "jwt_token" not in st.session_state:
    st.session_state["jwt_token"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None


# --- AUTHENTICATION SCREEN ---
if not st.session_state["jwt_token"]:
    st.title("💳 Wallet API Agent - Login")
    st.caption("Secure Agentic Financial Assistant powered by FastAPI, MCP & LangGraph")

    tab1, tab2 = st.tabs(["🔒 Login", "📝 Register"])

    with tab1:
        st.subheader("Sign In")
        login_user = st.text_input("Username", key="login_username")
        login_pass = st.text_input("Password", type="password", key="login_password")
        if st.button("Log In", type="primary"):
            if not login_user or not login_pass:
                st.error("Please enter both username and password.")
            else:
                try:
                    res = httpx.post(
                        f"{API_BASE_URL}/auth/login",
                        json={"username": login_user, "password": login_pass},
                        timeout=10.0
                    )
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state["jwt_token"] = data["access_token"]
                        st.session_state["username"] = login_user
                        st.session_state["user_id"] = login_user
                        st.success("Successfully logged in!")
                        st.rerun()
                    else:
                        detail = res.json().get("detail", "Login failed")
                        st.error(f"Login failed: {detail}")
                except Exception as e:
                    st.error(f"Could not connect to backend server at {API_BASE_URL}. Ensure uvicorn is running.")

    with tab2:
        st.subheader("Create New Account")
        reg_user = st.text_input("Choose Username", key="reg_username")
        reg_email = st.text_input("Email Address", key="reg_email")
        reg_pass = st.text_input("Password", type="password", key="reg_password")
        if st.button("Register & Login", type="primary"):
            if not reg_user or not reg_email or not reg_pass:
                st.error("Please fill in all registration fields.")
            else:
                try:
                    res = httpx.post(
                        f"{API_BASE_URL}/auth/register",
                        json={"username": reg_user, "email": reg_email, "password": reg_pass},
                        timeout=10.0
                    )
                    if res.status_code == 201:
                        data = res.json()
                        st.session_state["jwt_token"] = data["access_token"]
                        st.session_state["username"] = reg_user
                        st.session_state["user_id"] = reg_user
                        st.success("Registration successful!")
                        st.rerun()
                    else:
                        detail = res.json().get("detail", "Registration failed")
                        st.error(f"Registration failed: {detail}")
                except Exception as e:
                    st.error(f"Could not connect to backend server at {API_BASE_URL}. Ensure uvicorn is running.")

    st.stop()


# --- LOGGED IN USER INTERFACE ---
token = st.session_state["jwt_token"]
username = st.session_state["username"]
thread_id = f"thread_{username}"
config = {"configurable": {"thread_id": thread_id}}

# --- SIDEBAR DASHBOARD ---
with st.sidebar:
    st.title(f"👤 {username}")
    if st.button("🚪 Log Out"):
        st.session_state["jwt_token"] = None
        st.session_state["username"] = None
        st.session_state["user_id"] = None
        st.rerun()

    st.divider()
    st.subheader("💰 Wallet Overview")

    # Fetch live balance
    headers = {"Authorization": f"Bearer {token}"}
    try:
        bal_res = httpx.get(f"{API_BASE_URL}/wallet/balance", headers=headers, timeout=5.0)
        if bal_res.status_code == 200:
            balance = bal_res.json().get("balance", "0.00")
            st.metric(label="Current Balance", value=f"${float(balance):,.2f}")
        else:
            st.warning("Could not load balance.")
    except Exception:
        st.warning("Backend offline.")

    # Ledger history expander
    with st.expander("📜 Transaction Ledger"):
        try:
            led_res = httpx.get(f"{API_BASE_URL}/wallet/ledger", headers=headers, timeout=5.0)
            if led_res.status_code == 200:
                entries = led_res.json()
                if entries:
                    for entry in entries:
                        st.caption(
                            f"**{entry['transaction_type']}** | ${float(entry['amount']):.2f} | "
                            f"Bal: ${float(entry['balance_after']):.2f}"
                        )
                else:
                    st.info("No transactions yet.")
        except Exception:
            st.caption("Unable to load ledger.")


# --- MAIN CHAT AREA ---
st.title("💳 Wallet AI Assistant")
st.caption("Ask questions about your balance, view ledger history, or make credits/debits.")


# Graph execution helper functions
async def get_graph_state():
    checkpointer_cm = await create_checkpointer()
    async with checkpointer_cm as cp:
        graph = compile_graph(cp)
        state = await graph.aget_state(config)
        return graph, state


async def process_user_prompt(prompt: str):
    checkpointer_cm = await create_checkpointer()
    async with checkpointer_cm as cp:
        graph = compile_graph(cp)
        input_state = {
            "messages": [HumanMessage(content=prompt)],
            "jwt_token": token,
            "user_id": username
        }
        async for _ in graph.astream(input_state, config=config):
            pass


async def resume_graph_approval():
    checkpointer_cm = await create_checkpointer()
    async with checkpointer_cm as cp:
        graph = compile_graph(cp)
        async for _ in graph.astream(None, config=config):
            pass


async def reject_graph_approval():
    checkpointer_cm = await create_checkpointer()
    async with checkpointer_cm as cp:
        graph = compile_graph(cp)
        state = await graph.aget_state(config)
        if state.values.get("messages"):
            last_msg = state.values["messages"][-1]
            if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                tc = last_msg.tool_calls[0]
                rejection_msg = ToolMessage(
                    content=f"User REJECTED the financial transaction '{tc['name']}' of amount {tc['args'].get('amount')}.",
                    tool_call_id=tc['id'],
                    name=tc['name']
                )
                await graph.aupdate_state(config, {"messages": [rejection_msg]}, as_node="tools")
                async for _ in graph.astream(None, config=config):
                    pass


# Load graph state
graph, current_state = run_async(get_graph_state())

# Render message history
messages = current_state.values.get("messages", [])
for msg in messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.write(msg.content)
    elif isinstance(msg, AIMessage):
        if msg.content:
            text_content = ""
            if isinstance(msg.content, list):
                for part in msg.content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        text_content += part.get("text", "")
            else:
                text_content = str(msg.content)

            if text_content.strip():
                with st.chat_message("assistant"):
                    st.write(text_content)


# Check for Human-In-The-Loop (HITL) Interruption
is_interrupted = current_state.next == ("tools",)
pending_tool_call = None

if is_interrupted and messages:
    last_msg = messages[-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        pending_tool_call = last_msg.tool_calls[0]

# If interrupted at financial operation, show HITL Approval Card
if is_interrupted and pending_tool_call:
    tool_name = pending_tool_call.get("name")
    tool_args = pending_tool_call.get("args", {})
    amount = tool_args.get("amount", 0.0)
    desc = tool_args.get("description", "No description provided.")

    st.warning("⚠️ **HUMAN APPROVAL REQUIRED FOR FINANCIAL OPERATION**")
    with st.container(border=True):
        st.subheader("Financial Operation Details")
        st.markdown(f"**Action:** `{tool_name}`")
        st.markdown(f"**Amount:** `${float(amount):,.2f}`")
        st.markdown(f"**Description:** {desc}")

        col_approve, col_reject = st.columns(2)
        if col_approve.button("Approve ✅", type="primary", use_container_width=True):
            with st.spinner("Processing approved transaction..."):
                run_async(resume_graph_approval())
            st.rerun()

        if col_reject.button("Reject ❌", use_container_width=True):
            with st.spinner("Cancelling transaction..."):
                run_async(reject_graph_approval())
            st.rerun()


# Chat input for user
user_input = st.chat_input("Ask your wallet assistant...", disabled=is_interrupted)
if user_input:
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            run_async(process_user_prompt(user_input))

    st.rerun()
