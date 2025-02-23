from openai import OpenAI

import os
from dotenv import load_dotenv
import json

load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Function to analyze text bias
def GPT_ana(text, bias_level):
    """
    Analyze the text and determine why it is biased.

    Parameters:
    text (str): The chunk of text to analyze.
    bias_level (dict): A dictionary with keys 'Left', 'Middle', 'Right' and values between 0 and 1.

    Returns:
    - dict: {"bias": "Left/Middle/Right", "explanation": "reasoning"}
    """
    prompt = f"""
    Analyze the following text and determine its political bias. Choose from:
    - Left
    - Middle
    - Right

    Explain your classification.

    Text: {text}

    Bias Levels (BERT Prediction):
    - Left: {bias_level['Left']}
    - Middle: {bias_level['Middle']}
    - Right: {bias_level['Right']}

    Respond in JSON format:
    {{
        "bias": "Left/Middle/Right",
        "explanation": "your explanation here"
    }}
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a political bias detection expert."},
                  {"role": "user", "content": prompt}],
        max_tokens=200
    )

    # Extract JSON response
    gpt_output = response.choices[0].message.content.strip()
    try:
        gpt_data = json.loads(gpt_output)
        return {"bias": gpt_data["bias"], "explanation": gpt_data["explanation"]}
    except json.JSONDecodeError:
        return {"bias": "Unknown", "explanation": "GPT response not in JSON format."}
