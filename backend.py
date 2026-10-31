import os
from typing import TypedDict
from dotenv import load_dotenv

from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END

load_dotenv()

# state of agent
class AgentState(TypedDict):
    question: str
    schema: str
    sql_query: str
    query_result: str
    final_answer: str
    error: str

class TextToSQLAgent:
    def __init__(self):
        self.db = self._connect_db()  

    def _connect_db(self):
        uri = (
            f"mysql+pymysql://{os.getenv('MYSQL_USER')}:"
            f"{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:"
            f"{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DATABASE')}"
        ) 
        return SQLDatabase.from_uri(uri)

    def get_table_names(self):
        return self.db.get_usable_table_names()

    def get_schema_info(self):
        return self.db.get_table_info()

    def _get_schema(self, state:AgentState):
        return{"schema":self.db.get_table_info()}