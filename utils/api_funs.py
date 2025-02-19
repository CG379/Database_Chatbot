import json
import requests 
from tenacity import retry, wait_random_exponential, stop_after_attempt

# Exponential backoff
@retry(wait=wait_random_exponential(min=1, max=50), stop=stop_after_attempt(3))
# TODO: get model and key and other stuff
def send_api_request(messages, functions=None, function_call=None, model=AI_MODEL, api_key=OPENAI_KEY):
    """
    Send a request to the OpenAI API
    """
    try:
        # Prepare request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        data = {
            "model": model,
            "messages": messages
        }

        if functions:
            data.update("functions": functions)
        if function_call:
            data.update("function_call": function_call)
        response = requests.post("https://api.openai.com/v1/engines/davinci-codex/completions", headers=headers, data=json.dumps(data))
        response.raise_for_status()

        return response
    
    except Exception as e:
        print(e)

def execute_fun(message):
    if message["function_call"]["name"] == "ask_db":
        query = json.loads(message["function_call"]["args"][query]) 
        print(f"SQL: {query}")
        # TODO: Add db connection function
        results = ask_db(query)
        print(f"Results: {results}")
    else:
        results = f"Function {message['function_call']['name']} not found"    
    return results