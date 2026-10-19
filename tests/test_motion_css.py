"""Motion CSS contract: content must stay visible without scroll timelines."""
import re
import unittest

from tests.helpers import ROOT

SUPPORTS = "@supports (animation-timeline: view())"
REDUCED = "@media (prefers-reduced-motion: reduce)"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def strip_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def _match_end(css: str, open_idx: int) -> int:
    depth = 0
    for i in range(open_idx, len(css)):
        if css[i] == "{":
            depth += 1
        elif css[i] == "}":
            depth -= 1
            if depth == 0:
                return i + 1
    raise ValueError("unbalanced braces")


def extract_block(css: str, prelude: str) -> str:
    """Return the full text of the block starting at `prelude` (incl. braces)."""
    start = css.find(prelude)
    if start == -1:
        return ""
    open_idx = css.index("{", start)
    return css[start:_match_end(css, open_idx)]


def strip_keyframes(css: str, prefix: str) -> str:
    """Remove every `@keyframes <prefix>...{...}` block."""
    while True:
        m = re.search(r"@keyframes\s+" + re.escape(prefix), css)
        if not m:
            return css
        end = _match_end(css, css.index("{", m.start()))
        css = css[:m.start()] + css[end:]


class MotionCssTests(unittest.TestCase):
    def css(self) -> str:
        return strip_comments(read("static/css/motion.css"))

    def test_hidden_state_only_inside_supports(self):
        css = self.css()
        inside = extract_block(css, SUPPORTS)
        self.assertTrue(inside)
        outside = strip_keyframes(css.replace(inside, ""), prefix="hero-")
        self.assertIn("opacity: 0", inside)
        self.assertNotIn("opacity: 0", outside)

    def test_reveal_uses_view_timeline(self):
        inside = extract_block(self.css(), SUPPORTS)
        self.assertIn("animation-timeline: view()", inside)
        self.assertIn("scroll(root)", inside)
        for mod in ("reveal--left", "reveal--right", "reveal--zoom"):
            self.assertIn(mod, inside)

    def test_hero_keyframes_outside_supports(self):
        css = self.css()
        outside = css.replace(extract_block(css, SUPPORTS), "")
        self.assertRegex(outside, r"@keyframes hero-")

    def test_reduced_motion_disables_animation(self):
        block = extract_block(self.css(), REDUCED)
        self.assertIn("animation: none !important", block)
        self.assertIn("transition: none !important", block)
        self.assertIn("scroll-behavior: auto !important", block)
        self.assertIn("opacity: 1 !important", block)

    def test_style_css_never_hides_reveal(self):
        css = strip_comments(read("static/css/style.css"))
        self.assertNotRegex(css, r"\.reveal[^{]*\{[^}]*opacity:\s*0")

    def test_helpers(self):
        css = "@a{x{y:1}} @keyframes hero-a{from{opacity: 0}} @keyframes b{}"
        self.assertEqual(extract_block(css, "@a"), "@a{x{y:1}}")
        self.assertNotIn("hero-a", strip_keyframes(css, "hero-"))
        self.assertIn("@keyframes b", strip_keyframes(css, "hero-"))


if __name__ == "__main__":
    unittest.main()
