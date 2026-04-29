"""Playwright-driven login for grok.com / x.ai accounts.

Mirrors AutoGrok's ``browser.js`` reference implementation: launch a
real Chromium instance, drive ``accounts.x.ai/sign-in`` with the
user's email + password, then capture the cookies and the rotating
``x-statsig-id`` header that grok.com binds to each session.

The captured material is returned as a
:class:`~core.pixelle.grok_web_client.GrokSession` and stored
in-memory by the Producer page (``st.session_state["grok_session"]``).
**Nothing is persisted to disk.** Re-running the page after a process
restart triggers a fresh login.

Playwright is **not** a hard dependency of this project — pulling
Chromium binaries onto every CI runner would slow the test suite to
a crawl. Instead this module lazily imports
:mod:`playwright.sync_api` inside :func:`grok_browser_login` and
raises :class:`GrokBrowserUnavailable` with install instructions if
Playwright (or its bundled Chromium) is missing. Tests should mock
the function rather than driving a real browser.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from core.pixelle.grok_web_client import (
    DEFAULT_USER_AGENT,
    GROK_BASE_URL,
    GrokSession,
)

if TYPE_CHECKING:  # pragma: no cover
    from playwright.sync_api import Page

LOG = logging.getLogger(__name__)

# Where the OAuth-style sign-in flow lives. AutoGrok navigates here
# directly rather than starting on grok.com because the redirect chain
# strips the ``returnTo`` param and the email form gets stuck.
SIGN_IN_URL = "https://accounts.x.ai/sign-in"

# Headers we *must* capture from the live browser before they expire —
# grok.com tightly couples ``x-statsig-id`` to the session and rejects
# requests missing it with a 403 even when cookies are otherwise fine.
INTERESTING_REQUEST_HEADERS = (
    "x-statsig-id",
    "x-xai-request-id",
    "x-grok-client",
    "x-csrf-token",
)

# Watchdog for the entire login dance — long enough to handle slow
# captchas / 2FA prompts but short enough to abort cleanly when the
# remote network is wedged.
DEFAULT_LOGIN_TIMEOUT_MS = 90_000
DEFAULT_REQUEST_WAIT_MS = 30_000


# ─── Errors ─────────────────────────────────────────────────────────────────


class GrokBrowserError(RuntimeError):
    """Base error for any browser-driven Grok login problem."""


class GrokBrowserUnavailable(GrokBrowserError):
    """Raised when Playwright (or its Chromium bundle) is not installed."""


class GrokLoginFailed(GrokBrowserError):
    """Raised when the email/password were rejected or the page hung."""


# ─── Public ─────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class GrokLoginOptions:
    """Tunables for :func:`grok_browser_login`."""

    headless: bool = True
    timeout_ms: int = DEFAULT_LOGIN_TIMEOUT_MS
    request_wait_ms: int = DEFAULT_REQUEST_WAIT_MS


def grok_browser_login(
    email: str,
    password: str,
    *,
    options: GrokLoginOptions | None = None,
) -> GrokSession:
    """Drive ``accounts.x.ai/sign-in`` and return a usable
    :class:`GrokSession`.

    Parameters
    ----------
    email, password:
        Credentials for an active grok.com account.
    options:
        :class:`GrokLoginOptions` — set ``headless=False`` for visible
        debugging.

    Raises
    ------
    GrokBrowserUnavailable
        Playwright or its Chromium browser binary is not installed.
    GrokLoginFailed
        Login form rejected the credentials, never produced a
        post-login cookie, or timed out.
    """
    if not email or not password:
        raise GrokLoginFailed("Email and password are both required.")

    opts = options or GrokLoginOptions()

    sync_playwright = _import_playwright()

    with sync_playwright() as p:  # type: ignore[misc]
        try:
            browser = p.chromium.launch(headless=opts.headless)
        except Exception as exc:  # noqa: BLE001 — wrap binary missing → friendly error
            raise GrokBrowserUnavailable(
                "Playwright is installed but Chromium is missing. "
                "Run `playwright install chromium` to fetch the browser."
            ) from exc

        context = browser.new_context(user_agent=DEFAULT_USER_AGENT)
        page = context.new_page()

        captured_headers: dict[str, str] = {}
        page.on("request", lambda req: _maybe_capture_headers(req, captured_headers))

        try:
            _drive_login_form(page, email=email, password=password, opts=opts)
            _wait_for_grok_cookies(page, opts=opts)
            _trigger_statsig_request(page, opts=opts)
        except GrokLoginFailed:
            browser.close()
            raise
        except Exception as exc:  # noqa: BLE001 — anything else → login failed
            browser.close()
            raise GrokLoginFailed(f"Unexpected error during login: {exc}") from exc

        cookies = _extract_cookies(context)
        browser.close()

    if not cookies:
        raise GrokLoginFailed(
            "Login finished but no grok.com cookies were captured. "
            "The account may need a manual captcha / 2FA step."
        )

    headers = {
        "User-Agent": DEFAULT_USER_AGENT,
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Origin": GROK_BASE_URL,
        "Referer": f"{GROK_BASE_URL}/",
    }
    headers.update(captured_headers)
    return GrokSession(cookies=cookies, headers=headers, email=email)


# ─── Internals ──────────────────────────────────────────────────────────────


def _import_playwright():
    """Lazy-import :mod:`playwright.sync_api` with a friendly error."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover — exercised in tests via monkeypatch
        raise GrokBrowserUnavailable(
            "Playwright is not installed. Run `pip install playwright && "
            "playwright install chromium` to enable Grok login."
        ) from exc
    return sync_playwright


