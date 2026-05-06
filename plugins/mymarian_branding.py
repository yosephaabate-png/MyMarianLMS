from tutor import hooks

PRIMARY = "#6F2DBD"
SECONDARY = "#8E44AD"
ACCENT = "#C04CCF"
BG_MAIN = "#FFFFFF"
BG_SOFT = "#F8F9FB"
TEXT_DARK = "#1F2937"

INDIGO_EXTRA_SCSS = f"""
$primary: {PRIMARY};
$secondary: {SECONDARY};
$brand-accent: {ACCENT};
$brand-primary: {PRIMARY};
$brand-secondary: {SECONDARY};
$body-bg: {BG_MAIN};
$footer-bg: {BG_SOFT};
$footer-color: {TEXT_DARK};
$gray-base: {TEXT_DARK};
$text-color: {TEXT_DARK};
$link-color: {PRIMARY};
$link-hover-color: {SECONDARY};
$btn-primary-bg: {PRIMARY};
$btn-primary-border: {PRIMARY};
$btn-primary-hover-bg: {SECONDARY};
$action-primary-bg: {PRIMARY};
$action-primary-hover-bg: {SECONDARY};
"""

MFE_BRAND_CSS = f""":root {{
  --pgn-color-primary: {PRIMARY};
  --pgn-color-primary-base: {PRIMARY};
  --pgn-color-primary-hover: {SECONDARY};
  --pgn-color-primary-active: {SECONDARY};
  --pgn-color-brand-500: {PRIMARY};
  --pgn-color-brand-300: {SECONDARY};
  --pgn-color-accent-a: {ACCENT};
  --pgn-color-accent-b: {ACCENT};
  --pgn-color-white: {BG_MAIN};
  --pgn-color-light-100: {BG_SOFT};
  --pgn-color-light-200: {BG_SOFT};
  --pgn-color-dark-700: {TEXT_DARK};
  --pgn-color-text-default: {TEXT_DARK};
  --pgn-color-background-base: {BG_MAIN};
  --pgn-color-background-soft: {BG_SOFT};
  --pgn-color-footer-background: {BG_SOFT};
  --pgn-color-link-base: {PRIMARY};
  --pgn-color-link-hover: {SECONDARY};
}}

body, .footer, footer {{
  color: {TEXT_DARK};
}}

.footer, footer {{
  background-color: {BG_SOFT} !important;
}}

a {{ color: {PRIMARY}; }}
a:hover {{ color: {SECONDARY}; }}
"""

hooks.Filters.ENV_PATCHES.add_items([
    ("indigo-extra-scss", INDIGO_EXTRA_SCSS),
    ("indigo-extra-sass", INDIGO_EXTRA_SCSS),
    (
        "mfe-dockerfile-post-npm-install",
        (
            "RUN mkdir -p /openedx/brand-overrides && "
            f"printf '%s' {MFE_BRAND_CSS!r} "
            "> /openedx/brand-overrides/mymarian.css && "
            "echo \"@import '/openedx/brand-overrides/mymarian.css';\" "
            ">> src/index.scss || true"
        ),
    ),
    (
        "openedx-lms-common-settings",
        f"""
MYMARIAN_BRAND_CSS = '''
<style>
{MFE_BRAND_CSS}
</style>
'''
""",
    ),
])
