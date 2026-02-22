import sqlite3
import json
import glob

DB_FILE = 'manga.db'
BATCH_SIZE = 5000

def get_jsonl_files():
    return sorted(glob.glob('*.jsonl'))

def create_schema(cursor):
    cursor.execute('''DROP TABLE IF EXISTS manga''')
    cursor.execute('''
        CREATE TABLE manga (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            date TEXT,
            favorites INTEGER DEFAULT 0,
            num_pages INTEGER,
            cover_image TEXT,
            parodies TEXT,
            charecters TEXT,
            groups TEXT,
            categories TEXT,
            language TEXT,
            tags TEXT,
            artists TEXT,
            recommendations TEXT
        )
    ''')
    cursor.execute('CREATE INDEX idx_title ON manga (title)')

def load_all_data():
    files = get_jsonl_files()
    data = []
    
    for filepath in files:
        print(f"Loading {filepath}...")
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get('id'):
                        data.append(entry)
                except json.JSONDecodeError:
                    continue
    
    data.sort(key=lambda x: x['id'])
    return data

def ingest_data():
    files = get_jsonl_files()
    if not files:
        print("No JSONL files found.")
        return
    
    print(f"Found {len(files)} file(s)")
    data = load_all_data()
    print(f"\nLoaded {len(data):,} records, sorted by id")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    create_schema(cursor)
    
    batch = []
    for entry in data:
        batch.append((
            entry['id'],
            entry.get('title', 'Unknown'),
            entry.get('date', ''),
            entry.get('favorites', 0),
            entry.get('num_pages', 0),
            entry.get('cover_image', ''),
            json.dumps(entry.get('parodies', []), ensure_ascii=False),
            json.dumps(entry.get('charecters', []), ensure_ascii=False),
            json.dumps(entry.get('groups', []), ensure_ascii=False),
            json.dumps(entry.get('categories', []), ensure_ascii=False),
            json.dumps(entry.get('language', []), ensure_ascii=False),
            json.dumps(entry.get('tags', []), ensure_ascii=False),
            json.dumps(entry.get('artists', []), ensure_ascii=False),
            json.dumps(entry.get('recommendations', []), ensure_ascii=False)
        ))
        
        if len(batch) >= BATCH_SIZE:
            cursor.executemany('INSERT INTO manga VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', batch)
            conn.commit()
            batch = []
    
    if batch:
        cursor.executemany('INSERT INTO manga VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', batch)
        conn.commit()
    
    conn.close()
    print(f"\n✓ Created {DB_FILE} with {len(data):,} records sorted by id")

if __name__ == "__main__":
    ingest_data()