from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class CampgroundSchema(BaseModel):
    id: str
    type: str
    link_self: Optional[str]
    name: str
    latitude: float
    longitude: float
    region_name: Optional[str]
    administrative_area: Optional[str]
    nearest_city_name: Optional[str]
    accommodation_type_names: List[str] = []
    bookable: Optional[bool]
    camper_types: List[str] = []
    operator: Optional[str]
    photo_url: Optional[str]
    photo_urls: List[str] = []
    photos_count: Optional[int]
    rating: Optional[float]
    reviews_count: Optional[int]
    slug: Optional[str]
    price_low: Optional[float]
    price_high: Optional[float]
    availability_updated_at: Optional[datetime]
    address: Optional[str] = None
    
  
    @classmethod
    def validate_availability_updated_at(cls, v):
        if v:
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return None
