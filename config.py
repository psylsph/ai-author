"""Configuration for the book generation system"""
from openai import OpenAI

#llm_client = OpenAI(base_url="http://192.168.1.5:1234/v1", api_key="lm-studio")
llm_client = OpenAI(base_url="https://api.deepseek.com/v1", api_key="sk-a93151ad736d46c1aef86014f2ab045a")
#llm_client = OpenAI(base_url="http://127.0.0.1:11434/v1", api_key="ollama")
#llm_model = "patricide-12b-unslop-mell-v2" does not work well with the current system
#llm_model = "tifa-deepsex-14b-cot" write gaga rubbish
#llm_model = "darkest-muse-v1" context too small
#llm_model = "dolphin-2.9.3-mistral-nemo-12b" good speed
#llm_model = "qwen2.5-14b-instruct-1m" keeps repeating itself
#llm_model = "llama-3.2-3b-instruct" no explicit
#llm_model = "llama3.1-darkstorm-aspire-8b" works well with the current system
#llm_model = "mistral-7b-instruct-v0.3" # no system prompt
#llm_model = "mistral-nemo-instruct-2407-14.7b-brainstorm-10x-form-3" # wanders off
#llm_model = "peach-9b-8k-roleplay" # has no idea what it is talking about, can't even do all the character names
#llm_model = "darksapling-v1.1-ultra-quality-7b"# doesn't complete and wanders off
#llm_model = "Mistral-Nemo-Instruct-2407-GGUF:latest"
#llm_model = "deepseek-r1-distill-llama-8b" gets lost
#llm_model = "deepseek-r1-distill-qwen-7b" # seems ok, need to check how good the story is
#llm_model = "hamanasu-15b-instruct" # fails
#llm_model = "allura-org_bigger-body-8b" #goes in circles
#llm_model = "nousresearch_deephermes-3-llama-3-8b-preview" # goes in circles @ 0.3
#llm_model = "openthinker-7b" # goes off topic in chapter 3
#llm_model = "darkest-muse-v1" # seems pretty good
# OmnicromsBrain/Eros_Scribe-7b
# temperature=0.7, top_k=50, top_p=0.95
#llm_model = "mistral-small-instruct-2409"
#llm_model = "archaeo-12b"
llm_model = "deepseek-chat"

def get_llm_response(system_prompt: str, user_prompt: str):

    completion = llm_client.chat.completions.create(
        model=llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=1.3,
        max_completion_tokens=8192,
        timeout=6000,
        stream=False)
    
    response = completion.choices[0].message.content.replace("*", "").replace("#", "").replace("\n\n", "\n")
    response = response.replace("&", "").replace("\\", "").replace("{", "").replace("}", "")
    response = response.replace("\\hline", "").replace("\\boxed", "").replace("\\textbf", "").replace("\\begin", "")
    
    if "</think>" in response:
            response = response.split("</think>")[1]

    return response
