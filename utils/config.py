import os 
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
AI_MODEL = os.getenv('AI_MODEL', 'gpt-4o-mini')
MAX_TOKENS_ALLOWED = int(os.getenv('MAX_TOKENS_ALLOWED', 40000))
MAX_MESSAGES_TO_OPENAI = int(os.getenv('MAX_MESSAGES_TO_OPENAI', 3))
TOKEN_BUFFER = int(os.getenv('TOKEN_BUFFER', 500))

# Database credentials
db_credentials = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': os.getenv('DB_PORT', '5432'),
    'default_db': os.getenv('DB_DEFAULT_NAME', 'postgres')
}
