"""
Main entrypoint for The Dyrt web scraper case study.

Usage:
    The scraper can be run directly (`python main.py`) or via Docker Compose (`docker compose up`).

If you have any questions in mind you can connect to me directly via info@smart-maple.com
"""

"""
İlk olarak, gerekli bağımlılıkları içeren veritabanı bağlantısı başlatılır (init_db() fonksiyonu ile). Ardından, kamp alanları verisini çekmek için scrape_campgrounds() fonksiyonu belirli aralıklarla çalıştırılacak şekilde zamanlanır. Zamanlama, schedule modülü kullanılarak her 15 dakikada bir bu işin yapılması sağlanır. Uygulama çalıştırıldığında, veritabanı bağlantısı kurulur ve scraper'ın işleyişine başlamak için bir iş başlatılır. Ayrıca, scraper sürekli olarak belirtilen zaman diliminde çalışmaya devam eder. 
"""
from models import Base
from scraper import scrape_campgrounds
from db import init_db
import schedule
import time
from api import app

def job(engine):
    scrape_campgrounds(engine)

if __name__ == "__main__":
    
    print("Hello Smart Maple!")

    engine = init_db()  

    job(engine)
    
    schedule.every(15).minutes.do(job, engine)

    while True:
        schedule.run_pending()
        time.sleep(1)
