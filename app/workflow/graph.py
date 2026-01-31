from typing import TypedDict, List
from langgraph.graph import StateGraph, END

from app.agents.sql_agent import SQLAgent
from app.agents.router import RouterAgent
from app.agents.retrieval import RetrievalAgent
from app.agents.answer import AnswerAgent
from langchain_core.documents import Document

# Define State
class AgentState(TypedDict):
    question: str
    documents: List[Document]
    generation: str
    datasource: str

# Initialize Agents
router = RouterAgent()
retriever = RetrievalAgent()
answerer = AnswerAgent()
sql_agent = SQLAgent()

# Define Nodes
def router_node(state: AgentState):
    print("---ROUTER---")
    question = state["question"]
    route_result = router.route(question)
    return {"datasource": route_result["datasource"]}

def retrieve_node(state: AgentState):
    print("---RETRIEVE---")
    question = state["question"]
    # We retrieve from Milvus for both vector_store and excel_sheet 
    # (since we indexed excel rows as text)
    documents = retriever.retrieve(question)
    return {"documents": documents}

def generate_node(state: AgentState):
    print("---GENERATE---")
    question = state["question"]
    docs = state.get("documents", [])
    answer = answer_agent.generate_answer(question, docs)
    return {"answer": answer}

def sql_node(state: AgentState):
    question = state["question"]
    print("---SQL AGENT---")
    answer = sql_agent.query(question)
    return {"answer": answer, "datasource": "structured_db"} # structured_db source

# Determine Next Step
def route_query(state: AgentState):
    datasource = state.get("datasource")
    if datasource == "vector_store" or datasource == "excel_sheet":
        return "retrieval"
    elif datasource == "structured_query":
        return "sql_agent"
    else:
        return "answer"

# Build Graph
workflow = StateGraph(AgentState)

workflow.add_node("router", router_node)
workflow.add_node("retrieval", retrieval_node)
workflow.add_node("answer", answer_node)
workflow.add_node("sql_agent", sql_node) # Add node

workflow.set_entry_point("router")

workflow.add_conditional_edges(
    "router",
    route_query,
    {
        "retrieval": "retrieval",
        "sql_agent": "sql_agent",
        "answer": "answer"
    }
)

workflow.add_edge("retrieval", "answer")
workflow.add_edge("answer", END)
workflow.add_edge("sql_agent", END) # SQL agent ends directly

app_graph = workflow.compile()
