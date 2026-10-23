#!/usr/bin/env python3
"""
Concurrent crawler with on-disk cache (SQLite).
"""

import argparse

from cache import Cache
from crawler import crawl
from fetcher import normalize

BASE_URL = "https://developers.mercadolivre.com.br/pt_br/"
TARGET_STRING = "/pictures/items/upload"
DB_PATH = "crawl_cache.db"

def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=lambda prog: argparse.RawDescriptionHelpFormatter(
            prog=prog,
            max_help_position=40
        )
    )

    default = "(default: %(default)s)"
    parser.add_argument("-u", "--url", default=BASE_URL, help=f"Target URL {default}")
    parser.add_argument("-s", "--search", default=TARGET_STRING, help=f"Target string {default}")
    parser.add_argument("--db", default=DB_PATH, help=f"SQLite cache {default}")
    parser.add_argument("--workers", type=int, default=8, help=f"Parallel requests {default}")
    parser.add_argument("--max-pages", type=int, default=500, help=f"Page limit {default}")
    parser.add_argument("--max-age-hours", type=int, default=24 * 7, help=f"Cache lifetime {default}")
    parser.add_argument("--refresh", action="store_true", help="Ignore the cache and re-download")
    parser.add_argument("--search-only", action="store_true", help="Skip crawling, search the cache only")
    args = parser.parse_args()

    args.url = normalize(args.url)

    cache = Cache(args.db)

    if not args.search_only:
        max_age = 0 if args.refresh else args.max_age_hours * 3600
        print(f"Crawl em: {args.url}  ({args.workers} workers, cache: {args.db})")
        print("-" * 50)
        crawl(args.url, cache, args.workers, args.max_pages, max_age)

    print(f"\nProcurando por '{args.search}' no cache ({cache.count()} páginas salvas)")
    found = 0
    for url in cache.search(args.url, args.search):
        found += 1
        print(f"\n - {url}")
    print(f"\nEncontrado em {found} página(s).")

if __name__ == "__main__":
    main()
