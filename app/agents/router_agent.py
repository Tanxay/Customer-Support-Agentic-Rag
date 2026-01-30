from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.core.config import config

class RouterAgent:
    def __init__(self):
        self.llm = ChatOllama(model=config.LLM_MODEL, format="json", temperature=0)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert query router. Your job is to route the user's query to the correct data source.
            
            Available Data Sources:
            1. 'vector_store': Use this for questions about policies, procedures, manuals, or general text found in PDF/Text documents.
            2. 'excel_sheet': Use this for questions about specific data rows, error codes, inventory numbers, or structured tabular data.
            3. 'general_chat': Use this for greetings, or questions that don't look like they need external data.
            
            Return ONLY a JSON object with the following format:
            {{
                "datasource": "vector_store" | "excel_sheet" | "general_chat",
                "reasoning": "brief explanation"
            }}
            """),
            ("user", "{question}")
        ])
        
        self.chain = self.prompt | self.llm | JsonOutputParser()

    def route(self, question: str):
        print(f"Routing query: {question}")
        try:
            result = self.chain.invoke({"question": question})
            print(f"Route decision: {result}")
            return result
        except Exception as e:
            print(f"Routing error: {e}")
            return {"datasource": "general_chat", "reasoning": "Error in routing, defaulting to general chat"}

if __name__ == "__main__":
    # Test the router
    router = RouterAgent()
    router.route("What is the refund policy?")
    router.route("Look up error code 505 in the database")
    router.route("Hi, how are you?")
