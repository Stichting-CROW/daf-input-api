-- This entitiy respresents a registered bike in the register
-- In the initial version this table is automatically filled.
-- In the future owners of a bicycle may can register their bike in the register them selves. 
CREATE extension postgis;

CREATE TABLE bike (
	bike_id INT GENERATED ALWAYS AS IDENTITY,
    frame_number VARCHAR(255),
    chip_number VARCHAR(255),
    license_plate VARCHAR(255),
    brand VARCHAR(255),
    color VARCHAR(255),
    description VARCHAR(255),
	created_at timestamp NOT NULL DEFAULT NOW(),
    updated_at timestamp NOT NULL DEFAULT NOW(),
	PRIMARY KEY(bike_id)
);

CREATE TABLE depot (
    depot_id VARCHAR(255) NOT NULL,
    municipality_code VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    street VARCHAR(255),
    postal_code VARCHAR(255),
    phone_number VARCHAR(255),
    city VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    instruction TEXT,
    PRIMARY KEY(depot_id)
);

CREATE TABLE enforcement (
    enforcement_id INT GENERATED ALWAYS AS IDENTITY,
    city VARCHAR(255) NOT NULL,
    municipality_code VARCHAR(255) NOT NULL,
    location GEOMETRY,
    location_description TEXT,
    free_text_reason TEXT,
    timestamp timestamp,
    PRIMARY KEY(enforcement_id)
);

CREATE TABLE events (
    event_id INT GENERATED ALWAYS AS IDENTITY,
    event_type VARCHAR(50) NOT NULL,
    extra_information TEXT,
    timestamp timestamp NOT NULL DEFAULT NOW(),
	bike_id INT REFERENCES bike(bike_id),
	depot_id VARCHAR REFERENCES depot(depot_id),
    enforcement_details INT REFERENCES enforcement(enforcement_id),
    PRIMARY KEY(event_id)
);
