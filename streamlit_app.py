import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError


st.set_page_config(
    page_title="FreshGuard",
    page_icon="🥬",
    layout="wide",
    initial_sidebar_state="expanded",
)


def get_backend_url() -> str:
    try:
        secret_url = st.secrets.get("API_BASE_URL", "")
    except StreamlitSecretNotFoundError:
        secret_url = ""
    return (
        os.getenv("API_BASE_URL")
        or os.getenv("FRESHGUARD_BACKEND_URL")
        or secret_url
    ).strip().rstrip("/")


def validate_backend_url(base_url: str) -> tuple[str | None, str | None]:
    if not base_url:
        return None, "Set API_BASE_URL in Streamlit secrets or the environment."

    parsed = urlsplit(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return None, "API_BASE_URL must be an absolute HTTP or HTTPS URL."
    if parsed.username or parsed.password:
        return None, "Do not put credentials in API_BASE_URL. Configure secrets on the backend instead."
    if parsed.query or parsed.fragment:
        return None, "API_BASE_URL must not contain a query string or fragment."
    if parsed.path not in {"", "/"}:
        return None, "API_BASE_URL must contain only the backend origin, without a path."
    return base_url, None


@st.cache_data(ttl=15, show_spinner=False)
def fetch_backend_health(base_url: str) -> tuple[dict | None, str | None]:
    request = Request(
        f"{base_url}/health",
        headers={"Accept": "application/json"},
    )
    try:
        with urlopen(request, timeout=8) as response:
            payload = response.read(64 * 1024 + 1)
            if len(payload) > 64 * 1024:
                return None, "Backend health response exceeded the allowed size."
        health = json.loads(payload.decode("utf-8"))
    except HTTPError as exc:
        return None, f"Backend health check returned HTTP {exc.code}."
    except (URLError, TimeoutError, OSError):
        return None, "Could not connect to the configured backend."
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, "Backend returned an invalid health response."

    if not isinstance(health, dict):
        return None, "Backend returned an invalid health response."
    return health, None


st.title("FreshGuard")
st.caption("Streamlit backend status dashboard")

st.info(
    "This Streamlit app is a lightweight status dashboard, not a replacement "
    "for the React/FastAPI FreshGuard application. It currently makes one "
    "backend request: GET /health. Authentication, inventory, reports, and "
    "M1–M4 workflows are not implemented in this interface."
)

with st.sidebar:
    st.markdown("### Backend connection")
    st.caption("Configure API_BASE_URL as an origin such as https://api.example.com.")

backend_url, configuration_error = validate_backend_url(get_backend_url())
if configuration_error:
    st.warning(configuration_error)
    st.code('API_BASE_URL = "https://<your-public-fastapi-host>"', language="toml")
    st.stop()

hostname = urlsplit(backend_url).hostname
if hostname in {"localhost", "127.0.0.1", "::1"}:
    st.warning(
        "This backend URL points to loopback. It works only when Streamlit and "
        "FastAPI run on the same machine; Streamlit Community Cloud needs a "
        "publicly reachable backend URL."
    )

with st.sidebar:
    st.link_button("Open FastAPI docs", f"{backend_url}/docs")

if st.button("Refresh backend status"):
    fetch_backend_health.clear()

with st.spinner("Checking backend health…"):
    health, health_error = fetch_backend_health(backend_url)

if health_error:
    st.error(health_error)
else:
    st.success("Backend health endpoint is reachable.")
    col1, col2, col3 = st.columns(3)
    col1.metric("Service", str(health.get("service", "unknown")))
    col2.metric("Legacy ML availability", str(bool(health.get("ml_available", False))))
    col3.metric("Legacy model status", str(health.get("model_status", "unknown")))
    st.caption(
        "ML availability here reflects the backend health check only. It does "
        "not indicate approval of an M2 v2 image model."
    )
    st.json({
        key: health[key]
        for key in ("status", "service", "ml_available", "model_status")
        if key in health
    })

st.markdown("---")
st.subheader("Platform scope")
st.write(
    "The full FreshGuard workflows remain in the separately hosted FastAPI "
    "backend and React frontend. This page does not run models or access user "
    "data directly."
)
