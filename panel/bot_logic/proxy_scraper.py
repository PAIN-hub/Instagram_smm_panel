import requests
import time
from bs4 import BeautifulSoup
from django.utils import timezone
from panel.models import Proxy

def scrape_sslproxies(limit=50):
    """
    Scrapes fresh proxies from sslproxies.org and stores them in the Django database.
    """
    url = "https://www.sslproxies.org/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    proxies_created = 0
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Look for the primary proxy list textarea or table
        proxy_table = soup.find("table", id="proxylisttable")
        if not proxy_table:
            # Fallback to general tables
            proxy_table = soup.find("table")
            
        if proxy_table:
            tbody = proxy_table.find("tbody")
            rows = tbody.find_all("tr") if tbody else proxy_table.find_all("tr")[1:]
            
            for row in rows[:limit]:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    ip = cols[0].text.strip()
                    port_str = cols[1].text.strip()
                    try:
                        port = int(port_str)
                    except ValueError:
                        continue
                    
                    proto = "http"
                    if len(cols) >= 7:
                        proto = "https" if cols[6].text.strip().lower() == "yes" else "http"
                    
                    # Create or update in database
                    proxy_obj, created = Proxy.objects.get_or_create(
                        ip=ip,
                        port=port,
                        defaults={
                            'protocol': proto,
                            'is_active': True,
                            'last_checked': timezone.now()
                        }
                    )
                    if created:
                        proxies_created += 1
                        
        print(f"[SCRAPER] Successfully scraped and created {proxies_created} proxies.")
    except Exception as e:
        print(f"[SCRAPER] Error scraping sslproxies: {e}")
        
    return proxies_created

import concurrent.futures

def test_proxy(proxy, timeout=8):
    """
    Performs an Instagram-specific health check and handshake latency test on the proxy.
    Categorizes the proxy into:
      - 'clean': Active, fast response (< 2.5s), no rate-limiting or blocks
      - 'slow': Active, higher latency (>= 2.5s)
      - 'blocked': Instagram 429 Too Many Requests, 403 Forbidden, or challenge page
      - 'offline': Connection timeout, refused, SSL failure, or proxy down
    """
    auth_part = f"{proxy.username}:{proxy.password}@" if proxy.username and proxy.password else ""
    proxy_url = f"{proxy.protocol}://{auth_part}{proxy.ip}:{proxy.port}"
    
    proxies = {
        "http": proxy_url,
        "https": proxy_url
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    start_time = time.perf_counter()
    try:
        response = requests.get(
            "https://www.instagram.com",
            proxies=proxies,
            headers=headers,
            timeout=timeout,
            allow_redirects=True
        )
        latency = round(time.perf_counter() - start_time, 2)
        proxy.speed = latency
        proxy.last_checked = timezone.now()

        if response.status_code in [200, 301, 302]:
            body_sample = response.text[:2000].lower()
            if "checkpoint_required" in body_sample or "action blocked" in body_sample or "ip_blocked" in body_sample:
                proxy.is_active = False
                proxy.health_status = 'blocked'
                proxy.error_message = "Instagram IP Challenge/Block detected"
            elif latency < 2.5:
                proxy.is_active = True
                proxy.health_status = 'clean'
                proxy.error_message = None
            else:
                proxy.is_active = True
                proxy.health_status = 'slow'
                proxy.error_message = f"High latency ({latency}s)"
        elif response.status_code in [429, 403]:
            proxy.is_active = False
            proxy.health_status = 'blocked'
            proxy.error_message = f"Instagram HTTP {response.status_code} Blocked / Rate-Limited"
        else:
            proxy.is_active = False
            proxy.health_status = 'blocked'
            proxy.error_message = f"Instagram returned HTTP {response.status_code}"
    except requests.exceptions.ConnectTimeout:
        proxy.speed = None
        proxy.is_active = False
        proxy.health_status = 'offline'
        proxy.error_message = f"Connection timed out (>{timeout}s)"
    except requests.exceptions.ReadTimeout:
        proxy.speed = None
        proxy.is_active = False
        proxy.health_status = 'offline'
        proxy.error_message = f"Read timed out (>{timeout}s)"
    except requests.exceptions.ProxyError:
        proxy.speed = None
        proxy.is_active = False
        proxy.health_status = 'offline'
        proxy.error_message = "Proxy tunnel / connection failed"
    except Exception as e:
        proxy.speed = None
        proxy.is_active = False
        proxy.health_status = 'offline'
        proxy.error_message = str(e)[:150]

    proxy.last_checked = timezone.now()
    proxy.save()
    return proxy.is_active, proxy.health_status

def test_all_proxies_concurrently(proxy_ids=None, max_workers=5):
    """
    Tests multiple proxies in parallel using a thread pool with per-thread DB connection handling.
    """
    from django.db import connection
    
    if proxy_ids is None:
        try:
            proxy_ids = list(Proxy.objects.values_list('id', flat=True))
        finally:
            connection.close()
        
    if not proxy_ids:
        return 0

    def _worker(pid):
        from django.db import connection
        try:
            p = Proxy.objects.get(id=pid)
            test_proxy(p)
        except Exception as e:
            print(f"[PROXY_TEST] Error checking proxy {pid}: {e}")
        finally:
            connection.close()

    tested_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(_worker, pid) for pid in proxy_ids]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
                tested_count += 1
            except Exception:
                pass

    return tested_count

