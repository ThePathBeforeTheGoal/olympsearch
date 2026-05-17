import os
import time
import requests
import threading

def ping_self():
    """Каждые 4 минуты пингует /health, чтобы Render не засыпал"""
    # Получаем URL приложения из переменной окружения Render
    # Render автоматически задаёт RENDER_EXTERNAL_URL (если нет — используем localhost)
    base_url = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:10000")
    health_url = f"{base_url}/health"
    
    while True:
        try:
            response = requests.get(health_url, timeout=10)
            print(f"[KeepAlive] PING {health_url} → {response.status_code}")
        except Exception as e:
            print(f"[KeepAlive] ERROR: {e}")
        time.sleep(240)  # 4 минуты (240 секунд)

# Запускаем в отдельном потоке при старте
def start_keep_alive():
    thread = threading.Thread(target=ping_self, daemon=True)
    thread.start()