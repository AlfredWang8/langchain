import getpass
import os

from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage,AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
import sys
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder





try:
    # 加载环境配置（在.env文件中）
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

if not os.environ.get("DEEPSEEK_API_KEY"):
  os.environ["DEEPSEEK_API_KEY"] = getpass.getpass("Enter API key for DeepSeek: ")


model = init_chat_model("deepseek-chat", model_provider="deepseek",streaming=True)

# 定义新工作图
workflow = StateGraph(state_schema=MessagesState)

# 系统提示词
prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a doctor.Answer all questions to the best of your ability.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)


# 定义函数模型
def call_model(state: MessagesState):
    prompt=prompt_template.format(messages=state["messages"])
    response = model.invoke(state["messages"])
    return {"messages": response}


# 定义工作节点
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

# 添加记忆
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "abc123"}}

while True:
    query = input("用户提问：(输入exit退出)：")
    if "exit" == query:
        break
    input_messages = [HumanMessage(query)]

    # 流式输出
    for chunk, metadata in app.stream(
            {"messages": input_messages},
            config,
            stream_mode="messages",
    ):
        if isinstance(chunk, AIMessage): # 只打印AI的消息
            print(chunk.content, end="")



