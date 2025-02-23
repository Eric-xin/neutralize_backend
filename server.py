from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from CRUD.authen import auth
import uvicorn
import colorama
# from neutralize.neutralize import neu
from neutralize.neutralize_not_enc import neu
from neutralize.neutralize import neu as neu_encrypted
# from database import cache
from db.url_cache import cache

colorama.init()
origins = [
    "http://localhost:3000",
    "http://localhost:8080",
]

app = FastAPI(docs_url="/api/docs", openapi_url="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth, prefix="/api")
app.include_router(neu, prefix="/api")
app.include_router(cache, prefix="/api")
app.include_router(neu_encrypted, prefix="/api/encrypted")

# if __name__ == "__main__": uvicorn.run("server:app", host="localhost", reload=True, port=9999)

if __name__ == "__main__": uvicorn.run("server:app", host="::", reload=True, port=8000)