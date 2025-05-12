"""Bu Python scripti, coğrafi verileri kullanarak ABD'deki kamp alanlarını scrape etmek için tasarlanmış. İlk olarak gerekli kütüphaneler (requests, geopy, SQLAlchemy, vb.) içe aktarılıyor ve loglama yapılandırması yapılmakta. Script, `geopy`'nin `Nominatim` sınıfını kullanarak, kamp alanlarının enlem ve boylam bilgilerini alır ve bu koordinatlara karşılık gelen adresi `get_address` fonksiyonu ile sorgular. Eğer adres bulunamazsa, hata loglanır. Kamp alanları, The Dyrt API'sine yapılan isteklerle alınır. API'ye her seferinde belirli sınırlar (ABD'nin coğrafi sınırları) ve sayfa numarasına göre sorgular yapılır. Veriler, API'den JSON formatında alınır ve her kamp alanı için gerekli özellikler doğrulandıktan sonra, veritabanına eklenir. Bu ekleme işlemi sırasında, kamp alanı adresi de alınarak veritabanına kaydedilir. Veritabanı işlemleri SQLAlchemy session kullanılarak yapılır ve her sayfa tamamlandığında bir sonraki sayfaya geçilir. Hatalar ve API istek hataları loglanır. Bu süreç, tüm kamp alanları çekilene kadar devam eder.
 """

from geopy.geocoders import Nominatim
from sqlalchemy.orm import Session
from models import CampgroundDB
from schemas.campground import CampgroundSchema
import requests
import logging
import time


logging.basicConfig(
    filename='scraper.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


geolocator = Nominatim(user_agent="campground_scraper")

def get_address(lat, lon):
    try:
        location = geolocator.reverse((lat, lon), language="en", exactly_one=True)
        if location:
            return location.address
        else:
            return None
    except Exception as e:
        logging.warning(f"Adres bulunamadı: {lat}, {lon} - Hata: {e}")
        return None

def scrape_campgrounds(engine):
    URL = "https://thedyrt.com/api/v6/location-search-results"
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    USA_BOUNDS = {
        "west": -125.0,
        "south": 24.0,
        "east": -66.9,
        "north": 49.0
    }

    bbox = [USA_BOUNDS["west"], USA_BOUNDS["south"], USA_BOUNDS["east"], USA_BOUNDS["north"]]
    page = 1

    with Session(engine) as session:
        while True:
            params = {
                "filter[search][bbox]": ",".join(map(str, bbox)),
                "page[size]": 50,
                "page[number]": page
            }

            try:
                logging.info(f"Requesting page {page}")
                response = requests.get(URL, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()

                if not data.get("data"):
                    logging.info(" Tüm veriler çekildi.")
                    break

                for item in data["data"]:
                    attr = item.get("attributes", {})
                    lat = attr.get("latitude")
                    lon = attr.get("longitude")

                    if lat is None or lon is None:
                        logging.warning(f"Konum bilgisi eksik: {item['id']}")
                        continue

            
                    if not (USA_BOUNDS["south"] <= lat <= USA_BOUNDS["north"] and
                            USA_BOUNDS["west"] <= lon <= USA_BOUNDS["east"]):
                        logging.warning(f"ABD dışı kamp atlandı: {item['id']} - lat: {lat}, lon: {lon}")
                        continue

                    address = get_address(lat, lon)

                    try:
                        validated = CampgroundSchema(
                            id=item["id"],
                            type=item["type"],
                            link_self=item.get("links", {}).get("self"),
                            name=attr.get("name"),
                            latitude=lat,
                            longitude=lon,
                            region_name=attr.get("region_name"),
                            administrative_area=attr.get("administrative_area"),
                            nearest_city_name=attr.get("nearest_city_name"),
                            accommodation_type_names=attr.get("accommodation_type_names", []),
                            bookable=attr.get("bookable"),
                            camper_types=attr.get("camper_types", []),
                            operator=attr.get("operator"),
                            photo_url=attr.get("photo_url"),
                            photo_urls=attr.get("photo_urls", []),
                            photos_count=attr.get("photos_count"),
                            rating=attr.get("rating"),
                            reviews_count=attr.get("reviews_count"),
                            slug=attr.get("slug"),
                            price_low=attr.get("price_low"),
                            price_high=attr.get("price_high"),
                            availability_updated_at=attr.get("availability_updated_at")
                        )

                       
                        camp = CampgroundDB(
                            **validated.dict(exclude_unset=True, exclude={"availability_updated_at", "address"})
                        )
                        camp.availability_updated_at = validated.availability_updated_at
                        camp.address = address  

                        session.merge(camp)

                    except Exception as e:
                        logging.warning(f"Doğrulama hatası: {e}")
                        continue

                session.commit()
                logging.info(f"Page {page} tamamlandı.")
                page += 1
                time.sleep(1)

            except requests.exceptions.RequestException as e:
                logging.critical(f"İstek hatası: {e}")
                break
