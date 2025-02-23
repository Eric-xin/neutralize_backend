from fastapi import Depends
from service.oauth import get_current_user
from schemas import User, BiasRequest, TextRequest
from fastapi import HTTPException
from neutralize.GPT import GPT_ana
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import requests
from fastapi import APIRouter


CACHE_API_URL = "http://localhost:8000/api/cache"

neu = APIRouter()

@neu.post("/gpt_analyze/")
async def analyze_bias_endpoint(request: BiasRequest, current_user: User = Depends(get_current_user)):
    try:
        explanation = GPT_ana(request.text, request.bias_level)
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@neu.post("/analyze/")
async def analyze_bias(request: TextRequest, db: Session = Depends(get_db)):
    try:
        # NLP Analysis
        bias_result = NLP_ana(request.text)
        gpt_bias = "Middle"  # Placeholder value
        gpt_explanation = "Automated explanation"  # Placeholder value
        gpt_correction = 0  # Default correction status

        # Debugging: Print Bias Result
        print("[DEBUG] Bias Result:", bias_result)

        # Prepare Insert Query
        stmt = insert(website_cache).values(
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

        # Debugging: Print SQL Query
        print("[DEBUG] Executing SQL:", stmt)

        # Execute Query
        db.execute(stmt)
        db.commit()
        print("[DEBUG] Data committed successfully")

        return {"message": "NLP analysis performed", "bias_analysis": bias_result}

    except Exception as e:
        db.rollback()
        print("[ERROR] Database error:", e)
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()

@neu.post("/analyze_mult/")
async def analyze_bias(request: TextRequest, current_user: User = Depends(get_current_user)):
    try:
        # Analyze bias using PoliticalBiasBERT
        inputs = tokenizer(request.text, return_tensors="pt")
        with torch.no_grad():
            logits = model(**inputs).logits
            probabilities = logits.softmax(dim=-1)[0].tolist()
        categories = ["Left", "Middle", "Right"]
        bias_result = {categories[i]: probabilities[i] for i in range(len(categories))}

        # Analyze text bias using GPT
        explanation = GPT_ana(request.text, bias_result)
        return {"bias_analysis": bias_result, "explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
