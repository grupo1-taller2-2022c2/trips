from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import trips_routes, drivers_routes

app = FastAPI()

accept_all = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=accept_all,
    allow_credentials=True,
    allow_methods=accept_all,
    allow_headers=accept_all,
)


@app.get("/")
def read_root():
    return {"Welocme to": "Trips microservice"}


app.include_router(trips_routes.router, prefix="/trips", tags=["Trips"])
app.include_router(drivers_routes.router, prefix="/drivers", tags=["Drivers"])
