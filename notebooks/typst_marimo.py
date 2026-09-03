"""Small experimental bridge from Typst HTML export to Marimo output."""

from html import escape
from inspect import cleandoc
import re
from threading import Lock

import marimo
import typst


_FRAGMENT_CSS = r"""
<style>
.typst-fragment {
  color: inherit;
  display: inline-block;
  max-width: 100%;
  overflow-x: auto;
  vertical-align: middle;
}
.typst-fragment > p { margin: 0; }
.typst-error {
  color: var(--error, #b00020);
  font-family: var(--monospace-font, ui-monospace, monospace);
  font-size: 0.875rem;
  white-space: pre-wrap;
}
</style>
"""


def _renderer_state():
    state = getattr(typst, "_marimo_html_renderer", None)
    if state is None:
        state = {
            "compiler": typst.Compiler(ignore_system_fonts=True),
            "lock": Lock(),
            "cache": {},
            "body_pattern": re.compile(
                r"<body(?:\s[^>]*)?>(.*?)</body>",
                re.DOTALL | re.IGNORECASE,
            ),
            "head_pattern": re.compile(
                r"<head(?:\s[^>]*)?>(.*?)</head>",
                re.DOTALL | re.IGNORECASE,
            ),
            "style_pattern": re.compile(
                r"<style(?:\s[^>]*)?>.*?</style>",
                re.DOTALL | re.IGNORECASE,
            ),
            "heading_pattern": re.compile(
                r"<(/?)h([2-6])(?=[\s>])",
                re.IGNORECASE,
            ),
            "mathml_css": "",
        }
        setattr(typst, "_marimo_html_renderer", state)
    return state


def typst_shared_css():
    state = _renderer_state()
    return f'{state["mathml_css"]}{_FRAGMENT_CSS}'


def render_typst_html(
    source,
    *,
    font_size=15.0,
    prose=False,
    include_styles=True,
):
    """Compile one Typst fragment to themed prose or compact HTML."""

    if not isinstance(source, str):
        raise TypeError("Typst source must be a string")

    state = _renderer_state()
    cleaned_source = cleandoc(source)
    try:
        with state["lock"]:
            body = state["cache"].get(cleaned_source)
            if body is None:
                compiled = state["compiler"].compile(
                    input=f"{cleaned_source}\n".encode("utf-8"),
                    format="html",
                )
                if not isinstance(compiled, bytes):
                    raise TypeError("Typst HTML export returned multiple outputs")
                document = compiled.decode("utf-8")
                body_match = state["body_pattern"].search(document)
                if body_match is None:
                    raise ValueError("Typst HTML output did not contain a body")
                head_match = state["head_pattern"].search(document)
                mathml_css = (
                    ""
                    if head_match is None
                    else "".join(
                        state["style_pattern"].findall(head_match.group(1))
                    )
                )
                if mathml_css:
                    state["mathml_css"] = mathml_css
                body = body_match.group(1)
                state["cache"][cleaned_source] = body
                if len(state["cache"]) > 512:
                    state["cache"].pop(next(iter(state["cache"])))

        styles = typst_shared_css() if include_styles else ""
        if prose:
            body = state["heading_pattern"].sub(
                lambda match: f"<{match.group(1)}h{int(match.group(2)) - 1}",
                body,
            )
            return (
                f"{styles}"
                '<div class="markdown prose dark:prose-invert contents">'
                f"{body}</div>"
            )

        size_style = (
            "" if font_size is None else f"font-size:{float(font_size):g}pt"
        )
        return (
            f"{styles}"
            f'<div class="typst-fragment" style="{size_style}">'
            f"{body}</div>"
        )
    except Exception as error:
        diagnostic = str(getattr(error, "diagnostic", None) or error)
        styles = _FRAGMENT_CSS if include_styles else ""
        return (
            f"{styles}"
            '<div class="typst-error" role="alert">'
            "<strong>Typst compilation failed</strong>"
            f"<pre>{escape(diagnostic)}</pre>"
            "</div>"
        )


def typst_html(source, *, font_size=15.0, prose=False):
    """Return one responsive Typst fragment as a Marimo HTML object."""

    return marimo.Html(
        render_typst_html(source, font_size=font_size, prose=prose)
    )


def typst_md(source):
    """Render Typst prose with Marimo's Markdown typography classes."""

    return typst_html(source, font_size=None, prose=True)
