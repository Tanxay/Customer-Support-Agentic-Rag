from typing import TypedDict, List
from langgraph.graph import StateGraph, END

from app.agents.router_agent import RouterAgent
from app.agents.retrieval_agent import RetrievalAgent
from app.agents.answer_agent import AnswerAgent
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
    documents = state.get("documents", [])
    datasource = state.get("datasource", "general_chat")
    
    if datasource == "general_chat" and not documents:
        # For general chat, we might want to skip context or perform a simple chat
        # But here we use the same agent, maybe passing empty context/instruction
        # Ideally AnswerAgent should handle "no context" gracefully or we use a different prompt.
        # Let's just pass empty docs, AnswerAgent will say "I couldn't find answer..." 
        # So we should modify AnswerAgent to be chatty if context is empty, OR
        # better: use a separate 'chat_node' for general chat.
        # For now, let's keep it simple: AnswerAgent tries to answer.
        # But let's add a small hack: if general search, we don't retrieve, so docs is empty.
        pass

    generation = answerer.generate_answer(question, documents)
    return {"generation": generation}

# Define Conditional Edge
def route_decision(state: AgentState):
    datasource = state["datasource"]
    if datasource == "vector_store" or datasource == "excel_sheet":
        return "retrieve"
    else:
        return "generate"

# Build Graph
workflow = StateGraph(AgentState)

workflow.add_node("router", router_node)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("generate", generate_node)

workflow.set_entry_point("router")

workflow.add_conditional_edges(
    "router",
    route_decision,
    {
        "retrieve": "retrieve",
        "generate": "generate"
    }
)

workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

app_graph = workflow.compile()
