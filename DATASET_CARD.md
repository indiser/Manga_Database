# NSFW Manga Metadata Dataset

## Dataset Summary
Comprehensive metadata for 111,849 manga entries from nhentai, covering IDs 1-629832.

**Date Range:** June 28, 2014 - February 14, 2026

## Dataset Structure

### Fields
- `id` (int): Unique manga identifier
- `title` (str): Full manga title
- `date` (str): Upload date (YYYY-MM-DD)
- `favorites` (int): Number of favorites
- `num_pages` (int): Page count
- `cover_image` (str): Cover image URL
- `parodies` (list): Source material parodies
- `charecters` (list): Character names
- `groups` (list): Creator groups
- `categories` (list): Content categories
- `language` (list): Available languages
- `tags` (list): Content tags
- `artists` (list): Artist names
- `recommendations` (list): Related manga recommendations (id, title)

## Data Format
- **JSONL**: 9 files (manga_full_1.jsonl, manga_full_2.jsonl, manga_full_3.jsonl, manga_full_4.jsonl, manga_full_5.jsonl, manga_full_6.jsonl, manga_full_7.jsonl, manga_full_8.jsonl, manga_full_9.jsonl)
- **Parquet**: Single file (manga_all.parquet)
- **CSV**: Single file (manga_all.csv)
- **SQLite**: Single database (manga.db) with indexed id and title

## Usage
```python
import pandas as pd

# Load parquet
df = pd.read_parquet('manga_all.parquet')

# Load JSONL
df = pd.read_json('manga_full_1.jsonl', lines=True)

# Load CSV
df = pd.read_csv('manga_all.csv')
```

## Future Aspects

I plan to update the datset every year or so.
