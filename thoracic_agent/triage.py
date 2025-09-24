from triage import triage_node
from langchain_core.messages import SystemMessage, HumanMessage
from config import model_with_tools, thread_config
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.checkpoint.memory import MemorySaver  # an in-memory checkpointer

#定义输入
while True:
    query = input("用户提问：(输入exit退出)：")
    if "exit" == query:
        break
    input_messages = [HumanMessage(query)]
    state = {"messages": input_messages}

    #分类路由
    triage_result = triage_node(state)
    category = triage_result["category"]
    messages = triage_result["messages"]
    if category == "treatment" or category == "diagnostic":
        print("进入治疗或检查流程")
        break

