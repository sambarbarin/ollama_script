import requests
import json
import sys

def list_available_models():
    """Get the list of available models from Ollama API"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            return [model['name'] for model in models]
        else:
            print(f"Error retrieving models: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error connecting to Ollama API: {e}")
        return []

def get_model_selection():
    """Prompt user to select a model with a question mark"""
    available_models = list_available_models()
    
    if not available_models:
        print("Could not retrieve models. Using default model 'llama3'.")
        return "llama3"
    
    print("Available models:")
    for i, model in enumerate(available_models, 1):
        print(f"{i}. {model}")
    
    while True:
        try:
            choice = input("? Which model would you like to use? (number or name): ")
            
            # Check if user entered a number
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(available_models):
                    return available_models[index]
                else:
                    print("Invalid selection. Please try again.")
            # Check if user entered a model name
            elif choice in available_models:
                return choice
            else:
                print("Model not found. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number or model name.")

def chat_with_ollama(model="llama3", stream=True):
    """
    Function to chat with Ollama API
    
    Args:
        model (str): The model to use for chat
        stream (bool): Whether to stream the response or not
    """
    print(f"Chat with {model} (Type 'exit' to quit)")
    print("-" * 50)

    # Keep track of conversation history
    messages = []
    
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        # Check if user wants to exit
        if user_input.lower() in ['exit', 'quit', 'q']:
            print("Goodbye!")
            break
        
        # Add user message to history
        messages.append({"role": "user", "content": user_input})
        
        # Prepare the request body
        request_data = {
            "model": model,
            "messages": messages,
            "stream": stream
        }
        
        # Make the API call
        try:
            if stream:
                # Streaming response handling
                print("\nOllama: ", end="", flush=True)
                response = requests.post(
                    "http://localhost:11434/api/chat",
                    json=request_data,
                    stream=True
                )
                
                assistant_response = ""
                for line in response.iter_lines():
                    if line:
                        json_data = json.loads(line)
                        if 'message' in json_data and 'content' in json_data['message']:
                            chunk = json_data['message']['content']
                            print(chunk, end="", flush=True)
                            assistant_response += chunk
                        if json_data.get('done', False):
                            break
                print()  # Add a newline after completed response
            else:
                # Non-streaming response handling
                response = requests.post(
                    "http://localhost:11434/api/chat",
                    json=request_data
                )
                
                response_data = response.json()
                assistant_response = response_data['message']['content']
                print(f"\nOllama: {assistant_response}")
            
            # Add assistant response to conversation history
            messages.append({"role": "assistant", "content": assistant_response})
            
        except requests.exceptions.RequestException as e:
            print(f"\nError connecting to Ollama API: {e}")
        except json.JSONDecodeError:
            print("\nError: Received invalid JSON from the API")
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    # Check if model is provided as argument
    if len(sys.argv) > 1:
        model_name = sys.argv[1]
    else:
        # Ask user to select a model
        model_name = get_model_selection()
    
    # Check if streaming preference is provided
    enable_streaming = True
    if len(sys.argv) > 2:
        enable_streaming = sys.argv[2].lower() in ['true', 't', '1', 'yes', 'y']
    
    chat_with_ollama(model=model_name, stream=enable_streaming)