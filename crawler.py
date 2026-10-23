from collections import deque
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED

from cache import Cache
from fetcher import make_session, fetch, normalize

SKIP_EXTENSIONS = (
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico",
    ".pdf", ".zip", ".gz", ".tar", ".css", ".js", ".json", ".xml",
    ".mp4", ".woff", ".woff2", ".ttf",
)

def crawl(start_url: str, cache: Cache, workers: int, max_pages: int, max_age_seconds: int):
    session = make_session(workers)
    seen = {start_url}
    frontier = deque([start_url])
    pending = set()
    dispatched = cache_hits = downloaded = errors = 0

    def in_scope(link):
        return link == start_url or link.startswith(start_url + "/")

    def enqueue(links):
        for link in links:
            link = normalize(link)
            if (
                in_scope(link)
                and link not in seen
                and not link.lower().endswith(SKIP_EXTENSIONS)
            ):
                seen.add(link)
                frontier.append(link)

    pool = ThreadPoolExecutor(max_workers=workers)
    try:
        while frontier or pending:
            while frontier and dispatched < max_pages and len(pending) < workers * 2:
                url = frontier.popleft()
                dispatched += 1

                links = cache.get_links(url, max_age_seconds)
                if links is not None:
                    cache_hits += 1
                    enqueue(links)
                else:
                    pending.add(pool.submit(fetch, session, url))

            if not pending:
                break

            done, pending = wait(pending, return_when=FIRST_COMPLETED)
            for future in done:
                url, status, html, links, error = future.result()
                if error:
                    errors += 1
                    print(f"! Erro em {url}: {error}")
                    continue
                downloaded += 1
                cache.put(url, status, html, links)
                enqueue(links)
                print(f"[{cache_hits + downloaded + errors}/{max_pages}] baixado ({status}): {url}")
    except KeyboardInterrupt:
        print("\nInterrompido - o progresso já está salvo no cache.")
    finally:
        pool.shutdown(wait=False, cancel_futures=True)
        cache.commit()

    print("-" * 50)
    print(f"Páginas processadas: {dispatched}")
    print(f"- Do cache: {cache_hits} | Baixadas: {downloaded} | Erros: {errors}")
    if frontier:
        print(f"- Ainda na fila (limite de --max-pages): {len(frontier)}")
