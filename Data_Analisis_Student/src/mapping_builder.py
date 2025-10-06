"""
Genera docs/mapping_columns.json escaneando columnas con patrones típicos del survey:
- Ingresos: O4A.., OGVTL, OGOVB, OOTHL, OPVTL, etc. (O=Oct, N=Nov, D=Dec, J=Jan, F=Feb, M=Mar, A=Apr, Y=May)
- Gastos:  O5A..O5M, O6A..O6D

Si cambian nombres/columnas, vuelve a ejecutar este builder.
"""
from __future__ import annotations
import json, re
import pandas as pd
from .config import RAW_DATA, MAPPING_FILE
from .log import Logger

log = Logger("mapping_builder")
MONTHS = list("ONDFMJAY")

def _starts_with_any(col: str, prefixes: list[str]) -> bool:
    return any(str(col).startswith(p) for p in prefixes)

def _by_suffix(columns: list[str], suffix: str) -> list[str]:
    return sorted([c for c in columns if re.search(rf"{suffix}$", c)])

def build_mapping(df: pd.DataFrame) -> dict:
    income_prefixes = [f"{m}4" for m in MONTHS] + [f"{m}GVTL" for m in MONTHS] + \
                      [f"{m}GOVB" for m in MONTHS] + [f"{m}OTHL" for m in MONTHS] + \
                      [f"{m}PVTL" for m in MONTHS]
    expense_prefixes = [f"{m}5" for m in MONTHS] + [f"{m}6" for m in MONTHS]

    cols = [c.strip().upper() for c in df.columns]

    income_cols = [c for c in cols if _starts_with_any(c, income_prefixes)]
    expense_cols = [c for c in cols if _starts_with_any(c, expense_prefixes)]

    income_map = {
        "trabajo": _by_suffix(income_cols, r"4A"),
        "apoyo_familiar": _by_suffix(income_cols, r"4B"),
        "apoyo_pareja": _by_suffix(income_cols, r"4C"),
        "otros_familia": _by_suffix(income_cols, r"4D"),
        "prestamos_gobierno": sorted([c for c in income_cols if "GVTL" in c]),
        "becas_subsidios": sorted([c for c in income_cols if ("GOVB" in c or "OTHL" in c)]),
        "prestamos_privados": sorted([c for c in income_cols if "PVTL" in c]),
        "prestamos_familia": _by_suffix(income_cols, r"4E"),
        "inversiones_propiedades": _by_suffix(income_cols, r"4F"),
        "pension_seguro": _by_suffix(income_cols, r"4G"),
        "asistencia_gobierno": _by_suffix(income_cols, r"4H"),
        "otros_ingresos": _by_suffix(income_cols, r"4I"),
    }

    expense_map = {
        "vivienda": _by_suffix(expense_cols, r"5A"),
        "electricidad": _by_suffix(expense_cols, r"5B"),
        "calefaccion": _by_suffix(expense_cols, r"5C"),
        "telefono": _by_suffix(expense_cols, r"5D"),
        "internet": _by_suffix(expense_cols, r"5E"),
        "cable": _by_suffix(expense_cols, r"5F"),
        "otras_utilidades": _by_suffix(expense_cols, r"5E1"),
        "hogar": _by_suffix(expense_cols, r"5G"),
        "cuidado_ninos": _by_suffix(expense_cols, r"5H"),
        "transporte": _by_suffix(expense_cols, r"5I"),
        "educacion_libros": _by_suffix(expense_cols, r"5J"),
        "inversiones_personales": _by_suffix(expense_cols, r"5K"),
        "pagos_deuda": _by_suffix(expense_cols, r"5L"),
        "otros_gastos": _by_suffix(expense_cols, r"5M"),
        "alimentacion": _by_suffix(expense_cols, r"6A"),
        "cuidado_personal_salud": _by_suffix(expense_cols, r"6B"),
        "entretenimiento": _by_suffix(expense_cols, r"6C"),
        "ropa_joyeria": _by_suffix(expense_cols, r"6D"),
    }

    return {"income_map": income_map, "expense_map": expense_map}

def run() -> None:
    log.info(f"Leyendo raw CSV: {RAW_DATA}")
    df = pd.read_csv(RAW_DATA)
    mapping = build_mapping(df)
    MAPPING_FILE.write_text(json.dumps(mapping, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info(f"Mapping generado en {MAPPING_FILE}")

if __name__ == "__main__":
    run()
