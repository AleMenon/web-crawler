import sqlite3
import time
import json
import zlib

class Cache:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS pages (
                url        TEXT PRIMARY KEY,
                status     INTEGER,
                html       BLOB,      -- zlib-compressed, NULL for non-HTML / non-200
                links      TEXT,      -- JSON list of absolute URLs found in the page
                fetched_at REAL
            )
            """
        )
        self.db.commit()
        self._dirty = 0

    def get_links(self, url, max_age_seconds):
        row = self.db.execute(
            "SELECT links, fetched_at FROM pages WHERE url = ?", (url,)
        ).fetchone()
        if row is None:
            return None
        links, fetched_at = row
        if time.time() - fetched_at > max_age_seconds:
            return None
        return json.loads(links)

    def put(self, url, status, html, links):
        blob = zlib.compress(html.encode("utf-8")) if html else None
        self.db.execute(
            "INSERT OR REPLACE INTO pages (url, status, html, links, fetched_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (url, status, blob, json.dumps(links), time.time()),
        )
        self._dirty += 1
        if self._dirty >= 20:
            self.commit()

    def commit(self):
        self.db.commit()
        self._dirty = 0

    def search(self, prefix, target):
        target = target.lower()
        cursor = self.db.execute(
            "SELECT url, html FROM pages "
            "WHERE html IS NOT NULL AND substr(url, 1, ?) = ? ORDER BY url",
            (len(prefix), prefix),
        )
        for url, blob in cursor:
            html = zlib.decompress(blob).decode("utf-8", errors="replace")
            if target in html.lower():
                yield url

    def count(self):
        return self.db.execute("SELECT COUNT(*) FROM pages").fetchone()[0]
