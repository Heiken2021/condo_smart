from pathlib import Path
F=Path("core/formatting.py").read_text(encoding="utf-8")
D=Path("views/dashboard.py").read_text(encoding="utf-8")
P=Path("views/portafolio.py").read_text(encoding="utf-8")
E=Path("views/espacios.py").read_text(encoding="utf-8")
def test_money_uses_global_currency_setting():
 assert 'get_setting("DEFAULT_CURRENCY","MXN")' in F
 assert 'CURRENCY_SYMBOLS' in F
def test_financial_kpis_use_money_formatter():
 assert "money(x['cargos'])" in D and "money(x['pagos'])" in D and "money(x['gastos'])" in D
 assert "money(charges)" in P and "money(paid)" in P
def test_spaces_formats_base_fee_as_currency():
 assert '"Cuota Base":money(r.get("cuota_base"))' in E
 assert 'st.write("Cuota Base:",money(row.get("cuota_base")))' in E
