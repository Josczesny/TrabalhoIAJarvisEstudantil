import logging
from openai import OpenAI

MODEL = 'Qwen/Qwen2.5-14B-Instruct-AWQ'

client = OpenAI(
    base_url='https://llm.liaufms.org/v1/qwen2-5-14b-instruct-awq',
    api_key='REIkURcI7rTTqsTwlJi8MrgnKFwOiqky7Ezh7hH-l-k'
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler('jarvis_logs.log'), logging.StreamHandler()]
)
logger = logging.getLogger('JARVIS')
