# Web Crawler

Crawler em Python que percorre documentação web e procura por string em HTML das páginas, listando as URLs onde a mesma foi encontrada.

Foi pensado para responder perguntas como *"em quais páginas da documentação aparece `/pictures/items/upload`?"* sem precisar abrir página por página.

## Características

- **Downloads em paralelo:** thread pool com `requests.Session`.
- **Cache em disco (SQLite):** cada página baixada é salva (HTML comprimido + links). Rodar de novo não baixa as mesmas páginas.
- **Retomada automática:** Proteção contra Ctrl-C, o progresso já está salvo e a próxima execução continua de onde parou.
- **Busca offline:** com o cache montado, é possível procurar outras strings sem acessar a rede.
- **Retry com backoff:** tenta novamente em erros de conexão.
- **URLs normalizadas:** remove query string, fragmento e barra final, evitando baixar a mesma página várias vezes.
- **Escopo restrito:** só segue links que estejam dentro da URL inicial, e ignora arquivos que não são páginas.

## Requisitos

- [uv](https://docs.astral.sh/uv/) (recomendado) ou ambiente configurado com dependências presentes no `pyproject.toml`

## Uso

Para ver todas as opções:

```bash
uv sync
uv run web_crawler.py --help
```

Exemplos:

```bash
# Crawl (usando o cache) + busca pela string padrão
uv run web_crawler.py

# Crawl + busca por outra string
uv run web_crawler.py -s "/items/search"

# Busca sem acessar a rede
uv run web_crawler.py --search-only -s "/pictures"

# Ignora o cache e baixa tudo novamente
uv run web_crawler.py --refresh

# Cobrir mais páginas, com mais workers
uv run web_crawler.py --max-pages 3000 --workers 16

# Explorar outro site, com um cache separado
uv run web_crawler.py -u https://exemplo.com/docs/ -s "texto" --db exemplo.db
```

Ao final, o script lista as URLs onde a string foi encontrada

## Argumentos

| Argumento | Padrão | Descrição |
|---|---|---|
| `-u`, `--url` | URL da documentação | URL inicial. O crawl fica restrito a ela, e a busca também filtra por ela |
| `-s`, `--search` | `/pictures/items/upload` | String a ser procurada (sem diferenciar maiúsculas e minúsculas) |
| `--db` | `crawl_cache.db` | Arquivo do cache SQLite |
| `--workers` | `8` | Número de requisições em paralelo |
| `--max-pages` | `500` | Limite de páginas processadas por execução |
| `--max-age-hours` | `168` (7 dias) | Tempo de validade das páginas no cache |
| `--refresh` | | Ignora o cache e baixa as páginas de novo |
| `--search-only` | | Não faz crawl, só busca no cache |

## Uso responsável

Este projeto é voltado para consultar documentação pública. Antes de rodar em outros sites, confira o `robots.txt` e os termos de uso, mantenha poucos workers para não sobrecarregar o servidor e evite coletar dados pessoais, que ficam sujeitos à LGPD.

Qualquer uso indevido é de estrita responsabilidade de quem utilizou a ferramenta.
