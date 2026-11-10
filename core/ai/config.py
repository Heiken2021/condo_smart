import os


DEFAULT_AI_MODEL = "gpt-4o-mini"


def _streamlit_secret(name):
    try:
        import streamlit as st
        return st.secrets.get(name)
    except Exception:
        return None


def get_ai_api_key():
    return (
        os.getenv("OPENAI_API_KEY")
        or _streamlit_secret("OPENAI_API_KEY")
    )


def get_ai_model():
    return (
        os.getenv("CONDO_SMART_AI_MODEL")
        or _streamlit_secret("CONDO_SMART_AI_MODEL")
        or DEFAULT_AI_MODEL
    )


def ai_is_configured():
    return bool(get_ai_api_key())
