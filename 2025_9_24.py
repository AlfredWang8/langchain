import getpass
import os

from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage,AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
import sys
from langchain_tavily import TavilySearch
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver  # an in-memory checkpointer
from langgraph.prebuilt import create_react_agent



try:
    # 加载环境配置（在.env文件中）
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

if not os.environ.get("LANGSMITH_API_KEY"):
  os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter API key for Langsmith: ")

if not os.environ.get("DEEPSEEK_API_KEY"):
  os.environ["DEEPSEEK_API_KEY"] = getpass.getpass("Enter API key for DeepSeek: ")

if not os.environ.get("TAVILY_API_KEY"):
  os.environ["TAVILY_API_KEY"] = getpass.getpass("Enter API key for Tavily: ")

model = init_chat_model("deepseek-chat", model_provider="deepseek",streaming=True)
search = TavilySearch(max_results=2)
tools = [search]
model_with_tools = model.bind_tools(tools)


# 定义函数模型
def call_model(state: MessagesState):
    response = model_with_tools.invoke(
        [
            SystemMessage(content = "你是一个专业的胸外科医生")
        ]
        +state["messages"])
    return {"messages": response}


# 定义新工作图
agent_builder = StateGraph(state_schema=MessagesState)


# 定义工作节点
agent_builder.add_edge(START, "model")
agent_builder.add_node("model", call_model)

# 添加记忆
memory = MemorySaver()
agent = agent_builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "abc123"}}

while True:
    query = input("用户提问：(输入exit退出)：")
    if "exit" == query:
        break
    input_messages = [HumanMessage(query)]

    # 流式输出
    for chunk, metadata in agent.stream(
            {"messages": input_messages},
            config,
            stream_mode="messages",
    ):
        if isinstance(chunk, AIMessage): # 只打印AI的消息
            print(chunk.content, end="")
