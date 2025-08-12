import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
API = os.getenv("AI_API_KEY")
#print(API)

client = genai.Client(api_key=API)

user_input = input("Ask any question you have ")

response = client.models.generate_content(
    model="gemini-2.5-flash", contents=user_input
)
print(response.text)