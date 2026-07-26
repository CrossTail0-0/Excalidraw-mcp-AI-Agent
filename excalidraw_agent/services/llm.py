from groq import Groq


class LLMService:


    def __init__(
        self,
        api_key: str,
        model="llama-3.1-8b-instant" #"openai/gpt-oss-120b"
    ):

        self.client = Groq(
            api_key=api_key
        )

        self.model = model



    def chat(
        self,
        messages,
        temperature=0
    ):
        

        try: 
            response = self.client.chat.completions.create(

                model=self.model,

                messages=messages,

                temperature=temperature,

                max_completion_tokens=4096
            )
            return response.choices[0].message.content
        except Exception as e:
            # llm answers instead with the error
            raise ValueError(e)