import google.generativeai as genai
import os

genai.configure(
    api_key=os.environ["GEMINI_API_KEY"]
)

model = genai.GenerativeModel("gemini-2.5-flash")

response = model.generate_content(
    "Translate to Persian: Stop at the next intersection."
)

print(response.text)