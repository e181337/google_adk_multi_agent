from typing import Protocol, Optional

class LlmClient(Protocol):
    def generate(self,
                user_prompt: str,
                system_prompt: Optional[str] = None,
                temperature: Optional[float] = None,
                max_output_tokens: Optional[int] = None) -> str:
        ...

class StaticLlmClient:
    def __init__(self, fixed_response: str, model_name: str):
        self.fixed_response = fixed_response
        self.model_name = model_name
    
    def generate(self,
                user_prompt: str,
                system_prompt: Optional[str] = None,
                temperature: Optional[float] = None,
                max_output_tokens: Optional[int] = None) -> str:
        return self.fixed_response
    
class GeminiRequestBuilder:
    @staticmethod
    def build(
            model: str,
            user_prompt: str,
            system_prompt: Optional[str] = None,
            temperature: Optional[float] = None,
            max_output_tokens: Optional[int] = None 
    ) -> dict:
        payload = {}
        payload["model"]= model
        
        if system_prompt is not None:
            if system_prompt.strip() != "":
                payload["system_instruction"] = system_prompt
        
        payload["contents"] = [{"role":"user",
                                "parts":[{"text": user_prompt}]}]

        generation_config = {}
        if temperature is not None:
            generation_config["temperature"] = temperature
        if max_output_tokens is not None:
            generation_config["max_output_tokens"] = max_output_tokens
        if generation_config:
            payload["generation_config"] = generation_config

        return payload
        
class GoogleAdkLlmClient:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def _validate_user_prompt(self, user_prompt: str) -> None:
        if not user_prompt or user_prompt.strip() == "":
            raise ValueError("User prompt cannot be empty")
    
    def _validate_system_prompt(self, system_prompt: Optional[str] = None) -> Optional[str]:
        if  system_prompt is not None and not system_prompt.strip():
            system_prompt = None
        return system_prompt
    
    def _validate_temperature(self, temperature: Optional[float] = None) -> None:
        if temperature is not None:
            if not isinstance(temperature, (int, float)):
                raise ValueError("temperature should be number")
            if temperature < 0 : 
                raise ValueError("temperature should be positive")
    
    def _validate_max_output_tokens(self, max_output_tokens: Optional[int] = None) -> None:
        if max_output_tokens is not None:
            if not isinstance(max_output_tokens, int) :
                raise ValueError("max_output_tokens should be int")
            if max_output_tokens <= 0 :
                raise ValueError("max_output_tokens should be int")
            
        
    def generate(self,
                user_prompt: str,
                system_prompt: Optional[str] = None,
                temperature: Optional[float] = None,
                max_output_tokens: Optional[int] = None) -> str:

        self._validate_user_prompt(user_prompt)
        system_prompt = self._validate_system_prompt(system_prompt)
        self._validate_temperature(temperature)
        self._validate_max_output_tokens(max_output_tokens)

        payload  = GeminiRequestBuilder.build(self.model_name,
                                              user_prompt, 
                                              system_prompt,
                                              temperature,
                                              max_output_tokens)
                    
        return f"Model: {self.model_name} | System: {system_prompt} | User: {user_prompt}"
        

        