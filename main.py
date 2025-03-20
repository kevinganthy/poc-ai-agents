import logging
from llama_agents import AgentOrchestrator, ControlPlaneServer, SimpleMessageQueue, ServerLauncher, CallableMessageConsumer
from agents.secret_fact import SecretFactAgent
from agents.random_fact import RandomFactAgent
from agents.query_pgsql import QueryPgsqlAgent
from agents.notion import NotionAgent
from agents.web_scraper import WebScraperAgent
from libs.llm_factory import LlmFactory

import os
from dotenv import load_dotenv
load_dotenv()

HOST=os.getenv("HOST")
PORT=int(os.getenv("PORT"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='💡 %(levelname)s @ %(asctime)s : %(name)s\n%(message)s'
)
logger = logging.getLogger(__name__)


# Choose LLM for orchestrator
llm = LlmFactory(os.getenv("LLM_MAIN"), "ollama").llm

# Init servers
message_queue = SimpleMessageQueue(port=PORT)
control_plane = ControlPlaneServer(
    message_queue=message_queue,
    host=HOST,
    orchestrator=AgentOrchestrator(llm=llm),
    port=PORT+1,
)

# Init agents
secret_fact_server = SecretFactAgent.get_agent_service(HOST, PORT+2, message_queue)
random_fact_server = RandomFactAgent.get_agent_service(HOST, PORT+3, message_queue)
query_sql_server = QueryPgsqlAgent.get_agent_service(HOST, PORT+4, message_queue)
notion_server = NotionAgent.get_agent_service(HOST, PORT+5, message_queue)
web_scraper_server = WebScraperAgent.get_agent_service(HOST, PORT+6, message_queue)


def handle_result(message) -> None:
    logger.info(f"Got result: {message.data}")

human_consumer = CallableMessageConsumer(handler=handle_result, message_type="human")
launcher = ServerLauncher(
    [secret_fact_server, random_fact_server, query_sql_server, notion_server, web_scraper_server],
    control_plane,
    message_queue,
    additional_consumers=[human_consumer]
)

if __name__ == "__main__":
    logger.info("Starting servers...")
    launcher.launch_servers()