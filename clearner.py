import json

# Open the original file and create a new one for the fixed data
with open('manga_full.jsonl', 'r', encoding='utf-8') as infile, \
     open('manga_full.jsonl', 'w', encoding='utf-8') as outfile:
    
    for line in infile:
        # 1. Parse the JSON line into a dictionary
        data = json.loads(line)
        
        if 'id' in data:
            data['id']=int(data['id'])
        
        # 2. Loop through recommendations and convert 'id' to int
        if 'recommendations' in data:
            for rec in data['recommendations']:
                # The conversion happens here
                rec['id'] = int(rec['id'])
        
        # 3. Write the corrected line back to the new file
        outfile.write(json.dumps(data, ensure_ascii=False) + '\n')

print("Conversion complete. Check 'manga_fixed.jsonl'.")