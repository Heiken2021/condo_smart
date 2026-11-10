from pathlib import Path
A=Path("app.py").read_text(encoding="utf-8")
def test_sidebar_logo_reads_global_settings():
 assert "get_system_identity,get_setting" in A
 assert "SYSTEM_LOGO_WIDTH" in A and "SYSTEM_LOGO_MAX_HEIGHT" in A
def test_sidebar_logo_no_longer_hardcodes_dimensions():
 assert "max_width=245,max_height=180" not in A
 assert "max_width=sidebar_logo_width,max_height=sidebar_logo_height" in A
