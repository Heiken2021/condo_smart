from pathlib import Path
COMMANDS=Path("services/financial_governance_commands.py").read_text(encoding="utf-8")
VIEW=Path("views/financial_governance.py").read_text(encoding="utf-8")
GRID=Path("services/financial_rules_grid.py").read_text(encoding="utf-8")
MIG=Path("database/migrations/029_financial_global_scope_build02.sql").read_text(encoding="utf-8")

def test_dynamic_definition_and_applicability_commands_exist():
    assert "def create_financial_rule_definition(" in COMMANDS
    assert "def set_financial_rule_applicability(" in COMMANDS
    assert "FINANCIAL_RULE_DEFINITION_CREATED" in COMMANDS
    assert "FINANCIAL_RULE_APPLICABILITY_SET" in COMMANDS

def test_catalog_is_global_admin_governed():
    assert "FINANCIAL_RULE_DEFINITION_REQUIRES_GLOBAL_ADMIN" in COMMANDS
    assert "Catálogo y asignación de reglas" in VIEW

def test_any_property_uses_data_driven_catalog():
    assert "TIPO_INMUEBLE" in VIEW
    assert "Todos los inmuebles" in VIEW
    assert "Sólo en ciertos tipos de inmueble" in VIEW
    assert "Plaza Satélite" not in VIEW
    assert "Las Misiones I" not in VIEW

def test_grid_explains_origin():
    for label in ["Catálogo de reglas","Global heredada","Propia del inmueble","Modificada localmente"]:
        assert label in GRID
    assert "Disponible global" not in GRID
    assert '"Origen"' in VIEW

def test_migration_does_not_seed_rules_or_properties():
    assert "INSERT INTO financial_rules" not in MIG
    assert "INSERT INTO financial_rule_versions" not in MIG
    assert "Plaza Satélite" not in MIG
    assert "Las Misiones I" not in MIG

def test_empty_property_does_not_block_dynamic_catalog():
    assert "Actualmente no hay reglas compatibles asignables para esta tipología" in VIEW
    assert "Puedes crear una nueva regla global" in VIEW
    assert "crear una regla propia para este inmueble" in VIEW
    assert "No es necesario modificar código" not in VIEW

def test_catalog_contract_is_universal_not_property_specific():
    for forbidden in ["Plaza Satelite", "Plaza Satélite", "Plaza Las Golondrinas", "Amores - 819", "Las Misiones I"]:
        assert forbidden not in VIEW
        assert forbidden not in GRID

def test_global_catalog_entry_point_is_always_visible():
    assert "Catálogo y asignación de reglas" in VIEW
    assert "global_rule_catalog_grid_" in VIEW
    assert "+ Nueva regla global" in VIEW
    assert "+ Nueva regla propia del inmueble" in VIEW

def test_business_console_uses_catalog_grid_and_assignment():
    assert "Catálogo y asignación de reglas" in VIEW
    assert "list_global_financial_rule_catalog(" in VIEW
    assert '"Asignación al inmueble"' in VIEW
    assert "global_rule_catalog_grid_" in VIEW

def test_business_console_separates_catalog_from_property_configuration():
    assert "#### Configuración del inmueble" in VIEW
    assert "+ Nueva regla global" in VIEW
    assert "+ Nueva regla propia del inmueble" in VIEW

def test_business_console_hides_technical_choices():
    assert 'st.selectbox("Tipo de resultado"' not in VIEW
    assert 'st.text_input("Dominio"' not in VIEW
    assert '"GLOBAL_PARA_TODOS"' not in VIEW
    assert '"LIMITADA_POR_TIPOLOGIA"' not in VIEW
    assert '"Todos los inmuebles"' in VIEW
    assert '"Sólo en ciertos tipos de inmueble"' in VIEW

def test_final_catalog_semantics_and_assignment_actions():
    assert "Catálogo de reglas" in GRID
    assert "Disponible para asignar" in GRID
    assert 'origin_label="Catálogo global"' not in GRID
    assert "Asignar a este inmueble" in VIEW
    assert "Configurar para este inmueble" in VIEW
    assert "aplicabilidad sólo puede modificarse" in VIEW
    assert "Actualmente no hay reglas compatibles asignables para esta tipología" in VIEW

