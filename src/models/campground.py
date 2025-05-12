from sqlalchemy import Column, String, Float, Boolean, Integer, DateTime, Text, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CampgroundDB(Base):
    __tablename__ = 'campgrounds'

    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    link_self = Column(String, nullable=False)  
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    region_name = Column(String, default="Unknown")


    administrative_area = Column(String)
    nearest_city_name = Column(String)
    accommodation_type_names = Column(ARRAY(String), default=[])
    bookable = Column(Boolean, default=False)
    camper_types = Column(ARRAY(String), default=[])
    operator = Column(String)
    photo_url = Column(String)
    photo_urls = Column(ARRAY(String), default=[])
    photos_count = Column(Integer, default=0)
    rating = Column(Float)
    reviews_count = Column(Integer, default=0)
    slug = Column(String)
    price_low = Column(Float)
    price_high = Column(Float)
    availability_updated_at = Column(DateTime)
    address = Column(String)
