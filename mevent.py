import datetime

import depot_details
import enforcement_details
import mbike
from exceptions import InvalidUsage
from models import EventIn


class Event:
    def __init__(self, bike_id, event_type, extra_information, timestamp, depot_id, enforcement_id):
        self.event_id = None
        self.bike_id = bike_id
        self.event_type = event_type
        self.extra_information = extra_information
        self.timestamp = timestamp
        self.depot_id = depot_id
        self.enforcement_id = enforcement_id

    def save(self, conn):
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO events
                (bike_id, event_type, extra_information, timestamp, depot_id, enforcement_details)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING event_id""", (self.bike_id, self.event_type, self.extra_information,
                    self.timestamp, self.depot_id, self.enforcement_id))
            self.event_id = cur.fetchone()[0]
        conn.commit()
        return self

    @staticmethod
    def insert(conn, data: EventIn):
        enforcement_id = None
        depot = data.depot_details

        if depot is None:
            raise InvalidUsage("depot_details should be specified.", status_code=400)
        depot_details.DepotDetails.check_or_create_depot(conn, depot)

        if data.event_type == "check_in_depot":
            if data.enforcement_details is None:
                raise InvalidUsage("enforcement_details should be specified on check_in.", status_code=400)
            enforcement_id = enforcement_details.EnforcementDetails.create_enforcement_details(
                conn, data.enforcement_details)

        bike = mbike.Bike.check_if_bike_exists_or_create(conn, data.bike)

        timestamp = datetime.datetime.now()
        if data.timestamp:
            timestamp = datetime.datetime.strptime(data.timestamp, "%Y-%m-%dT%H:%M:%SZ")

        event = Event(bike.bike_id, data.event_type, data.extra_information, timestamp,
            depot.depot_id, enforcement_id)
        event.save(conn)

        msg = data.model_dump()
        msg["timestamp"] = datetime.datetime.strftime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        msg["event_id"] = event.event_id
        return msg
