import csv
import json
import glob

def jsonl_to_csv():
    files = sorted(glob.glob('*.jsonl'))
    if not files:
        print("No JSONL files found.")
        return
    
    print(f"Loading {len(files)} file(s)...")
    data = []
    
    for filepath in files:
        print(f"  Reading {filepath}...")
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    
    data.sort(key=lambda x: x.get('id', 0))
    
    output = 'manga_all.csv'
    print(f"\nWriting {len(data):,} records to {output}...")
    
    with open(output, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(data[0].keys()))
        writer.writeheader()
        for obj in data:
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v 
                           for k, v in obj.items()})
    
    print(f"✓ Created {output} sorted by id")

if __name__ == "__main__":
    jsonl_to_csv()
