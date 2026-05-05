import requests
import json
from typing import List, Dict, Optional, Generator

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
    
    def list_available_models(self) -> List[str]:
        """Get the list of available models from Ollama API"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'] for model in models]
            else:
                return []
        except Exception as e:
            print(f"Error connecting to Ollama API: {e}")
            return []
    
    def chat_stream(self, model: str, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """
        Stream chat response from Ollama API
        
        Args:
            model (str): The model to use for chat
            messages (List[Dict]): List of message objects with role and content
            
        Yields:
            str: Individual chunks of the response
        """
        request_data = {
            "model": model,
            "messages": messages,
            "stream": True
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=request_data,
                stream=True
            )
            
            if response.status_code != 200:
                yield f"Error: API returned status code {response.status_code}"
                return
            
            for line in response.iter_lines():
                if line:
                    try:
                        json_data = json.loads(line)
                        if 'message' in json_data and 'content' in json_data['message']:
                            chunk = json_data['message']['content']
                            if chunk:  # Only yield non-empty chunks
                                yield chunk
                        if json_data.get('done', False):
                            break
                    except json.JSONDecodeError:
                        continue
                        
        except requests.exceptions.RequestException as e:
            yield f"Error: Connection failed - {str(e)}"
        except Exception as e:
            yield f"Error: {str(e)}"
    
    def chat_complete(self, model: str, messages: List[Dict[str, str]]) -> Optional[str]:
        """
        Get complete chat response from Ollama API (non-streaming)
        
        Args:
            model (str): The model to use for chat
            messages (List[Dict]): List of message objects with role and content
            
        Returns:
            str: Complete response or None if error
        """
        request_data = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=request_data
            )
            
            if response.status_code == 200:
                response_data = response.json()
                return response_data['message']['content']
            else:
                return f"Error: API returned status code {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            return f"Error: Connection failed - {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def is_available(self) -> bool:
        """Check if Ollama API is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False