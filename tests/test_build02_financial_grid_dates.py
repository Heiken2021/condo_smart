from pathlib import Path


VIEW = Path(
    "views/financial_governance.py"
).read_text(encoding="utf-8")


def test_grid_dates_are_business_text():
    assert (
        '"Desde": ('
        in VIEW
    )

    assert (
        '"Hasta": ('
        in VIEW
    )

    assert (
        "Sin fecha de término"
        in VIEW
    )


def test_grid_does_not_force_business_text_into_datecolumn():
    grid_start = VIEW.index(
        "event = st.dataframe("
    )

    grid_end = VIEW.index(
        "selected_rows =",
        grid_start,
    )

    block = VIEW[
        grid_start:grid_end
    ]

    assert (
        "DateColumn("
        not in block
    )

    assert (
        "TextColumn("
        in block
    )


def test_grid_formats_existing_dates():
    assert (
        "_date("
        in VIEW
    )


def test_missing_start_date_uses_dash():
    assert (
        'else "—"'
        in VIEW
    )
