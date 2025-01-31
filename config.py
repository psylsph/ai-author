"""Configuration for the book generation system"""
from typing import Dict
import autogen

def get_config(local_url: str = "http://192.168.1.5:1234/v1") -> Dict:

    """Get the configuration for the agents"""
    # Basic config for local LLM
    config_list = [{
        'model': 'mistral-nemo-instruct-2407',
        'base_url': local_url,
        'api_key': 'not-needed',
        'price': [0,0],
    }]

    # Common configuration for all agents
    agent_config = {
        "temperature": 0.3, # use 0.3 for mistral-nemo-instruct-2407
        "top_p": 0.95,
        "frequency_penalty": 0.3,
        "presence_penalty": 0.2,
        "config_list": config_list,
        "cache_seed": None
    }

    return agent_config

def get_user_proxy() -> autogen.UserProxyAgent:
        return autogen.UserProxyAgent(name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config={"work_dir": "story_output"}, )