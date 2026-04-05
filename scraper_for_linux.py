import os
import json
import asyncio
import aiohttp
import random


script_dir = os.path.dirname(os.path.abspath(__file__))
filepath = os.path.join(script_dir, "manga_full_10.jsonl")
good_ids_filepath = os.path.join(script_dir, "good_id_2.txt")
bad_ids_filepath = os.path.join(script_dir, "bad_id_2.txt")

START_RANGE = 600000
END_RANGE = 700000
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
                
                data=await response.json()
                recommendations=data.get("recommendations",[])

                data_payload={
                    "id" : data["id"],
                    "title" : data["title"],
                    "date" : data["date"],
                    "parodies" : data["parodies"] if data["parodies"] else [],
                    "charecters" : data["characters"] if data["characters"] else [],
                    "groups" : data["groups"] if data["groups"] else [],
                    "categories" : data["categories"] if data["categories"] else [],
                    "language" : data["language"] if data["language"] else [],
                    "favorites" : data["favorites"] if data["favorites"] else None,
                    "tags" : data["tags"] if data["tags"] else [],
                    "artists" : data["artists"] if data["artists"] else [],
                    "num_pages" : data["num_pages"] if data["num_pages"] else None,
                    "recommendations" : [{"id" : rec["id"], "title" : rec["title"]} for rec in recommendations],
                    "cover_image" : data["cover_image"]
                }
                
                await save_result(data_payload, file_lock)
                await save_id(good_ids_filepath, manga_id, file_lock)
                good_ids.add(manga_id)
                stats['success'] += 1
                stats['consecutive_failures'] = 0
                
                print(f"✓ {manga_id}: {data['title']}")
                
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
