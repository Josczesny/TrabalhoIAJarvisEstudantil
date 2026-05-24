import logging
from openai import OpenAI

MODEL = 'google/gemma-3-12b-it'

client = OpenAI(
    base_url='https://llm.liaufms.org/v1/gemma-3-12b-it',
    api_key='Cxt2ftLF7d3mHS2JdiFqB-eSDAQeZvFATPXPs02lV9A'
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler('jarvis_logs.log'), logging.StreamHandler()]
)
logger = logging.getLogger('JARVIS')
