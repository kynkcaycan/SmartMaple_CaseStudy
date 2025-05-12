"""
Bu dosya, API üzerinden tetiklenebilen arka plan scraping işlemi için FastAPI ve SQLAlchemy tabanlı bir temel sağlar. 
"""

"""
uvicorn api:app --reload komutunu terminalde çalıştırdıktan sonra api ye istek attığımda veritabanı bağlantısı kuruluyor. Ancak, scraping işlemi sırasında "utf-8' codec can't decode byte 0xf6 in position 68: invalid start byte" şeklinde bir hata alıyorum. Şu an bu hatanın nedenini tam olarak çözebilmiş değilim.

"""




from fastapi import FastAPI, BackgroundTasks
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import asyncio

app = FastAPI()

db_url = os.getenv("DB_URL", "postgresql://user:pswd@src-postgres-1:5432/postgres")
engine = create_engine(db_url, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@app.get("/")
def root():
    return {"message": "The Dyrt scraper API is running."}

async def scrape_campgrounds():
    try:
        print("Scraping işlemi başlatılıyor...")
        async with engine.connect() as connection:
            result = await connection.execute("SELECT 1")
            print(f"Veritabanı bağlantısı başarılı: {result.fetchone()}")
        await asyncio.sleep(5)
        print("Scraping işlemi tamamlandı.")
    except Exception as e:
        print(f"Scraping sırasında bir hata oluştu: {e}")

@app.post("/start-scraping/")
async def start_scraping(background_tasks: BackgroundTasks):
    background_tasks.add_task(scrape_campgrounds)
    return {"status": "Scraping started in background."}
