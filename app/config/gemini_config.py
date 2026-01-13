from google import genai

from app.config.app_config import getAppConfig

app_config = getAppConfig()
client = genai.Client(api_key=app_config.gemini_api_key)
