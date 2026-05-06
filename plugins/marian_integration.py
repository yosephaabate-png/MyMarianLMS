"""
Marian frontend <-> OpenEDX integration.

Wires up the OpenEDX (MyMarianLMS) side for a React SPA hosted at
https://marian-seven.vercel.app to: SSO via OAuth2 PKCE, call LMS REST
APIs (courses, enrollments, grades) with JWT, and iframe-embed course
units.

Requires a public LMS_HOST with HTTPS for the Vercel app to reach it.
"""
from tutor import hooks

MARIAN_ORIGIN = "https://marian-seven.vercel.app"
MARIAN_OAUTH_CLIENT_ID = "marian-frontend"

LMS_SETTINGS_PATCH = f"""
# --- Marian frontend integration ---
CORS_ORIGIN_WHITELIST = list(globals().get("CORS_ORIGIN_WHITELIST", [])) + [
    "{MARIAN_ORIGIN}",
]
CSRF_TRUSTED_ORIGINS = list(globals().get("CSRF_TRUSTED_ORIGINS", [])) + [
    "{MARIAN_ORIGIN}",
]
LOGIN_REDIRECT_WHITELIST = list(globals().get("LOGIN_REDIRECT_WHITELIST", [])) + [
    "marian-seven.vercel.app",
]
CORS_ALLOW_CREDENTIALS = True
CORS_URLS_REGEX = r"^(/api/|/oauth2/|/user_api/).*$"

# Allow iframe embedding of course units inside Marian.
X_FRAME_OPTIONS = "ALLOW-FROM " + "{MARIAN_ORIGIN}"
CONTENT_SECURITY_POLICY = {{
    "frame-ancestors": ["'self'", "{MARIAN_ORIGIN}"],
}}

# Make JWTs include enough claims for Marian to identify the user.
JWT_AUTH = dict(globals().get("JWT_AUTH", {{}}), **{{
    "JWT_PAYLOAD_USER_ATTRIBUTES": ("email", "username", "user_id"),
    "JWT_AUTH_COOKIE_HEADER_PAYLOAD": "edx-jwt-cookie-header-payload",
    "JWT_AUTH_COOKIE_SIGNATURE": "edx-jwt-cookie-signature",
}})
"""

# Init task: create / update the OAuth2 Application for Marian on first
# `tutor local do init`. Public client + PKCE means no client_secret is
# stored on the SPA.
INIT_TASK = f"""
./manage.py lms shell <<'PYEOF'
from oauth2_provider.models import Application
from django.contrib.auth import get_user_model

User = get_user_model()
admin = User.objects.filter(is_superuser=True).first()
if admin is None:
    admin = User.objects.first()

app, created = Application.objects.update_or_create(
    client_id="{MARIAN_OAUTH_CLIENT_ID}",
    defaults=dict(
        name="Marian Frontend",
        user=admin,
        client_type=Application.CLIENT_PUBLIC,
        authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        redirect_uris="{MARIAN_ORIGIN}/auth/callback",
        skip_authorization=True,
    ),
)
print("Marian OAuth2 app:", "created" if created else "updated", app.client_id)

try:
    from openedx.core.djangoapps.oauth_dispatch.models import ApplicationAccess
    ApplicationAccess.objects.update_or_create(
        application=app,
        defaults={{"scopes": "read write profile email user_id"}},
    )
    print("Marian ApplicationAccess scopes set.")
except Exception as e:
    print("Skipping ApplicationAccess setup:", e)
PYEOF
"""

hooks.Filters.ENV_PATCHES.add_items(
    [
        ("openedx-lms-common-settings", LMS_SETTINGS_PATCH),
    ]
)

hooks.Filters.CLI_DO_INIT_TASKS.add_item(("lms", INIT_TASK))
