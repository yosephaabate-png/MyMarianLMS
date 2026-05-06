from tutor import hooks

PRIMARY = "#6F2DBD"
SECONDARY = "#8E44AD"
ACCENT = "#C04CCF"
BG_MAIN = "#FFFFFF"
BG_SOFT = "#F8F9FB"
TEXT_DARK = "#1F2937"

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
  --pgn-color-link-base: {PRIMARY};
  --pgn-color-link-hover: {SECONDARY};
}}
body {{ color: {TEXT_DARK}; background-color: {BG_MAIN}; }}
.footer, footer {{ background-color: {BG_SOFT} !important; color: {TEXT_DARK}; }}
a {{ color: {PRIMARY}; }}
a:hover {{ color: {SECONDARY}; }}
.btn-primary {{ background-color: {PRIMARY}; border-color: {PRIMARY}; }}
.btn-primary:hover, .btn-primary:focus {{ background-color: {SECONDARY}; border-color: {SECONDARY}; }}
"""

# Escape for safe single-quoted heredoc inside a Dockerfile RUN.
MFE_BRAND_CSS_ESCAPED = MFE_BRAND_CSS.replace("'", "'\\''")

MFE_DOCKERFILE_PATCH = f"""RUN printf '%s' '{MFE_BRAND_CSS_ESCAPED}' > public/mymarian-brand.css \\
 && sed -i 's#</head>#<link rel="stylesheet" href="/mymarian-brand.css"></head>#' public/index.html
"""

MFE_NAMES = [
    "learning",
    "learner-dashboard",
    "profile",
    "account",
    "discussions",
    "authn",
]

LMS_INLINE_CSS = f"""
MYMARIAN_BRAND_CSS = '''<style>
{MFE_BRAND_CSS}
</style>'''
"""

# Append our SCSS variable overrides directly onto the indigo theme
# inside the openedx image at build time. This recolors footer bg, body
# text, links, and buttons in the legacy LMS / Studio templates (which
# tutor-indigo's INDIGO_PRIMARY_COLOR / INDIGO_ACCENT_COLOR alone do not
# cover). The "|| true" guards against the file path moving in a future
# indigo release so that the openedx image still builds.
INDIGO_OVERRIDE_SCSS = f"""
// MyMarian brand overrides
$primary: {PRIMARY};
$secondary: {SECONDARY};
$brand-primary: {PRIMARY};
$brand-secondary: {SECONDARY};
$brand-accent: {ACCENT};
$body-bg: {BG_MAIN};
$footer-bg: {BG_SOFT};
$footer-color: {TEXT_DARK};
$text-color: {TEXT_DARK};
$gray-base: {TEXT_DARK};
$link-color: {PRIMARY};
$link-hover-color: {SECONDARY};
$btn-primary-bg: {PRIMARY};
$btn-primary-border: {PRIMARY};
$btn-primary-hover-bg: {SECONDARY};
$action-primary-bg: {PRIMARY};
$action-primary-hover-bg: {SECONDARY};
"""

INDIGO_OVERRIDE_SCSS_ESCAPED = INDIGO_OVERRIDE_SCSS.replace("'", "'\\''")

OPENEDX_DOCKERFILE_PATCH = f"""
RUN for f in \\
      /openedx/themes/indigo/lms/static/sass/partials/lms/theme/_variables.scss \\
      /openedx/themes/indigo/cms/static/sass/partials/cms/theme/_variables.scss; do \\
      [ -f "$f" ] && printf '%s' '{INDIGO_OVERRIDE_SCSS_ESCAPED}' >> "$f" || true; \\
    done
"""

hooks.Filters.ENV_PATCHES.add_items(
    [(f"mfe-dockerfile-post-npm-install-{name}", MFE_DOCKERFILE_PATCH) for name in MFE_NAMES]
    + [
        ("openedx-lms-common-settings", LMS_INLINE_CSS),
        ("openedx-cms-common-settings", LMS_INLINE_CSS),
        ("openedx-dockerfile-post-python-install", OPENEDX_DOCKERFILE_PATCH),
    ]
)
