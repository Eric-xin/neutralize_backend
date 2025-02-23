from fastapi import FastAPI, HTTPException
from fastapi import APIRouter
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from neutralize.GPT.work import GPT_ana
from neutralize.NLP.nlp_model import NLP_ana
from neutralize.GPT.multimo import reduce_bias, multicon_GPT_ana

from schemas import BiasRequest, TextRequest, NeuReason

from fastapi import File, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import io, os

neu = APIRouter()

@neu.post("/gpt_analyze/")
async def analyze_bias_endpoint(request: BiasRequest):
    try:
        explanation = GPT_ana(request.text, request.bias_level)
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@neu.post("/analyze/")
async def analyze_bias(request: TextRequest):
    try:
        bias_result = NLP_ana(request.text)
        return {"bias_analysis": bias_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Integrated API
# NLP + GPT
# Endpoint: /analyze_mult/
@neu.post("/analyze_mult/")
async def analyze_bias(request: TextRequest):
    try:
        # Analyze bias using NLP_ana
        bias_result = NLP_ana(request.text)

        # Analyze text bias using GPT
        explanation = GPT_ana(request.text, bias_result)
        return {"bias_analysis": bias_result, "explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True) # Create dir

@neu.post("/reduce_bias")
async def reduce_bias_endpoint(
    text: str = Form(...), image: UploadFile = File(None)
):
    try:
        # Read the text input
        bias_level = NLP_ana(text)

        # Process the image if provided
        image_path = None
        if image:
            # Ensure the uploaded file has a valid image extension
            allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
            ext = os.path.splitext(image.filename)[-1].lower()
            if ext not in allowed_extensions:
                raise HTTPException(status_code=400, detail=f"Invalid image format: {ext}")

            image_bytes = await image.read()  # Read image as binary
            image_path = os.path.join(UPLOAD_DIR, image.filename)

            # Save the image
            with open(image_path, "wb") as f:
                f.write(image_bytes)

            # Ensure the file was saved properly
            if not os.path.exists(image_path):
                raise HTTPException(status_code=500, detail=f"Failed to save image: {image.filename}")

        # Select model based on bias level
        model = "gpt-3.5-turbo" if bias_level["Middle"] < 0.3 else "gpt-4-turbo"
        # model = "gpt-3.5-turbo"

        # Process the text using AI model
        try:
            neutral_text, mulcont = reduce_bias(text, bias_level, image_path, model)
        except Exception as processing_error:
            raise HTTPException(status_code=500, detail=f"Error processing bias reduction: {str(processing_error)}")

        return JSONResponse(
            content={
                "original_text": text,
                "mulcont": mulcont,
                "bias_analysis": bias_level,
                "neutral_text": neutral_text,
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@neu.post("/reduce_bias_txt")
async def reduce_bias_only_txt_endpoint(request: TextRequest):
    try:
        text = request.text
        bias_level = NLP_ana(text)
        
        # Select model based on bias level
        model = "gpt-3.5-turbo" if bias_level['Middle'] < 0.3 else "gpt-4"
        image_path = None
        
        neutral_text = reduce_bias(text, bias_level, image_path, model)
        return {"original_text": text, "bias_analysis": bias_level, "neutral_text": neutral_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@neu.post("/multicon_GPT_ana")
async def multicon_GPT_ana_endpoint(request: TextRequest):
    try:
        text = request.text
        bias_level = NLP_ana(text)
        
        # Select model based on bias level
        model = "gpt-3.5-turbo" if bias_level['Middle'] < 0.3 else "gpt-4"
        image_path = None
        
        neutral_text = multicon_GPT_ana(text, bias_level, image_path, model)
        return {"original_text": text, "bias_analysis": bias_level, "neutral_text": neutral_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))