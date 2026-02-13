import os

from dotenv import load_dotenv
import streamlit as st


# Load .env for local runs. Streamlit Cloud ignores this unless file exists.
load_dotenv(override=False)


def get_setting(key: str, default: str | None = None) -> str | None:
    """Read config from st.secrets first, then environment variables."""
    try:
        val = st.secrets.get(key)
        if val is not None and str(val).strip() != "":
            return str(val)
    except Exception:
        pass
    val = os.getenv(key)
    if val is not None and str(val).strip() != "":
        return str(val)
    return default


def get_mongo_uri() -> str | None:
    return get_setting("MONGODB_URI")


def get_mongo_db(default: str) -> str:
    return get_setting("MONGODB_DB", default=default) or default


def get_mongo_collection(default: str, key: str = "MONGODB_COLLECTION") -> str:
    # Default key keeps compatibility; tips page uses a different key.
    return get_setting(key, default=default) or default

