from api import links, auth
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.database import create_db_and_tables

app = FastAPI()
app.add_middleware(CORSMiddleware, 
                   allow_origins=["*"],
                   allow_credentials=True, 
                   allow_methods=["*"], 
                   allow_headers=["*"]
                   )

app.include_router(links.router, tags=["links"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.on_event("startup")
async def startup_event():
    create_db_and_tables()

@app.get("/")
async def root():
    return {"message": "API-сервис сокращения ссылок"}