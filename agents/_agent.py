from abc import ABC, abstractmethod
from llama_agents import AgentService, SimpleMessageQueue
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from libs.llm_factory import LlmFactory
from llama_index.core import Settings

class AbstractAgent(ABC):
    agent: ReActAgent
    LLM_NAME = "openai"

    @property
    @abstractmethod
    def DESCRIPTION(self):
        pass

    @property
    @abstractmethod
    def SERVICE_NAME(self):
        pass

    @classmethod
    def get_agent_service(cls, host: str, port: int, message_queue: SimpleMessageQueue) -> AgentService:
        """
        Returns an AgentService object for the agent.
        
        Args:
            host (str): The host of the server.
            port (int): The port of the server.
            message_queue (SimpleMessageQueue): The message queue for the server.

        Returns:
            AgentService: The agent service object.
        """
        try:
            agent_service = AgentService(
                agent=cls().agent,
                message_queue=message_queue,
                description=cls.DESCRIPTION,
                service_name=cls.SERVICE_NAME,
                host=host,
                port=port,
            )
            return agent_service
        except Exception as e:
            raise ValueError(f"Error creating agent service: {e}")
    
    def get_llm(self, llm_name: str):
        """
        Returns the LLM object for the agent.

        Args:
            llm_name (str): The name of the LLM.

        Returns:
            Llm: The LLM object.
        """
        Settings.llm = LlmFactory(llm_name).llm
        return Settings.llm
    
    def init_re_act_agent(self, tools: list[FunctionTool], llm) -> ReActAgent:
        """
        Returns the ReActAgent object for the agent.

        Args:
            tools (list[FunctionTool]): The tools for the agent.
            llm: The LLM object for the agent.

        Returns:
            ReActAgent: The ReActAgent object.
        """
        self.agent = ReActAgent.from_tools(
            tools,
            llm=llm
        )
        return self.agent