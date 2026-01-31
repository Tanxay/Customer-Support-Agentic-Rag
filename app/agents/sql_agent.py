from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.chat_models import ChatOllama
from app.core.config import config

class SQLAgent:
    def __init__(self):
        # Initialize DB
        self.db = SQLDatabase.from_uri("sqlite:///data/orders.db")
        
        # Initialize LLM
        self.llm = ChatOllama(model=config.LLM_MODEL, temperature=0)
        
        # Create Toolkit & Agent
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        self.agent_executor = create_sql_agent(
            llm=self.llm,
            toolkit=self.toolkit,
            verbose=True,
            handle_parsing_errors=True
        )

    def query(self, user_query: str):
        print(f"Executing SQL Query for: {user_query}")
        try:
            # The agent will: 1. Get Table Info, 2. Generate SQL, 3. Execute, 4. Answer
            response = self.agent_executor.invoke(user_query)
            return response["output"]
        except Exception as e:
            print(f"SQL Agent Error: {e}")
            return "I encountered an error querying the database."

if __name__ == "__main__":
    agent = SQLAgent()
    print(agent.query("How many orders are there?"))
