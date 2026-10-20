import re

from markdown_it import MarkdownIt

_SAFE_LINK = re.compile(r"^(?:https?://|mailto:)", re.IGNORECASE)
_HAS_SCHEME = re.compile(r"^[a-z][a-z0-9+.\-]*:", re.IGNORECASE)


def _is_safe(url: str) -> bool:
    url = url.strip()
    return bool(_SAFE_LINK.match(url)) or not _HAS_SCHEME.match(url)


def _drop_unsafe_links(state) -> None:
    """Unwrap links with disallowed schemes so only their text remains."""
    for block in state.tokens:
        if block.type != "inline" or not block.children:
            continue
        kept, skipping = [], []
        for tok in block.children:
            if tok.type == "link_open":
                unsafe = not _is_safe(tok.attrGet("href") or "")
                skipping.append(unsafe)
                if unsafe:
                    continue
            elif tok.type == "link_close":
                if skipping.pop():
                    continue
            elif tok.type == "image" and not _is_safe(tok.attrGet("src") or ""):
                tok.type, tok.tag, tok.attrs, tok.children = "text", "", {}, None
                tok.content = tok.content
            kept.append(tok)
        block.children = kept


_md = MarkdownIt("commonmark", {"html": False})
_md.validateLink = lambda url: True  # unsafe URLs are unwrapped by _drop_unsafe_links
_md.core.ruler.push("drop_unsafe_links", _drop_unsafe_links)


def render_markdown(md: str) -> str:
    return _md.render(md)
