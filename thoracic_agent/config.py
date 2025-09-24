import os
import getpass
from langchain.chat_models import init_chat_model
from langchain_tavily import TavilySearch

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

model = init_chat_model("deepseek-chat", model_provider="deepseek", streaming=True)
search = TavilySearch(max_results=2)
tools = [search]
model_with_tools = model.bind_tools(tools)

thread_config = {"configurable": {"thread_id": "abc123"}}