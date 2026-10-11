from models import DepotDetails as DepotDetailsModel


class DepotDetails:
    @staticmethod
    def check_if_depot_exists(conn, depot_id):
        with conn.cursor() as cur:
            cur.execute("""
                SELECT depot_id
                FROM depot
                WHERE depot_id = %s
            """, (depot_id,))
            return len(cur.fetchall()) > 0

    @staticmethod
    def create_depot(conn, data: DepotDetailsModel):
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO depot
                (depot_id, municipality_code, name, street,
                postal_code, phone_number, city, email, instruction)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (data.depot_id, data.municipality_code, data.name,
                data.street, data.postal_code, data.phone_number, data.city,
                data.email, data.instruction))
        conn.commit()

    @staticmethod
    def check_or_create_depot(conn, data: DepotDetailsModel):
        if not DepotDetails.check_if_depot_exists(conn, data.depot_id):
            DepotDetails.create_depot(conn, data)
