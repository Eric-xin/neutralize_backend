from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter
from pydantic import BaseModel
import io, os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from neutralize.GPT.work import GPT_ana
from neutralize.NLP.nlp_model import NLP_ana
from neutralize.GPT.multimo import reduce_bias, multicon_GPT_ana

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
        # Read the text input and analyze bias
        bias_level = NLP_ana(text)

        # Process the image if provided
        image_path = None
        if image:
            allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
            ext = os.path.splitext(image.filename)[-1].lower()
            if ext not in allowed_extensions:
                raise HTTPException(status_code=400, detail=f"Invalid image format: {ext}")

            image_bytes = await image.read()  # Read image as binary
            image_path = os.path.join(UPLOAD_DIR, image.filename)

            # Save the image
            with open(image_path, "wb") as f:
                f.write(image_bytes)

            if not os.path.exists(image_path):
                raise HTTPException(status_code=500, detail=f"Failed to save image: {image.filename}")

        # Select model based on bias level
        model = "gpt-3.5-turbo" if bias_level["Middle"] < 0.3 else "gpt-4"

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

@neu.post("/multicon_GPT_ana", dependencies=[Depends(get_current_user)])
async def multicon_GPT_ana_endpoint(request: TextRequest):
    try:
        text = request.text
        bias_level = NLP_ana(text)
        model = "gpt-3.5-turbo" if bias_level['Middle'] < 0.3 else "gpt-4"
        image_path = None
        
        neutral_text = multicon_GPT_ana(text, bias_level, image_path, model)
        return {"original_text": text, "bias_analysis": bias_level, "neutral_text": neutral_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Create API router for authentication endpoints
auth = APIRouter()

@auth.get("/users", response_model=list[UserResponse], dependencies=[Depends(get_current_user)])
async def retrieve_all_user():
    users = conn.execute(Users.select()).fetchall()
    return [dict(user._mapping) for user in users]

@auth.get("/user/{id}", response_model=UserResponse, dependencies=[Depends(get_current_user)])
async def retrieve_one_user(id: int):
    user = conn.execute(Users.select().where(Users.c.id == id)).fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(user._mapping)

@auth.patch("/user/{id}", response_model=list[UserResponse], dependencies=[Depends(get_current_user)])
async def update_user_data(id: int, req: User):
    conn.execute(Users.update().values(
        username=req.username,
        email=req.email,
    ).where(Users.c.id == id))
    users = conn.execute(Users.select()).fetchall()
    return [dict(user._mapping) for user in users]

@auth.delete("/user/{id}", response_model=list[UserResponse], dependencies=[Depends(get_current_user)])
async def delete_user_data(id: int):
    conn.execute(Users.delete().where(Users.c.id == id))
    users = conn.execute(Users.select()).fetchall()
    return [dict(user._mapping) for user in users]

@auth.post('/register', response_model=list[UserResponse])
def create_user(req: User):
    conn.execute(Users.insert().values(
        username=req.username,
        email=req.email,
        is_superuser=req.is_superuser,
        password=Hash.bcrypt(req.password)
    ))
    users = conn.execute(Users.select()).fetchall()
    return [dict(user._mapping) for user in users]

@auth.post('/login')
def login(req: OAuth2PasswordRequestForm = Depends()):
    user = conn.execute(Users.select().where(Users.c.username == req.username)).fetchone()
    if not user:
        raise HTTPException(status_code=404, detail=f"No user found with username: {req.username}")
    if not Hash.verify(user[-1], req.password):
        raise HTTPException(status_code=401, detail="Wrong username or password")
    access_token = create_access_token(data={"username": user[1], "email": user[2], "is_superuser": user[3]})
    return {"access_token": access_token, "token_type": "bearer", "id": user[0]}

@auth.get("/verify_token")
def read_root(current_user: User = Depends(get_current_user)):
    return current_user

@auth.patch("/change_superuser/{id}", response_model=list[UserResponse], dependencies=[Depends(get_current_user)])
def change_superuser(id: int, req: User):
    if req.is_superuser:
        conn.execute(Users.update().values(is_superuser=False).where(Users.c.id == id))
    else:
        conn.execute(Users.update().values(is_superuser=True).where(Users.c.id == id))
    users = conn.execute(Users.select()).fetchall()
    return [dict(user._mapping) for user in users]

# Finally, include the routers in your main FastAPI application instance
app = FastAPI()
app.include_router(neu, prefix="/api/neu")
app.include_router(auth, prefix="/api/auth")