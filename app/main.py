import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routes import trips_routes, drivers_routes, notifications_routes
from starlette import status
from app.database import get_db
from sqlalchemy.orm import Session
from app.cruds import drivers_cruds, notifications_cruds, trips_cruds

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


@app.delete("/reset_db", status_code=status.HTTP_200_OK)
def reset_database(db: Session = Depends(get_db)):
    drivers_cruds.delete_added_drivers_info(db)
    notifications_cruds.delete_added_notifications_info(db)
    trips_cruds.delete_added_trips_info(db)
    return "Successfully reset"


app.include_router(trips_routes.router, prefix="/trips", tags=["Trips"])
app.include_router(drivers_routes.router, prefix="/drivers", tags=["Drivers"])
app.include_router(notifications_routes.router,
                   prefix="/notifications", tags=["Notifications"])
