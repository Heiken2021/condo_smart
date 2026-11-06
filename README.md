# Condo_Smart 4.2.2 Build 01 Revision 2
Reconstruction under a no-regression QA gate. Includes SuperAdmin root governance, central authorization, last-root protection, multiple administrators per property, property CRUD and branding, portfolio cards/KPIs/charts, property dashboard charts, schema gate, audit, and preservation of Spaces, People, Users, Catalogs and Audit modules.

## Clean test database
Use a clean test database because the governance schema changes materially. Copy `.streamlit/secrets.toml`, install requirements, run `pytest -q`, then `streamlit run app.py`.
