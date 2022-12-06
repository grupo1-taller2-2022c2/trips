from datetime import datetime
from app.schemas.trips_schemas import PriceChange


MONDAY = 0
TUESDAY = 1
WEDNESDAY = 2
THURSDAY = 3
FRIDAY = 4
SATURDAY = 5
SUNDAY = 6


class Pricing:
    def __init__(self):
        self.base = 0.0001
        self.distance = 0.0000001
        self.duration = 0.00001
        self.days_of_week = []
        self.busy_hours = []
        self.busy_hours_extra = 0.000001
        self.week_day_extra = 0.000001
        self.passenger_rating = 0.00001

    def calculate(self, distance, duration, passenger_rating):
        cost_sum = self.base + (self.distance * distance) + (self.duration * duration) - \
                   (self.passenger_rating * passenger_rating)
        dt = datetime.now()
        if dt.weekday() in self.days_of_week:
            cost_sum += self.week_day_extra
        if dt.hour in self.busy_hours:
            cost_sum += self.busy_hours_extra
        return cost_sum

    def change_pricing(self, price_change: PriceChange):
        if price_change.base:
            self.base = price_change.base
        if price_change.distance:
            self.distance = price_change.distance
        if price_change.duration:
            self.duration = price_change.duration
        if price_change.days_of_week:
            self.set_days_of_week(price_change.days_of_week)
        if price_change.busy_hours:
            self.busy_hours = price_change.busy_hours
        if price_change.busy_hours_extra:
            self.busy_hours_extra = price_change.busy_hours_extra
        if price_change.week_day_extra:
            self.week_day_extra = price_change.week_day_extra
        if price_change.passenger_rating:
            self.passenger_rating = price_change.passenger_rating

    def set_days_of_week(self, days_of_week):
        self.days_of_week = []
        for day in days_of_week:
            if day == "Monday":
                self.days_of_week.append(MONDAY)
            if day == "Tuesday":
                self.days_of_week.append(TUESDAY)
            if day == "Wednesday":
                self.days_of_week.append(WEDNESDAY)
            if day == "Thursday":
                self.days_of_week.append(THURSDAY)
            if day == "Friday":
                self.days_of_week.append(FRIDAY)
            if day == "Saturday":
                self.days_of_week.append(SATURDAY)
            if day == "Sunday":
                self.days_of_week.append(SUNDAY)

