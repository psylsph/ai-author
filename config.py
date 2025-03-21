"""Configuration for the book generation system"""
import time
from openai import OpenAI

llm_client = OpenAI(base_url="http://192.168.1.5:1234/v1", api_key="lm-studio")
#llm_client = OpenAI(base_url="https://api.deepseek.com/v1", api_key="")
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
#llm_model = "nbeerbower_-_mistral-nemo-gutenberg-12b-v2" # 0.3
#llm_model = "deepseek-r1-distill-llama-8b" gets lost
#llm_model = "deepseek-r1-distill-qwen-7b" # seems ok, need to check how good the story is
#llm_model = "hamanasu-15b-instruct" # fails
#llm_model = "allura-org_bigger-body-8b" #goes in circles
#llm_model = "nousresearch_deephermes-3-llama-3-8b-preview" # goes in circles @ 0.3
#llm_model = "openthinker-7b" # goes off topic in chapter 3
#llm_model = "darkest-muse-v1" # seems pretty good 1.0, min_p 0.1
# OmnicromsBrain/Eros_Scribe-7b
# temperature=0.7, top_k=50, top_p=0.95
#llm_model = "phi-4" #0.7
#llm_model = "deepseek-reasoner" # 0.7 or docs says 1.5
#llm_model = "gemma-2-ataraxy-v4d-9b" # temp 1, min_p 0.1,
#llm_model = "phi-4-deepseek-r1k-rl-ezo-i1" # 1.0
#llm_model = "qwq-32b" # 0.7
#llm_model = "gemma-3-12b-it" # temperature = 1.0, top_k = 64, top_p = 0.95, min_p = 0.0


#llm_model = "lmstudio-community/mistral-nemo-instruct-2407" # temperature = 0.3
#llm_model = "mistral-nemo-gutenberg3-12b" # temperature = 0.3
#llm_model = "quill-v1" # temperature = 1.0
#llm_model = "delta-vector/archaeo-12b" # temperature = 0.2
#llm_model = "eros_scribe-7b" # temperature = 1.0
llm_model = "llama-3some-8b-v2" # temperature = 0.7

def get_llm_response(system_prompt: str, user_prompt: str):

    response = llm_client.chat.completions.create(
        model=llm_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        top_p=0.95,
        #max_tokens=8192,
        max_completion_tokens=5000,
        timeout=6000,
        stream=True
    )
    
    # create variables to collect the stream of chunks
    collected_messages = []
    # iterate through the stream of events
    for chunk in response:
        chunk_message = chunk.choices[0].delta.content  # extract the message
        collected_messages.append(chunk_message)  # save the message
        print(chunk_message, sep=' ', end='', flush=True)  # print the text
    print()
    # clean None in collected_messages
    collected_messages = [m for m in collected_messages if m is not None]
    full_reply_content = ''.join(collected_messages)
    #full_reply_content = response.choices[0].message.content
    
    cleaned_response = full_reply_content.replace("*", "").replace("#", "").replace("\n\n", "\n")
    cleaned_response = cleaned_response.replace("&", "").replace("\\", "").replace("{", "").replace("}", "")
    cleaned_response = cleaned_response.replace("\\hline", "").replace("\\boxed", "").replace("\\textbf", "").replace("\\begin", "")
    
    if "</think>" in cleaned_response:
            cleaned_response = cleaned_response.split("</think>")[1]

    return cleaned_response
