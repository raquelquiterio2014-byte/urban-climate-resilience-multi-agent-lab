"""Optional Gemini interpretation; never changes deterministic calculations."""
import os

def interpret(workflow):
    from dotenv import load_dotenv
    load_dotenv()
    key = os.getenv('GEMINI_API_KEY')
    if not key:
        raise ValueError('GEMINI_API_KEY is missing. Set it in your local .env file.')
    from google import genai
    client = genai.Client(api_key=key)
    a = workflow['agents']
    prompt = (f"Interpret this SYNTHETIC educational climate-risk screening for district {workflow['district']}. "
              f"Risk index {a['Risk Agent']['risk_index']} ({a['Risk Agent']['risk_level']}). "
              f"Options: {a['Planning Agent']['options']}. "
              "Provide a concise explanation, key limitations, and human verification steps. "
              "Do not claim measured risk, calibrated reductions, official recommendations, or real-world impacts. "
              "Do not change any calculated values.")
    result = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
    return result.text or 'No response text returned.'