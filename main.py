from fastapi import FastAPI

from database import engine
from models import Base
from routers import *

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}
