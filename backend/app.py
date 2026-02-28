from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core import settings, app_logger
from middleware import LogMiddleware
from routes.attendance import attendance_router

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LogMiddleware)

app.include_router(attendance_router)


@app.get("/")
async def root():
    return {"message": "Facial Recognition Attendance API", "status": "running"}


if __name__ == "__main__":
    import uvicorn

    app_logger.info("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
