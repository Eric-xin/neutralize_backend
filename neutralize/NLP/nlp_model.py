from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from db.url_cache import get_db, website_cache
from sqlalchemy.orm import Session
from sqlalchemy import select, insert
from transformers import AdamW

# Initialize FastAPI app
app = FastAPI()

# Load PoliticalBiasBERT model
MODEL_NAME = "bucketresearch/politicalBiasBERT"
tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

# Define input structure
class TextRequest(BaseModel):
    url: str
    title: str
    text: str

# NLP function
def NLP_ana(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        logits = model(**inputs).logits
        probabilities = logits.softmax(dim=-1)[0].tolist()

    categories = ["Left", "Middle", "Right"]
    return {categories[i]: float(probabilities[i]) for i in range(len(categories))}  # Ensure float values

# Reinforcement Learning Function
def reinforce_learning(text, correct_label):
    """
    Fine-tune PoliticalBiasBERT model using GPT-4’s classification.

    Parameters:
    - text (str): The text used for reinforcement learning.
    - correct_label (str): The bias classification from GPT-4 ('Left', 'Middle', 'Right').
    """
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    labels = torch.tensor([[0, 0, 0]])  # One-hot encoding

    if correct_label == "Left":
        labels[0][0] = 1
    elif correct_label == "Middle":
        labels[0][1] = 1
    elif correct_label == "Right":
        labels[0][2] = 1

    model.train()
    optimizer = AdamW(model.parameters(), lr=5e-5)
    loss_fn = torch.nn.CrossEntropyLoss()

    outputs = model(**inputs)
    loss = loss_fn(outputs.logits, labels)

    loss.backward()
    optimizer.step()

    return {"message": "Model fine-tuned based on GPT feedback"}

# Define endpoint
@app.post("/analyze/")
async def analyze_bias(request: TextRequest, db: Session = Depends(get_db)):
    try:
        # Check if the URL is already in the cache
        existing_entry = db.execute(
            select(website_cache.c.left, website_cache.c.center, website_cache.c.right)
            .where(website_cache.c.url == request.url)
        ).fetchone()

        if existing_entry:
            return {
                "message": "Data retrieved from cache",
                "bias_analysis": {
                    "Left": existing_entry[0],
                    "Middle": existing_entry[1],
                    "Right": existing_entry[2]
                }
            }

        # If URL is not in cache, run NLP analysis
        bias_result = NLP_ana(request.text)

        # Compare results and reinforce learning if needed
        model_prediction = max(bias_result, key=bias_result.get)  # Get highest probability category
        gpt_correction = 0  # Default no correction

        if model_prediction != gpt_bias and gpt_bias in ["Left", "Middle", "Right"]:
            reinforce_learning(request.text, gpt_bias)  # Fine-tune model
            gpt_correction = 1  # Mark as corrected by GPT

        # Store results in database
        db.execute(
            insert(website_cache).values(
                url=request.url,
                title=request.title,
                text=request.text,
                left=bias_result["Left"],
                center=bias_result["Middle"],
                right=bias_result["Right"],
                gpt_bias=gpt_bias,
                gpt_explanation=gpt_explanation,
                gpt_correction=gpt_correction
            )
        )
        db.commit()

        return {"message": "NLP analysis performed", "bias_analysis": bias_result}

    except Exception as e:
        db.rollback()  # Rollback in case of an error
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()  # Ensure the database session is properly closed
