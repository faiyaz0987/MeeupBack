from fastapi import FastAPI
from routes import admin_routes, host_routes, auth_routes

app = FastAPI(title="MeetUp Backend API")

app.include_router(admin_routes.router, prefix="/admin", tags=["Admin"])
app.include_router(host_routes.router, prefix="/host", tags=["Host/Participant"])
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])

@app.get("/")
def root():
    return {"message": "MeetUp API is running"}
