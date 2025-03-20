from llama_index.core.tools import FunctionTool
from agents._agent import AbstractAgent

import os
from dotenv import load_dotenv
load_dotenv()


class SecretFactAgent(AbstractAgent):
    SERVICE_NAME = "secret_fact_agent"
    DESCRIPTION = "Useful for getting the secret fact."
    LLM_NAME = os.getenv("LLM_SECRET_FACT") or AbstractAgent.LLM_NAME

    def __init__(self):
        self.init_re_act_agent(
            [
                FunctionTool.from_defaults(fn=self.get_the_fact)
            ],
            self.get_llm(self.LLM_NAME)
        )
        
    def get_the_fact(self) -> str:
        return "The secret fact is: A baby llama is called a 'Cria'."