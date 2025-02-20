import os 
# Set up OpenAI variables 
# TODO: Set up open ai api key
OPENAI_API_KEY=
AI_MODEL='gpt-4o-mini'
MAX_TOKENS_ALLOWED=40000
# request per day = 200, per minute = 3
# TODO: check which rate limit to use
MAX_MESSAGES_TO_OPENAI=3
TOKEN_BUFFER=500

# TODO: Add db credentials