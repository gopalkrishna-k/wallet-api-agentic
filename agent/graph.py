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
from agent.tools import TOOLS

# Initialize Model
api_key = os.getenv("GOOGLE_API_KEY")
model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

model = ChatGoogleGenerativeAI(
    model=model_name,
    api_key=api_key,
    max_retries=5
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
    response = await model.ainvoke(messages)
    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    messages = state["messages"]
    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


# Create Workflow Graph
builder = StateGraph(AgentState)
builder.add_node("agent", call_model)
builder.add_node("tools", ToolNode(TOOLS))

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue, ["tools", END])
builder.add_edge("tools", "agent")


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
        interrupt_before=["tools"]  # Human-In-The-Loop approval before financial tool execution
    )

