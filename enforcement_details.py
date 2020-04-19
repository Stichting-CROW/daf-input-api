import datetime
import mbike

class EnforcementDetails():

    @staticmethod
    def create_enforcement_details(conn, data):
        cur = conn.cursor()
        timestamp = None
        stmt = """INSERT INTO enforcement
            (city, municipality_code, location, location_description, free_text_reason)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING enforcement_id
            """
        cur.execute(stmt, (data.get("city"), data.get("municipality_code"), None, data.get("location_description"), 
            data.get("free_text_reason")))
        conn.commit()
        return cur.fetchone()[0]
