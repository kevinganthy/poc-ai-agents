import time
from llama_agents import LlamaAgentsClient

client = LlamaAgentsClient("http://0.0.0.0:8001")

def poll_result(query: str, timeout: int = 120):
    print(query)
    task_id = client.create_task(query)
    start_time = time.time()

    while True:
        try:
            result = client.get_task_result(task_id=task_id)
            return result
        except Exception as e:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Timeout exceeded: {timeout} seconds")
            time.sleep(1)
            

# result = poll_result("Parcours la base de donnée Notion 9eaa1ac2410842878444ed9ad33a8ef8 et synthétise ce qui est dit sur le SEO.")
# result = poll_result("Lis la page Notion c608190a740e4ac9bf677b029473377d et extrait les bonnes pratiques pour un logo.")
# result = poll_result("Quel es le pourcentage homme femme de mes clients ?")
# result = poll_result("Quel est le secret ?")
# result = poll_result("Donne moi un fait amusant.")
result = poll_result("d'après le site https://gnth.fr, quel est le prix pour une landing page ?")

print("=>", result.result)