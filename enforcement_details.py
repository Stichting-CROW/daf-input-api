from models import EnforcementDetails as EnforcementDetailsModel


class EnforcementDetails:
    @staticmethod
    def create_enforcement_details(conn, data: EnforcementDetailsModel):
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO enforcement
                (city, municipality_code, location, location_description, free_text_reason)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING enforcement_id
                """, (data.city, data.municipality_code, None, data.location_description,
                    data.free_text_reason))
            enforcement_id = cur.fetchone()[0]
        conn.commit()
        return enforcement_id