def _drive_login_form(
    page: "Page", *, email: str, password: str, opts: GrokLoginOptions
) -> None:
    """Fill and submit the sign-in form."""
    page.set_default_timeout(opts.timeout_ms)
    page.goto(SIGN_IN_URL, wait_until="domcontentloaded")

    # x.ai sometimes presents email + password on one screen, sometimes
    # email-then-password. Try both common selectors before falling
    # back to a generic ``input[type=...]`` query.
    email_input = _first_visible_locator(
        page,
        [
            "input[name=email]",
            "input[type=email]",
            "input[autocomplete=username]",
        ],
    )
    if email_input is None:
        raise GrokLoginFailed("Could not find the email input on accounts.x.ai/sign-in.")
    email_input.fill(email)

    # Hit Enter or click the "Continue" button if present (two-step flow).
    cont = page.locator("button:has-text('Continue')")
    if cont.count() > 0:
        cont.first.click()
        page.wait_for_load_state("domcontentloaded")

    pwd_input = _first_visible_locator(
        page,
        [
            "input[name=password]",
            "input[type=password]",
            "input[autocomplete=current-password]",
        ],
    )
    if pwd_input is None:
        raise GrokLoginFailed("Could not find the password input on accounts.x.ai/sign-in.")
    pwd_input.fill(password)

    submit = _first_visible_locator(
        page,
        [
            "button[type=submit]",
            "button:has-text('Sign in')",
            "button:has-text('Log in')",
        ],
    )
    if submit is None:
        # Last-ditch: press Enter and hope the form binds it.
        pwd_input.press("Enter")
    else:
        submit.click()


def _wait_for_grok_cookies(page: "Page", *, opts: GrokLoginOptions) -> None:
    """Wait until the page lands somewhere on ``grok.com`` with cookies."""
    # The post-login redirect lands on https://grok.com/?ref=accounts ;
    # we wait for that hostname to appear and the network to settle.
    try:
        page.wait_for_url(
            lambda url: "grok.com" in url,
            timeout=opts.timeout_ms,
        )
    except Exception as exc:  # noqa: BLE001
        raise GrokLoginFailed(
            "Login did not redirect to grok.com (wrong credentials, "
            "captcha, or 2FA blocking)."
        ) from exc

    try:
        page.wait_for_load_state("networkidle", timeout=opts.request_wait_ms)
    except Exception:  # noqa: BLE001 — networkidle is best-effort
        pass


def _trigger_statsig_request(page: "Page", *, opts: GrokLoginOptions) -> None:
    """Make grok.com fire at least one authenticated request so we can
    snag the rotating ``x-statsig-id`` header.

    grok.com's home page issues this header only on the first chat
    list / quota call; we visit the home page (already on it after
    redirect) and wait briefly for the next outbound request.
    """
    try:
        page.wait_for_request(
            lambda req: req.url.startswith(GROK_BASE_URL + "/rest/")
            and req.headers.get("x-statsig-id") is not None,
            timeout=opts.request_wait_ms,
        )
    except Exception:  # noqa: BLE001 — header capture is best-effort
        # Falling through is fine — the cookies alone may still be
        # enough for image generation. Log so the operator can debug.
        LOG.warning("Did not observe an x-statsig-id header during login.")


def _first_visible_locator(page: "Page", selectors: list[str]):
    """Return the first selector with at least one visible match."""
    for sel in selectors:
        loc = page.locator(sel)
        try:
            if loc.count() > 0 and loc.first.is_visible():
                return loc.first
        except Exception:  # noqa: BLE001 — Playwright can race here
            continue
    return None


def _maybe_capture_headers(req, sink: dict[str, str]) -> None:
    """Listener hook: extract headers we care about from each request."""
    headers = req.headers or {}
    for name in INTERESTING_REQUEST_HEADERS:
        value = headers.get(name)
        if value and name not in sink:
            sink[name] = value


def _extract_cookies(context) -> dict[str, str]:
    """Pull the cookies set on grok.com / x.ai after a successful login."""
    out: dict[str, str] = {}
    for c in context.cookies():
        domain = (c.get("domain") or "").lstrip(".")
        if not (domain.endswith("grok.com") or domain.endswith("x.ai")):
            continue
        name = c.get("name")
        value = c.get("value")
        if isinstance(name, str) and isinstance(value, str) and name:
            out[name] = value
    return out


__all__ = [
    "DEFAULT_LOGIN_TIMEOUT_MS",
    "DEFAULT_REQUEST_WAIT_MS",
    "GrokBrowserError",
    "GrokBrowserUnavailable",
    "GrokLoginFailed",
    "GrokLoginOptions",
    "SIGN_IN_URL",
    "grok_browser_login",
]
