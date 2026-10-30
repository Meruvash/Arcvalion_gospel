"""Endereço público do site, num lugar só: o `url` de config/portal.json (SITE_URL no ambiente manda, como em portal.py).
Trocar o domínio é editar config/portal.json; as ferramentas que montam links absolutos (SEO, sitemap, cartões,
IndexNow, métricas) importam SITE e HOST daqui."""
import json
from pathlib import Path
from urllib.parse import urlparse

from portal import endereco

SITE = endereco(json.loads((Path(__file__).resolve().parent.parent / "config" / "portal.json").read_text(encoding="utf-8"))["url"])
HOST = urlparse(SITE).hostname
