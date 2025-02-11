"""Configuration for the book generation system"""
from cgitb import small
from tabnanny import process_tokens
from openai import OpenAI

llm_client = OpenAI(base_url="http://192.168.1.5:1234/v1", api_key="lm-studio")
#llm_model = "patricide-12b-unslop-mell-v2" does not work well with the current system
#llm_model = "tifa-deepsex-14b-cot" write gaga rubbish
#llm_model = "darkest-muse-v1" context too small
llm_model = "dolphin-2.9.3-mistral-nemo-12b"

def get_llm_response(system_prompt: str, user_prompt: str):

    completion = llm_client.chat.completions.create(
        model=llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        timeout=6000)

    return completion.choices[0].message.content
