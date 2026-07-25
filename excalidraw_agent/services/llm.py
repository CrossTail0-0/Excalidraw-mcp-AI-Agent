from groq import Groq


class LLMService:


    def __init__(
        self,
        api_key: str,
        model="openai/gpt-oss-120b"
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

        response = self.client.chat.completions.create(

            model=self.model,

            messages=messages,

            temperature=temperature,

            max_completion_tokens=4096
        )


        return response.choices[0].message.content