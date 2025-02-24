from fastapi import HTTPException, Depends, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi import APIRouter

import io, os

from neutralize.NLP import reduce_bias, multicon_GPT_ana, GPT_ana
from neutralize.reinforced import NLP_ana

from schemas import BiasRequest, TextRequest, NeuReason, User, UserResponse
from service.jwttoken import create_access_token
from service.oauth import get_current_user
from service.hashing import Hash
from database import conn
from models import Users

# Create API router for neutral endpoints and enforce authorization
neu = APIRouter()

@neu.post("/gpt_analyze/", dependencies=[Depends(get_current_user)])
async def analyze_bias_endpoint(request: BiasRequest):
    try:
        explanation = GPT_ana(request.text, request.bias_level)
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@neu.post("/analyze/", dependencies=[Depends(get_current_user)])
async def analyze_bias(request: TextRequest):
    try:
        bias_result = NLP_ana(request.text)
        return {"bias_analysis": bias_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@neu.post("/analyze_mult/", dependencies=[Depends(get_current_user)])
async def analyze_bias_mult(request: TextRequest):
    try:
        # Analyze bias using NLP_ana
        bias_result = NLP_ana(request.text)

        # Analyze text bias using GPT
        explanation = GPT_ana(request.text, bias_result)
        return {"bias_analysis": bias_result, "explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Create directory if it doesn't exist

@neu.post("/reduce_bias", dependencies=[Depends(get_current_user)])
async def reduce_bias_endpoint(
    text: str = Form(...), image: UploadFile = File(None)
):
    try:
        # Analyze bias from the text
        bias_level = NLP_ana(text)

        image_path = None
        if image:
            allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
            ext = os.path.splitext(image.filename)[-1].lower()
            if ext not in allowed_extensions:
                raise HTTPException(status_code=400, detail=f"Invalid image format: {ext}")

            image_bytes = await image.read()  # Read image as binary
            image_path = os.path.join(UPLOAD_DIR, image.filename)

            # Save the image to disk
            with open(image_path, "wb") as f:
                f.write(image_bytes)

            if not os.path.exists(image_path):
                raise HTTPException(status_code=500, detail=f"Failed to save image: {image.filename}")

        # Choose model based on bias level
        model = "gpt-3.5-turbo" if bias_level["Middle"] < 0.3 else "gpt-4"

        try:
            # Process the image and text for bias reduction
            neutral_text, mulcont = reduce_bias(text, bias_level, image_path, model)
        except Exception as processing_error:
            raise HTTPException(status_code=500, detail=f"Error processing bias reduction: {str(processing_error)}")
        finally:
            # Delete the image file after processing (if it exists)
            if image_path and os.path.exists(image_path):
                os.remove(image_path)

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


@neu.post("/reduce_bias_txt", dependencies=[Depends(get_current_user)])
async def reduce_bias_only_txt_endpoint(request: TextRequest):
    try:
        text = request.text
        bias_level = NLP_ana(text)
        model = "gpt-3.5-turbo" if bias_level['Middle'] < 0.3 else "gpt-4"
        image_path = None
        
        neutral_text = reduce_bias(text, bias_level, image_path, model)
        return {"original_text": text, "bias_analysis": bias_level, "neutral_text": neutral_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@neu.post("/multicon_bias_ana", dependencies=[Depends(get_current_user)])
async def reduce_bias_endpoint(
    text: str = Form(...), image: UploadFile = File(None)
):
    try:
        # Analyze bias from the text
        bias_level = NLP_ana(text)

        image_path = None
        if image:
            allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
            ext = os.path.splitext(image.filename)[-1].lower()
            if ext not in allowed_extensions:
                raise HTTPException(status_code=400, detail=f"Invalid image format: {ext}")

            image_bytes = await image.read()  # Read image as binary
            image_path = os.path.join(UPLOAD_DIR, image.filename)

            # Save the image to disk
            with open(image_path, "wb") as f:
                f.write(image_bytes)

            if not os.path.exists(image_path):
                raise HTTPException(status_code=500, detail=f"Failed to save image: {image.filename}")

        # Choose model based on bias level
        model = "gpt-3.5-turbo" if bias_level["Middle"] < 0.3 else "gpt-4"

        try:
            # Process the image and text for bias reduction
            neutral_text, mulcont = multicon_GPT_ana(text, bias_level, image_path, model)
        except Exception as processing_error:
            raise HTTPException(status_code=500, detail=f"Error processing bias reduction: {str(processing_error)}")
        finally:
            # Delete the image file after processing (if it exists)
            if image_path and os.path.exists(image_path):
                os.remove(image_path)

        return JSONResponse(
            content={
                "original_text": text,
                "mulcont": mulcont,
                "bias_analysis": bias_level,
                "explanation": neutral_text,
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
