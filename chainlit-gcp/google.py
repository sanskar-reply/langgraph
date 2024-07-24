from typing import Annotated
from typing_extensions import TypedDict
import os
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_google_community import GoogleSearchAPIWrapper
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
import chainlit as cl

# Set up environment variables for API keys
# os.environ["GOOGLE_CSE_ID"] = ""
# os.environ["GOOGLE_API_KEY"] = ""
load_dotenv()
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# Initialize in-memory checkpointer
memory = SqliteSaver.from_conn_string(":memory:")
# Initialize language model
llm = ChatOpenAI(model="gpt-4-1106-preview")
# Initialize Google search tool
search = GoogleSearchAPIWrapper()
tool = Tool(
    name="google_search",
    description="Search Google for recent results.",
    func=search.run,
)
tools = [tool]
llm_with_tools = llm.bind_tools(tools)

class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")
graph = graph_builder.compile(checkpointer=memory)

while True:
    config = {"configurable": {"thread_id": "1"}}
    user_input = input("Query:")
    events = graph.stream(
        {"messages": [("user", user_input)]}, config, stream_mode="values"
    )
    for event in events:
        if "messages" in event:
            event["messages"][-1].pretty_print()
