from libs.mistral_llm import MistralLLM
from llama_index.llms.openai import OpenAI
from llama_index.llms.ollama import Ollama
import os, requests
from dotenv import load_dotenv
load_dotenv()


class LlmFactory:
    _instances = {}
    llm = None
    name = None

    def __new__(cls, *args, **kwargs):
        model = args[0]
        if not model in cls._instances:
            cls._instances[model] = super(LlmFactory, cls).__new__(cls)
        return cls._instances[model]
    
    def __init__(self, name: str = None, default: str = None):
        if not self.name and not self.llm:
            self.name = name
            self.llm = self.get_llm(name, default)

    def get_llm(self, name: str, default: str = "ollama"):
        if name == "mistral":
            llm = MistralLLM(model=os.getenv("MISTRAL_MODEL"), api_key=os.getenv("MISTRAL_TOKEN"))
        elif name == "openai":
            llm = OpenAI(model=os.getenv("OPENAI_MODEL"), api_key=os.getenv("OPENAI_TOKEN"))
        elif name == "ollama":
            self.ollama_check_and_pull_model(os.getenv("OLLAMA_MODEL"), os.getenv("OLLAMA_BASE_URL"))
            llm = Ollama(model=os.getenv("OLLAMA_MODEL"), request_timeout=360.0, base_url=os.getenv("OLLAMA_BASE_URL"))
        else:
            llm = self.get_llm(default)
        return llm

    def ollama_check_and_pull_model(self, model_name: str, base_url: str):
        """
        Check if an Ollama model exists and pull it if not
        """
        print(f"@@ Checking if model {model_name} exists...")
        try:
            # Check if the model exists
            response = requests.get(f"{base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_exists = any(model.get("name") == model_name for model in models)
                
                if not model_exists:
                    print(f"@@ Model {model_name} not found, pulling it now...")
                    # Pull the model
                    pull_response = requests.post(
                        f"{base_url}/api/pull",
                        json={"name": model_name}
                    )
                    if pull_response.status_code == 200:
                        print(f"@@ Successfully pulled model {model_name}")
                    else:
                        print(f"@@ Failed to pull model {model_name}: {pull_response.text}")
                else:
                    print(f"@@ Model {model_name} already exists")
        except Exception as e:
            print(f"@@ Error checking/pulling model: {str(e)}")