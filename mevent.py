import datetime
import mbike
import depot_details
import enforcement_details

class Event():
    def __init__(self, bike_id, event_type, extra_information, timestamp):
        self.event_id = None
        self.bike_id = bike_id
        self.event_type = event_type
        self.extra_information = extra_information
        self.timestamp = timestamp

    def save(self, conn):
        cur = conn.cursor()

        cur.execute("""INSERT INTO events
            (bike_id, event_type, extra_information, timestamp)
            VALUES (%s, %s, %s, %s) 
            RETURNING event_id""", (self.bike_id, self.event_type, self.extra_information, self.timestamp))
        conn.commit()
        self.event_id = cur.fetchone()[0]
        cur.close()
        return self

    @staticmethod
    def insert(conn, data):
        if data["event_type"] in ["check_in_depot", "check_out_depot"]:
            if not data.get("depot_details"):
                raise InvalidUsage("depot_details should be specified.", status_code=400)
            depot_details.DepotDetails.check_or_create_depot(conn, data.get("depot_details"))

        if data["event_type"] == "check_in_depot":
            if not data.get("enforcement_details"):
                raise InvalidUsage("enforcement_details should be specified on check_in.", status_code=400)
            enforcement_details.EnforcementDetails.create_enforcement_details(conn, data.get("enforcement_details"))

        bike = mbike.Bike.check_if_bike_exists_or_create(conn, data.get("bike"))

        timestamp = datetime.datetime.now()
        if "timestamp" in data:
            timestamp = datetime.datetime.strptime(data["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
        else:
            data["timestamp"] = datetime.datetime.strftime(timestamp, "%Y-%m-%dT%H:%M:%SZ")

        event = Event(bike.bike_id, data["event_type"], data["extra_information"], timestamp)
        event.save(conn)
        data["event_id"] = event.event_id
        return data


    def get_webhook_json(self, bike):
        data = {}
        data["event_id"] = self.event_id
        data["event_type"] = self.event_type
        data["extra_information"] = self.extra_information
        data["timestamp"] = self.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        data["bike"] = {}
        data["bike"]["bike_id"] = bike.bike_id
        data["bike"]["brand"] = bike.brand
        data["bike"]["frame_number"] = bike.frame_number
        return data

