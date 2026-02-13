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


# ---------------------------------------------------------------------------
# Central MongoDB connection manager
# ---------------------------------------------------------------------------
_mongo_client = None


def get_client():
    """Return a shared MongoClient with proper TLS, timeout, and retry config.

    The client is created once per process and reused (connection pooling).
    If the connection is dead, the client is recreated automatically.
    """
    global _mongo_client

    uri = get_mongo_uri()
    if not uri:
        return None

    # Reuse existing healthy client
    if _mongo_client is not None:
        try:
            _mongo_client.admin.command("ping")
            return _mongo_client
        except Exception:
            try:
                _mongo_client.close()
            except Exception:
                pass
            _mongo_client = None

    # Build new client with robust settings
    try:
        import certifi
        tls_ca = certifi.where()
    except ImportError:
        tls_ca = None

    from pymongo import MongoClient

    kwargs = {
        "serverSelectionTimeoutMS": 30000,
        "connectTimeoutMS": 20000,
        "socketTimeoutMS": 60000,
        "retryWrites": True,
        "retryReads": True,
    }
    if tls_ca:
        kwargs["tlsCAFile"] = tls_ca

    client = MongoClient(uri, **kwargs)
    client.admin.command("ping")
    _mongo_client = client
    return _mongo_client


def get_collection(db_default: str, col_default: str, col_key: str = "MONGODB_COLLECTION"):
    """Return a pymongo Collection using the shared client.

    Returns None if connection fails.
    """
    client = get_client()
    if client is None:
        return None
    db_name = get_mongo_db(db_default)
    col_name = get_mongo_collection(col_default, key=col_key)
    return client[db_name][col_name]
