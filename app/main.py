from fastapi import FastAPI
from app.routes import router as item_router

app = FastAPI(
    title="Recidron API",
    description="A FastAPI backend with MySQL database",
    version="1.0.0",
)

app.include_router(item_router)


@app.get("/")
def root():
    return {"message": "Welcome to Recidron API", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}