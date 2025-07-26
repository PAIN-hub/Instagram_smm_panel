import requests
from bs4 import BeautifulSoup
import random
import os


def scrape_sslproxies(save_path="config/proxies.txt", limit=50):
    url = "https://www.sslproxies.org/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    proxy_table = soup.find("table", id="proxylisttable")
    
    proxies = []
    
    if proxy_table:
        for row in proxy_table.tbody.find_all("tr")[:limit]:
            cols = row.find_all("td")
            ip = cols[0].text.strip()
            port = cols[1].text.strip()
            proto = "https" if cols[6].text.strip().lower() == "yes" else "http"
            proxies.append(f"{proto}://{ip}:{port}")
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    with open(save_path, "w") as f:
        for proxy in proxies:
            f.write(proxy + "\n")
    
    print(f"[+] Saved {len(proxies)} proxies to {save_path}")


if __name__ == "__main__":
    scrape_sslproxies()
else:
    scrape_sslproxies()