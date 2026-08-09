from fastapi import FastAPI

from backend.api.upload import router as upload_router
from backend.api.pipeline import router as pipeline_router
from backend.api.experiment import router as experiment_router
from backend.api.health import router as health_router


app = FastAPI(
    title="AtlasML",
    description="Autonomous Machine Learning Research Scientist",
    version="1.0.0"
)



app.include_router(upload_router)
app.include_router(experiment_router)
app.include_router(pipeline_router)
app.include_router(health_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to AtlasML"
    }