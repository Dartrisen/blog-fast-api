from fastapi import FastAPI

from database import engine
from models import Base
from routers import auth, users, posts

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
