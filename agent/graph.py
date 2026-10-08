import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import os
from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from agent.state import AgentState
from agent.tools import TOOLS, get_balance, get_ledger, credit_wallet, debit_wallet


def get_model():
    api_key = os.getenv("GOOGLE_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    return ChatGoogleGenerativeAI(
        model=model_name,
        api_key=api_key,
        max_retries=2
    ).bind_tools(TOOLS)


async def call_model(state: AgentState) -> dict:
    jwt_token = state.get("jwt_token", "")
    system_prompt = SystemMessage(
        content=(
            "You are a Financial Wallet AI Assistant. "
            "Help the user check balance, view transaction ledger, credit wallet, or debit wallet. "
            f"When invoking any tool, you MUST pass jwt_token='{jwt_token}' as an argument."
        )
    )
    messages = [system_prompt] + list(state["messages"])
    model = get_model()
    response = await model.ainvoke(messages)
    return {"messages": [response]}


# Tool names that require HITL approval (financial writes only)
FINANCIAL_TOOL_NAMES = {"credit_wallet", "debit_wallet"}

# Separate ToolNodes: safe reads (no HITL) and financial writes (HITL before execution)
safe_tools_node = ToolNode([get_balance, get_ledger])
financial_tools_node = ToolNode([credit_wallet, debit_wallet])


def should_continue(state: AgentState) -> str:
    """Route to safe_tools, financial_tools, or END depending on the requested tool."""
    messages = state["messages"]
    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_name = last_message.tool_calls[0].get("name", "")
        if tool_name in FINANCIAL_TOOL_NAMES:
            return "financial_tools"
        return "safe_tools"
    return END


# Build the graph
builder = StateGraph(AgentState)
builder.add_node("agent", call_model)
builder.add_node("safe_tools", safe_tools_node)
builder.add_node("financial_tools", financial_tools_node)

builder.add_edge(START, "agent")
builder.add_conditional_edges(
    "agent",
    should_continue,
    ["safe_tools", "financial_tools", END]
)
builder.add_edge("safe_tools", "agent")
builder.add_edge("financial_tools", "agent")


def get_db_conn_string() -> str:
    db_url = os.getenv("DATABASE_URL", "")
    return db_url.replace("postgresql+psycopg://", "postgresql://")


async def create_checkpointer():
    conn_str = get_db_conn_string()
    checkpointer = AsyncPostgresSaver.from_conn_string(conn_str)
    return checkpointer


def compile_graph(checkpointer):
    return builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["financial_tools"]  # HITL only for credit_wallet and debit_wallet
    )
