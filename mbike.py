import logging

class Bike:
    def __init__(self, bike_id, frame_number, chip_number, 
            license_plate, brand, color, description):
        self.bike_id = bike_id
        self.frame_number = frame_number
        self.chip_number = chip_number
        self.license_plate = license_plate
        self.brand = brand
        self.color = color
        self.description = description 

    @staticmethod
    def row_to_object(records):
        if len(records) > 1:
            print("More than one bicycle with the %s + brand combination [%s, %s]!" % (type_lookup, identifier, brand))

        if len(records) > 0:
            data = records[0]
            return Bike(data[0], data[1], data[2], data[3], data[4], data[5], data[6])

    @staticmethod
    def look_up_frame_number(conn, frame_number, brand):
        if not frame_number or frame_number == "":
            return
        cur = conn.cursor()
        cur.execute("""
            SELECT bike_id, frame_number, chip_number, license_plate, brand, color, description
            FROM bike
            WHERE frame_number = %s
            AND brand = %s""", (frame_number, brand))
        return Bike.row_to_object(cur.fetchall())

    @staticmethod
    def look_up_chip_number(conn, chip_number, brand):
        if not chip_number or chip_number == "":
            return
        cur = conn.cursor()
        cur.execute("""
            SELECT bike_id, frame_number, chip_number, license_plate, brand, color, description
            FROM bike
            WHERE chip_number = %s
            AND brand = %s""", (chip_number, brand))
        return Bike.row_to_object(cur.fetchall())

    @staticmethod
    def look_up_license_plate(conn, license_plate, brand):
        if not license_plate or license_plate == "":
            return
        cur = conn.cursor()
        cur.execute("""
            SELECT bike_id, frame_number, chip_number, license_plate, brand, color, description
            FROM bike
            WHERE license_plate = %s
            AND brand = %s""", (license_plate, brand))
        return Bike.row_to_object(cur.fetchall())

    @staticmethod
    def try_create_bike_from_existing_data(conn, brand, frame_number, chip_number, license_plate):
        bike = Bike.look_up_frame_number(conn, frame_number, brand)
        if bike:
            return bike
        bike = Bike.look_up_chip_number(conn, chip_number, brand)
        if bike:
            return bike
        return Bike.look_up_license_plate(conn, license_plate, brand)

    @staticmethod
    def check_if_bike_exists_or_create(conn, data):
        cur = conn.cursor()

        frame_number = data.get("frame_number")
        chip_number = data.get("chip_number")
        license_plate = data.get("license_plate")
        brand = data.get("brand")
        if not brand or brand == "":
            raise InvalidUsage("No brand defined.", status_code=400)
        if (not frame_number or frame_number == "") and (not chip_number or chip_number == "") and (not license_plate or license_plate == ""):
            raise InvalidUsage("No frame_number, chip_number or license_plate defined.", status_code=400)
        bike = Bike.try_create_bike_from_existing_data(conn, brand, frame_number, chip_number, license_plate)

        if not bike:
            cur.execute("""INSERT INTO bike 
                (frame_number, chip_number, license_plate, brand, color, description, created_at, updated_at) 
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
                returning bike_id""", (frame_number, chip_number, license_plate, brand, data.get("color"), data.get("description")))
            bike_id = cur.fetchone()[0]
            bike = Bike(bike_id, frame_number, chip_number, license_plate, brand, data.get("color"), data.get("description"))

        conn.commit()
        cur.close()
        return bike

    @staticmethod
    def convert(data):
        result = Bike.check_if_bike_exists(data, conn)
        
    def __str__(self):
        return ("bike_id: " + str(self.bike_id) + "\n"
            + "brand: " + self.brand + "\n"
            + "frame_number: " + str(self.frame_number) + "\n")
            

