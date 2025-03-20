from llama_index.core.tools import FunctionTool
from agents._agent import AbstractAgent

import os
from dotenv import load_dotenv
load_dotenv()


class RandomFactAgent(AbstractAgent):
    SERVICE_NAME = "random_fact_agent"
    DESCRIPTION = "Useful for getting random facts."
    LLM_NAME = os.getenv("LLM_RANDOM_FACT") or AbstractAgent.LLM_NAME

    def __init__(self):
        self.init_re_act_agent(
            [
                FunctionTool.from_defaults(fn=self.get_the_fact)
            ],
            self.get_llm(self.LLM_NAME)
        )
    
    def get_the_fact(self) -> str:
        prompt = (
            "Génère un fait intéressant et surprenant en français. "
            "Le fait doit être court (une ou deux phrases maximum) et instructif. "
            "Réponds uniquement avec le fait, sans introduction ni conclusion."
        )
        response = self.get_llm(self.LLM_NAME).complete(prompt)
        return response.text
