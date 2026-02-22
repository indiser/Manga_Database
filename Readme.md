# 📚 Manga Metadata Scraper & Organizer

> *Because someone has to catalog the internet's vast library of... illustrated literature.*

## 🤔 What Even Is This?

Ever wondered how many pages of "art" exist on certain corners of the internet? Me neither. But here we are.

This is a collection of Python scripts that scrape, organize, and convert manga metadata from nhentai into various formats. Think of it as a digital librarian that works way too hard and asks zero questions.

## 🛠️ The Arsenal

### Scrapers (The Data Hunters)

- **`faster_scraper.py`** - The speed demon. Async scraping with 8 concurrent workers. Goes brrr. 🏎️
- **`scraper_for_linux.py`** - Same speed demon, but it took a shower and works on Linux too.
- **`mangascraper.py`** - The OG. Slower, but has PDF download capabilities. Retired but not forgotten.

### Data Wranglers

- **`jsonl_to_csv.py`** - Converts JSONL to CSV because Excel users exist.
- **`jsonl_to_db.py`** - Shoves everything into SQLite. Now with 100% more SQL!
- **`csv_to_parquet.py`** - Makes your data files smol and fast. Parquet gang rise up.

### Utility Belt

- **`clearner.py`** - Fixes those pesky string IDs that should've been integers. Oops.
- **`sorter.py`** - Sorts your ID lists. Revolutionary, I know.
- **`custom.py`** - A mysterious API caller. Does... something. Your guess is as good as mine.

## 🚀 Quick Start

### Scraping

```bash
# The fast way (Windows/Linux)
python faster_scraper.py

# The old-school way with range control
python mangascraper.py --start 1 --end 10000
```

### Converting Your Loot

```bash
# To CSV
python jsonl_to_csv.py

# To SQLite
python jsonl_to_db.py

# To Parquet (for the data nerds)
python csv_to_parquet.py
```

## 📦 What You'll Need

```bash
pip install aiohttp beautifulsoup4 requests pandas pyarrow sqlite3
```

*(Also img2pdf and Pillow if you're feeling nostalgic and want PDFs)*

## 🎯 Features That Slap

- **Async scraping** - Because waiting is for chumps
- **Auto-retry logic** - Handles rate limits like a champ
- **Duplicate prevention** - Tracks good/bad IDs so you don't waste time
- **UTF-8 support** - Japanese characters? No problem. Emojis? Sure, why not.
- **Multiple export formats** - CSV, SQLite, Parquet. Pick your poison.
- **Sleep prevention** - Your PC won't doze off mid-scrape (Windows only)

## 📊 Data Schema

Each entry includes:
- ID, Title, Upload Date
- Artists, Groups, Parodies, Characters
- Tags, Categories, Language
- Page count, Favorites
- Cover image URL
- Recommendations (because algorithms)

## 📈 The Dataset

The `manga_all.csv` file contains **594,346 entries** spanning IDs from 1 to 629,832. That's over half a million cataloged works with full metadata.

**Columns (14 total):**
- `id` - Unique identifier
- `title` - Full title (often includes event/circle info)
- `date` - Upload date (YYYY-MM-DD)
- `parodies`, `charecters`, `groups`, `categories`, `language`, `tags`, `artists` - JSON arrays of metadata
- `favorites` - Community popularity metric
- `num_pages` - Page count
- `recommendations` - Related works with IDs and titles
- `cover_image` - Direct URL to cover art

**Sample entry:**
```
ID: 1
Title: (C71) [Arisan-Antenna (Koari)] Eat The Rich! (Sukatto Golf Pangya)
Date: 2014-06-28
Pages: 14
Favorites: 3,029
```

All text fields support full UTF-8 (Japanese, Chinese, emojis, etc.) thanks to `ensure_ascii=False` in the export scripts.

## ⚠️ Legal Disclaimer

This is for educational purposes. Don't be weird. Respect rate limits. Don't DDoS anyone. Be cool.

## 🤷 FAQ

**Q: Why does this exist?**  
A: Data hoarding is a perfectly valid hobby.

**Q: Is this legal?**  
A: Scraping public data is generally fine. What you do with it is on you.

**Q: Can I use this for other sites?**  
A: Sure, but you'll need to rewrite like... everything.

**Q: Why are there so many scraper files?**  
A: Evolution, baby. Each one is slightly less terrible than the last.

## 🎓 Pro Tips

- Start small. Don't scrape 500k IDs on your first run.
- The site has rate limits. The scripts handle it, but don't be greedy.
- Use `faster_scraper.py` unless you need PDFs.
- SQLite is great for querying. CSV is great for sharing. Parquet is great for Pandas.

## 🐛 Known Issues

- Sometimes the site just... doesn't respond. That's life.
- PDF generation is slow and disabled by default.
- The code has comments like "Be polite" and "Don't let the user be stupid."

## 📝 License

MIT or whatever. Just don't sue me.

---

*Made with ☕ and questionable life choices.*
