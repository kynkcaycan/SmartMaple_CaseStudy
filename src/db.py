
"""  
Öncelikle .env dosyasındaki ortam değişkenleri load_dotenv() ile yüklenir ve DB_URL adlı veritabanı bağlantı adresi alınır. 
Eğer bu bilgi bulunamazsa, hata fırlatılır. 
Daha sonra create_engine ile SQLAlchemy veritabanı motoru oluşturulur. 
Base.metadata.create_all(engine) komutu ile models.py dosyasında tanımlı olan tüm SQLAlchemy modellerine karşılık gelen tablolar veritabanında oluşturulur.
Son olarak, bağlantı motoru (engine) döndürülerek sistemin geri kalanında kullanılmaya hazır hale getirilir.

"""


from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from models import Base  

def init_db():
    load_dotenv(dotenv_path=".env")

    DATABASE_URL = os.getenv("DB_URL")
    if not DATABASE_URL:
        raise ValueError("DB_URL not found in environment variables")

    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    print("Database initialized.")
    print("DB_URL from .env:", repr(DATABASE_URL))

    return engine
