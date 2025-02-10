"""Configuration for the book generation system"""
from tabnanny import process_tokens
from openai import OpenAI

llm_client = OpenAI(base_url="http://192.168.1.5:1234/v1", api_key="lm-studio")
#llm_model = "patricide-12b-unslop-mell-v2" does not work well with the current system
llm_model = "mistral-nemo-instruct-2407-14.7b-brainstorm-10x-form-3"

def get_llm_response(system_prompt: str, user_prompt: str):


    completion = llm_client.chat.completions.create(
        model=llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1,
        top_p=0.95,
        frequency_penalty=0.3,
        presence_penalty=0.2,
        timeout=6000)

    return completion.choices[0].message.content
