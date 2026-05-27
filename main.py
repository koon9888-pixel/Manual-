
from fastapi import FastAPI
from app.routes import diagnostics

app = FastAPI(title="1VD-FTV Intelligent Diagnostic API")

app.include_router(diagnostics.router)

@app.get("/")
async def root():
    return {"status": "running", "engine": "1VD-FTV"}
