from __future__ import annotations

import os
import re
import ssl
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Any


def _ssl_context() -> ssl.SSLContext:
    if os.environ.get("COA_KB_SSL_INSECURE", "").strip() in {"1", "true", "yes"}:
        return ssl._create_unverified_context()
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()

from .base import ExtractOptions, ExtractResult
from .registry import register_strategy

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\n{3,}")


class _TextCollector(HTMLParser):
    """Minimal HTML → text/markdown-ish fallback when trafilatura is unavailable."""

    SKIP = {"script", "style", "noscript", "svg", "nav", "footer", "header", "aside"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip_depth = 0
        self._parts: list[str] = []
        self.title: str | None = None
        self._in_title = False
        self._in_heading: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        t = tag.lower()
        if t in self.SKIP:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if t == "title":
            self._in_title = True
        if t in {"h1", "h2", "h3", "h4"}:
            self._in_heading = t
            self._parts.append("\n\n")
        if t in {"p", "li", "br", "tr"}:
            self._parts.append("\n")
        if t == "a":
            href = dict(attrs).get("href")
            if href:
                self._parts.append("[")

    def handle_endtag(self, tag: str) -> None:
        t = tag.lower()
        if t in self.SKIP and self._skip_depth:
            self._skip_depth -= 1
            return
        if self._skip_depth:
            return
        if t == "title":
            self._in_title = False
        if t == self._in_heading:
            level = int(t[1])
            # Prefix last line with markdown heading markers — applied in close.
            self._parts.append("\n")
            self._in_heading = None
            self._parts.append(f"\x00H{level}\x00")
        if t == "a":
            self._parts.append("]()")

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        text = data.strip()
        if not text:
            return
        if self._in_title:
            self.title = (self.title or "") + text
            return
        self._parts.append(text + " ")


def _html_to_markdown_fallback(html: str) -> tuple[str, str | None]:
    parser = _TextCollector()
    try:
        parser.feed(html)
        parser.close()
    except Exception:
        plain = _TAG_RE.sub(" ", html)
        return _WS_RE.sub("\n\n", plain).strip(), None

    raw = "".join(parser._parts)
    # Markers were appended after heading text; flip to prefix roughly.
    chunks = re.split(r"\x00H([1-4])\x00", raw)
    out: list[str] = []
    i = 0
    while i < len(chunks):
        if i + 1 < len(chunks) and chunks[i + 1] in "1234":
            body = chunks[i].rstrip()
            level = int(chunks[i + 1])
            # Take last line as heading title.
            lines = body.rsplit("\n", 1)
            if len(lines) == 2:
                out.append(lines[0] + "\n")
                out.append("\n" + ("#" * level) + " " + lines[1].strip() + "\n")
            else:
                out.append("\n" + ("#" * level) + " " + body.strip() + "\n")
            i += 2
        else:
            out.append(chunks[i])
            i += 1
    md = _WS_RE.sub("\n\n", "".join(out)).strip()
    return md, parser.title


def _extract_with_trafilatura(html: str, url: str) -> tuple[str, dict[str, Any]] | None:
    try:
        import trafilatura
    except ImportError:
        return None
    meta: dict[str, Any] = {}
    try:
        downloaded_meta = trafilatura.extract_metadata(html, default_url=url)
        if downloaded_meta:
            meta = {
                "title": downloaded_meta.title,
                "author": downloaded_meta.author,
                "date": downloaded_meta.date,
                "sitename": downloaded_meta.sitename,
            }
    except Exception:
        pass
    md = trafilatura.extract(
        html,
        url=url,
        output_format="markdown",
        include_comments=False,
        include_tables=True,
        favor_recall=True,
    )
    if not md:
        return None
    return md, meta


def _fetch_html(url: str, options: ExtractOptions) -> tuple[str, str, dict[str, str]]:
    req = urllib.request.Request(url, headers={"User-Agent": options.user_agent})
    with urllib.request.urlopen(req, timeout=options.timeout_s, context=_ssl_context()) as resp:
        raw = resp.read()
        ctype = resp.headers.get("Content-Type", "text/html")
        final_url = resp.geturl()
        charset = "utf-8"
        if "charset=" in ctype.lower():
            charset = ctype.split("charset=", 1)[-1].split(";")[0].strip() or "utf-8"
        try:
            html = raw.decode(charset, errors="replace")
        except LookupError:
            html = raw.decode("utf-8", errors="replace")
    return html, final_url, {"content_type": ctype}


class GenericMarkdownStrategy:
    """Default extractor: any URL → clean Markdown. No host-specific logic."""

    id = "generic_markdown"

    def extract(self, url: str, options: ExtractOptions | None = None) -> ExtractResult:
        opts = options or ExtractOptions()
        meta: dict[str, Any] = {
            "url": url,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "strategy_id": self.id,
        }
        try:
            html, final_url, headers = _fetch_html(url, opts)
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"http_error:{exc.code}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"url_error:{exc.reason}") from exc

        meta["final_url"] = final_url
        meta.update(headers)

        if "pdf" in headers.get("content_type", "").lower() or final_url.lower().endswith(".pdf"):
            # PDF: store note; full PDF→text is a later strategy swap.
            return ExtractResult(
                markdown=f"# PDF source\n\nFetched binary PDF from {final_url}. "
                "Text extraction for PDF is a separate strategy.\n",
                html=None,
                structured={"content_type": "application/pdf"},
                meta=meta,
                strategy_id=self.id,
            )

        tf = _extract_with_trafilatura(html, final_url)
        if tf:
            markdown, tf_meta = tf
            meta.update({k: v for k, v in tf_meta.items() if v})
            engine = "trafilatura"
        else:
            markdown, title = _html_to_markdown_fallback(html)
            if title:
                meta["title"] = title
            engine = "stdlib_html_parser"
        meta["extract_engine"] = engine

        return ExtractResult(
            markdown=markdown or "",
            html=html,
            structured=None,
            meta=meta,
            strategy_id=self.id,
        )


register_strategy(GenericMarkdownStrategy())
