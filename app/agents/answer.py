from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import config

class AnswerAgent:
    def __init__(self):
        self.llm = ChatOllama(model=config.LLM_MODEL, temperature=0.1) # Low temp for factual answers
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant. Use the following context to answer the user's question.
            If the answer is not in the context, say "I couldn't find the answer in the provided documents."
            Always cite the source (filename) if possible.
            Be concise. Do not repeat yourself.
            
            Context:
            {context}
            """),
            ("user", "{question}")
        ])
        
        self.chain = self.prompt | self.llm | StrOutputParser()

    def generate_answer(self, question: str, context_docs: list):
        # Format context
        context_text = "\n\n".join([f"Source: {doc.metadata.get('source', 'Unknown')}\nContent: {doc.page_content}" for doc in context_docs])
        
        print(f"Generating answer for: {question}")
        try:
            result = self.chain.invoke({"question": question, "context": context_text})
            print(f"Answer generated: {result}")
            return result
        except Exception as e:
            print(f"Error generating answer: {e}")
            return "I apologize, but I encountered an error while converting your request into an answer. Please check if the Ollama model is running."

if __name__ == "__main__":
    # Test with dummy context
    from langchain_core.documents import Document
    agent = AnswerAgent()
    docs = [Document(page_content="Refunds are processed within 30 days.", metadata={"source": "policy.pdf"})]
    print(agent.generate_answer("How long do refunds take?", docs))
