import os,streamlit as st
PRODUCT_NAME='Condo_Smart'; BUILD='4.2.2-build.01-r2'; SCHEMA_VERSION='4.2.2.1-r2'
def secret(name,default=None):
 try:return st.secrets[name]
 except Exception:return os.getenv(name,default)
def database_url():
 v=secret('DATABASE_URL')
 if not v:raise RuntimeError('Falta DATABASE_URL')
 return v
