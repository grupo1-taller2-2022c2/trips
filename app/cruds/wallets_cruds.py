import requests
import os
import json
from starlette.exceptions import HTTPException

wallets_base_url = os.getenv("WALLETS_BASE_URL")
users_url_base = os.getenv("USERS_BASE_URL")


def can_pay_trip(user_email, trip_price):
    user_id = get_user_id_from_email(user_email)

    url = wallets_base_url + "/wallets/" + str(user_id)
    response = requests.get(url=url)
    if response.ok:
        current_balance = float(response.json()["balance"])
        print("Current balance is: " + str(current_balance))
        print("Trip price is: " + str(trip_price))
        print("So passenger can afford trip? " + str(current_balance >= trip_price))
        return current_balance >= trip_price * 1.05
    raise HTTPException(status_code=response.status_code, detail=response.json())


def make_payment(passenger_mail, driver_mail, trip_price):
    passenger_id = get_user_id_from_email(passenger_mail)
    driver_id = get_user_id_from_email(driver_mail)

    url = wallets_base_url + "/transfers"
    body = {
        "passenger_user_id": passenger_id,
        "driver_user_id": driver_id,
        "amount_in_ethers": format(trip_price, "f"),
    }
    response = requests.post(url=url, json=body)
    if response.ok:
        print("Payment made")
        return 0
    raise HTTPException(status_code=response.status_code, detail=response.json())


############## AUX ##############
def get_user_id_from_email(email):
    url = users_url_base + "/users/" + email + "/id"
    response = requests.get(url=url)
    if response.ok:
        print(response.text)
        return int(response.text)

    raise HTTPException(status_code=response.status_code, detail=response.json())