def test_financial_rule_code_is_suggested_but_admin_editable():
    assert "def _suggest_business_code(" in VIEW
    assert "st.session_state[code_key]=suggest_financial_rule_code(name=name)" in VIEW
    assert '"Código de la regla"' in VIEW
    assert "Puedes editarla antes de guardar" in VIEW
    assert "unicidad" in VIEW

def test_code_suggestion_normalizes_business_name():
    assert 'unicodedata.normalize("NFKD"' in VIEW
    assert 'text.upper()' in VIEW
    assert 'strip("_")' in VIEW

def test_business_form_does_not_submit_on_enter():
    assert "enter_to_submit=False" in VIEW
    assert "Guardar es la única acción que registra la definición" in VIEW

def test_ui_uses_governed_rn_code_suggestion():
    assert "suggest_financial_rule_code," in VIEW
    assert "st.session_state[code_key]=suggest_financial_rule_code(name=name)" in VIEW

def test_name_widget_is_outside_form_and_updates_code_state_on_change():
    assert 'name=st.text_input(' in VIEW
    assert 'key=name_key' in VIEW
    assert 'previous_name=st.session_state.get(last_name_key, "")' in VIEW
    assert 'name != previous_name' in VIEW
    assert 'st.session_state[code_key]=suggest_financial_rule_code(name=name)' in VIEW
    assert 'key=code_key' in VIEW
    assert 'enter_to_submit=False' in VIEW

def test_availability_uses_clear_business_language_and_multiselect():
    assert "¿En qué inmuebles podrá utilizarse esta regla?" in VIEW
    assert "Sólo en ciertos tipos de inmueble" in VIEW
    assert "La disponibilidad determina dónde puede utilizarse la regla" in VIEW
    assert "No la asigna automáticamente a los inmuebles" in VIEW
    assert "Selecciona los tipos de inmueble" in VIEW
    assert "st.multiselect(" in VIEW
    assert '"Fraccionamiento": "FRACCIONAMIENTO"' in VIEW
    assert '"Plaza comercial": "PLAZA_COMERCIAL"' in VIEW
    assert '"Condominio vertical": "VERTICAL"' in VIEW

def test_multiple_property_types_are_persisted_as_applicability_rows():
    assert "for property_type in property_types:" in VIEW
    assert "SELECCIONA_AL_MENOS_UN_TIPO_DE_INMUEBLE" in VIEW

def test_code_generation_shows_business_feedback():
    assert "code_generated=True" in VIEW
    assert "Código de la regla generado:" in VIEW
    assert "Puedes editarlo antes de guardar." in VIEW

def test_code_generation_feedback_is_persistent_after_generation():
    assert "st.success(" in VIEW
    assert "Código de la regla generado:" in VIEW
    assert "st.spinner(" not in VIEW

def test_global_financial_catalog_uses_canonical_superadmin_role():
    commands=Path("services/financial_governance_commands.py").read_text(encoding="utf-8")
    assert '"SUPERADMIN"' in commands
    assert '"SUPER_ADMIN"' not in commands

def test_property_grid_uses_definition_only_business_semantics():
    assert 'if row.get("configured")\n                    else "—"' in VIEW
    assert '"Por definir"\n                    if not row.get("configured")' in VIEW

def test_assign_from_catalog_opens_governed_create_rule_flow():
    assert 'st.session_state[f"selected_financial_rule_{property_id}"] = (selected["definition_id"], None)' in VIEW
    assert 'st.session_state[f"governance_rule_action_{property_id}"] = "CREATE_RULE"' in VIEW
    assert 'st.session_state[f"assignment_flow_notice_{property_id}"] = True' in VIEW
    assert "Asignación iniciada. Revisa y confirma la configuración del inmueble" in VIEW
    assert "todavía no se ha creado ninguna versión" in VIEW

def test_catalog_assignment_defaults_to_property_scope():
    assert 'st.session_state[f"assignment_from_catalog_{property_id}"] = True' in VIEW
    assert 'st.session_state[f"rule_new_scope_{property_id}"] = "INMUEBLE"' in VIEW
