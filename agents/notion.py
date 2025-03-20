from llama_index.core.tools import FunctionTool
from llama_index.core import SummaryIndex
from llama_index.readers.notion import NotionPageReader
from agents._agent import AbstractAgent

import os
from dotenv import load_dotenv
load_dotenv()


class NotionAgent(AbstractAgent):
    SERVICE_NAME = "notion_agent"
    DESCRIPTION = "Useful for reading Notion pages and answering questions."
    LLM_NAME = os.getenv("LLM_NOTION") or AbstractAgent.LLM_NAME
    NOTION_TOKEN = os.getenv("NOTION_TOKEN")

    def __init__(self):
        if not self.NOTION_TOKEN:
            raise ValueError("NOTION_TOKEN is not set in the environment variables.")

        self.init_re_act_agent(
            [
                FunctionTool.from_defaults(fn=self.read),
                FunctionTool.from_defaults(fn=self.search)
            ], 
            self.get_llm(self.LLM_NAME)
        )
    
    def read(self, pages_id: list[str] = [], databases_id: list[str] = []) -> list[dict]:
        """
        Reads data from Notion pages and databases.

        Args:
            pages_id (list[str]): List of Notion page IDs.
            databases_id (list[str]): List of Notion database IDs.

        Returns:
            list: A list of documents retrieved from Notion.
        """
        documents = NotionPageReader(integration_token=self.NOTION_TOKEN).load_data(
            pages_id,
            databases_id
        )
        return documents

    async def search(self, documents, query: str) -> str:
        """
        Search a query in a list of documents and return the response.

        Args:
            documents: List of documents to search in.
            query: Query to search for.

        Returns:
            The response to the query as an asynchronous string.
        """
        index = SummaryIndex.from_documents(documents)
        query_engine = index.as_query_engine()
        response = await query_engine.search(query)
        return response

