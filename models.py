from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, model_validator


class Location(BaseModel):
    model_config = ConfigDict(extra="allow")

    latitude: float
    longitude: float


class BikeIn(BaseModel):
    model_config = ConfigDict(extra="allow")

    brand: str
    frame_number: Optional[str] = None
    chip_number: Optional[str] = None
    license_plate: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None


class DepotDetails(BaseModel):
    model_config = ConfigDict(extra="allow")

    depot_id: str
    municipality_code: str
    city: str
    name: Optional[str] = None
    street: Optional[str] = None
    postal_code: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    instruction: Optional[str] = None


class EnforcementDetails(BaseModel):
    model_config = ConfigDict(extra="allow")

    city: str
    municipality_code: str
    location: Optional[Location] = None
    location_description: Optional[str] = None
    free_text_reason: Optional[str] = None
    timestamp: Optional[str] = None


class EventIn(BaseModel):
    model_config = ConfigDict(extra="allow")

    event_type: Literal["check_in_depot", "check_out_depot"]
    timestamp: str
    bike: BikeIn
    extra_information: Optional[str] = None
    depot_details: Optional[DepotDetails] = None
    enforcement_details: Optional[EnforcementDetails] = None

    @model_validator(mode="after")
    def check_event_requirements(self):
        if self.depot_details is None:
            raise ValueError("depot_details should be specified.")
        if self.event_type == "check_in_depot" and self.enforcement_details is None:
            raise ValueError("enforcement_details should be specified on check_in.")
        return self
