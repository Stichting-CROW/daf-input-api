import datetime
import mbike

class DepotDetails():
    @staticmethod
    def check_if_depot_exists(conn, depot_id):
        cur = conn.cursor()
        stmt = """
            SELECT depot_id
            FROM depot
            WHERE depot_id = %s
        """
        cur.execute(stmt, (depot_id,))
        conn.commit()
        
        return len(cur.fetchall()) > 0

    @staticmethod
    def create_depot(conn, data):
        cur = conn.cursor()
        stmt = """
            INSERT INTO depot
            (depot_id, municipality_code, name, street,
            postal_code, phone_number, city, email, instruction)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(stmt, (data.get("depot_id"), data.get("municipality_code"), data.get("name"),
            data.get("street"), data.get("postal_code"), data.get("phone_number"), data.get("email"),
                data.get("instruction"), data.get("city")))
        conn.commit()

    @staticmethod
    def check_or_create_depot(conn, data):
        if not DepotDetails.check_if_depot_exists(conn, data.get("depot_id")):
            DepotDetails.create_depot(conn, data)