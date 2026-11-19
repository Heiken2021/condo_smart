from pathlib import Path

VIEW=Path("views/financial_governance.py").read_text(encoding="utf-8")

def test_existing_global_template_has_availability_admin():
    assert 'Administrar disponibilidad' in VIEW
    assert 'Tipos de inmueble permitidos' in VIEW
    assert 'Guardar disponibilidad' in VIEW

def test_availability_admin_is_global_admin_only():
    assert 'user.get("rol_global") in {"ROOT", "SUPERADMIN"}' in VIEW

def test_availability_uses_governed_command_for_all_supported_types():
    assert 'set_financial_rule_applicability(' in VIEW
    assert 'included=(property_type_code in selected_codes)' in VIEW
    for code in ['FRACCIONAMIENTO','PLAZA_COMERCIAL','VERTICAL']:
        assert code in VIEW

def test_business_copy_separates_availability_from_assignment():
    assert 'Esto no asigna ni crea una regla en ningún inmueble.' in VIEW
    assert 'El catálogo y el Workflow usarán esta configuración.' in VIEW
