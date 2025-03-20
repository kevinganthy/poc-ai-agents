from sqlalchemy import create_engine, URL
from llama_index.core import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from agents._agent import AbstractAgent

import os
from dotenv import load_dotenv
load_dotenv()


class QueryPgsqlAgent(AbstractAgent):
    SERVICE_NAME = "query_pgsql_agent"
    DESCRIPTION = "Useful for querying a PostgreSQL database containing users data with natural language."
    LLM_NAME = os.getenv("LLM_QUERY_PGSQL") or AbstractAgent.LLM_NAME
    DB_METADATA = """
        The database contains a table named 'users' with classic fields and birthdate, sex (M/F), and country (state) columns.
    """
    
    def __init__(self):
        llm = self.get_llm(self.LLM_NAME)
        self.init_re_act_agent(
            [
                self.get_query_tool(llm)
            ], 
            llm
        )

    def get_query_tool(self, llm) -> QueryEngineTool:
        # Create database URL object
        db_url = URL.create(
            drivername="postgresql",
            username=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT'),
            database=os.getenv('POSTGRES_DB')
        )
        
        # Create engine and database connection
        engine = create_engine(db_url)
        self.db_conn = SQLDatabase(engine)
        
        # Create and return the query tool in one step
        return QueryEngineTool.from_defaults(
            query_engine=NLSQLTableQueryEngine(
                sql_database=self.db_conn,
                embed_model=llm,
            ),
            name="query_pgsql_tool",
            description=self.DB_METADATA
        )