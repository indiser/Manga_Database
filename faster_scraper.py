import os
import re
import json
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
import ctypes
import random

def prevent_sleep():
    if os.name == 'nt':
        try:
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
        except: pass

prevent_sleep()

script_dir = os.path.dirname(os.path.abspath(__file__))
filepath = os.path.join(script_dir, "manga_full_5.jsonl")
good_ids_filepath = os.path.join(script_dir, "good_id_2.txt")
bad_ids_filepath = os.path.join(script_dir, "bad_id_2.txt")

START_RANGE = 10000
END_RANGE = 1000000
MAX_CONCURRENT = 8
CHUNK_SIZE = 100
DELAY = 0.15
MAX_CONSECUTIVE_FAILURES = 10000

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "DNT": "1",
        "Connection": "keep-alive",
    }

def load_ids(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return {int(line.strip()) for line in f if line.strip().isdigit()}
    return set()

async def save_id(filepath, manga_id, lock):
    async with lock:
        with open(filepath, "a") as f:
            f.write(f"{manga_id}\n")

async def save_result(data, lock):
    async with lock:
        with open(filepath, "a", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
            f.write("\n")

async def scrape_manga(session, manga_id, good_ids, bad_ids, file_lock, semaphore, stats):
    if manga_id in good_ids or manga_id in bad_ids:
        return
    
    async with semaphore:
        url = f"https://nhentai.net/g/{manga_id}/"
        
        try:
            async with session.get(url, headers=get_headers()) as response:
                
                if response.status == 404:
                    await save_id(bad_ids_filepath, manga_id, file_lock)
                    bad_ids.add(manga_id)
                    stats['bad'] += 1
                    stats['consecutive_failures'] += 1
                    return
                
                if response.status == 429:
                    print(f"⚠️  Rate limited, backing off...")
                    await asyncio.sleep(random.uniform(10, 15))
                    return
                
                if response.status != 200:
                    stats['errors'] += 1
                    return
                
                html = await response.text()
                
                json_pattern = r"window\._gallery\s*=\s*JSON\.parse\(\"(.*?)\"\);"
                match = re.search(json_pattern, html)
                
                if not match:
                    stats['errors'] += 1
                    return
                
                clean_json_str = match.group(1).encode('utf-8').decode('unicode_escape')
                gallery_data = json.loads(clean_json_str)
                
                soup = BeautifulSoup(html, 'html.parser')
                
                recommendations = []
                related_container = soup.find('div', id='related-container')
                if related_container:
                    for gallery in related_container.find_all('div', class_='gallery'):
                        link_tag = gallery.find('a', class_='cover')
                        caption_tag = gallery.find('div', class_='caption')
                        if link_tag and caption_tag:
                            rec_id = link_tag['href'].strip('/').split('/')[-1]
                            rec_title = caption_tag.text
                            recommendations.append({'id': int(rec_id), 'title': rec_title})
                
                cover_url = None
                cover_div = soup.find('div', id='cover')
                if cover_div:
                    cover_img = cover_div.find('img')
                    if cover_img and 'data-src' in cover_img.attrs:
                        cover_url = "https:" + cover_img['data-src']
                
                data_payload = {
                    'id': int(gallery_data['id']),
                    'title': gallery_data['title']['english'],
                    'date': datetime.fromtimestamp(gallery_data['upload_date']).strftime('%Y-%m-%d'),
                    'parodies': [tag['name'] for tag in gallery_data['tags'] if tag['type'] == 'parody'],
                    'charecters': [tag['name'] for tag in gallery_data['tags'] if tag['type'] == 'character'],
                    'groups': [tag['name'] for tag in gallery_data['tags'] if tag['type'] == 'group'],
                    'categories': [tag['name'] for tag in gallery_data['tags'] if tag['type'] == 'category'],
                    'language': [tag['name'] for tag in gallery_data['tags'] if tag['type'] == 'language'],
                    'favorites': int(gallery_data['num_favorites']),
                    'tags': [tag['name'] for tag in gallery_data['tags'] if tag['type'] == 'tag'],
                    'artists': [tag['name'] for tag in gallery_data['tags'] if tag['type'] == 'artist'],
                    'num_pages': int(gallery_data['num_pages']),
                    'recommendations': recommendations,
                    'cover_image': cover_url
                }
                
                await save_result(data_payload, file_lock)
                await save_id(good_ids_filepath, manga_id, file_lock)
                good_ids.add(manga_id)
                stats['success'] += 1
                stats['consecutive_failures'] = 0
                
                print(f"✓ {manga_id}: {gallery_data['title']['english']}")
                
                await asyncio.sleep(DELAY)
                
        except asyncio.TimeoutError:
            stats['errors'] += 1
        except Exception as e:
            stats['errors'] += 1

async def process_chunk(session, chunk_ids, good_ids, bad_ids, file_lock, semaphore, stats):
    tasks = [scrape_manga(session, mid, good_ids, bad_ids, file_lock, semaphore, stats) for mid in chunk_ids]
    await asyncio.gather(*tasks, return_exceptions=True)

async def main():
    print("🚀 Async Scraper Starting...")
    
    good_ids = load_ids(good_ids_filepath)
    bad_ids = load_ids(bad_ids_filepath)
    
    print(f"📊 Loaded: {len(good_ids)} good, {len(bad_ids)} bad IDs")
    
    all_ids = [i for i in range(START_RANGE, END_RANGE + 1) if i not in good_ids and i not in bad_ids]
    
    print(f"📋 Processing {len(all_ids)} IDs in chunks of {CHUNK_SIZE}")
    
    file_lock = asyncio.Lock()
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    stats = {'success': 0, 'bad': 0, 'errors': 0, 'consecutive_failures': 0}
    
    connector = aiohttp.TCPConnector(limit=30, limit_per_host=15, ttl_dns_cache=300)
    timeout = aiohttp.ClientTimeout(total=20, connect=10)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        for i in range(0, len(all_ids), CHUNK_SIZE):
            chunk = all_ids[i:i + CHUNK_SIZE]
            chunk_num = i // CHUNK_SIZE + 1
            total_chunks = (len(all_ids) + CHUNK_SIZE - 1) // CHUNK_SIZE
            
            print(f"\n📦 Chunk {chunk_num}/{total_chunks} | Success: {stats['success']} | Bad: {stats['bad']} | Errors: {stats['errors']} | Consecutive Failures: {stats['consecutive_failures']}")
            
            await process_chunk(session, chunk, good_ids, bad_ids, file_lock, semaphore, stats)
            
            if stats['consecutive_failures'] >= MAX_CONSECUTIVE_FAILURES:
                print(f"\n🛑 Stopping: {MAX_CONSECUTIVE_FAILURES} consecutive failures reached. No more IDs likely exist.")
                break
            
            if i + CHUNK_SIZE < len(all_ids):
                await asyncio.sleep(random.uniform(1, 2))
    
    print(f"\n✅ Complete! Success: {stats['success']} | Bad: {stats['bad']} | Errors: {stats['errors']}")

if __name__ == "__main__":
    asyncio.run(main())
