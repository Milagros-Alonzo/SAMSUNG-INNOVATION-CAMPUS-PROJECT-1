from __future__ import annotations
import json, re
import pandas as pd
from .config import RAW_DATA, MAPPING_FILE
from .log import Logger

log = Logger("mapping_builder")

# --------- Config semántica (ajustable) ---------
MONTH_LETTER_TO_NAME = {
    "o": "oct",  # Oct
    "n": "nov",  # Nov
    "d": "dec",  # Dec
    "j": "jan",  # Jan
    "f": "feb",  # Feb
    "m": "mar",  # Mar
    "a": "apr",  # Apr
    "y": "may",  # May
}

INCOME_CODE_TO_CATEGORY = {
    "4A":  ("trabajo",                 "Ingresos por trabajo/empleo"),
    "4B":  ("apoyo_familiar",          "Apoyo de familia"),
    "4C":  ("apoyo_pareja",            "Apoyo de pareja"),
    "4D":  ("otros_familia",           "Apoyo de otros familiares"),
    "4E":  ("prestamos_familia",       "Préstamos de familia/amigos"),
    "4F":  ("inversiones_propiedades", "Ingresos por inversiones/propiedades"),
    "4G":  ("pension_seguro",          "Pensiones/seguros"),
    "4H":  ("asistencia_gobierno",     "Asistencia del gobierno"),
    "4I":  ("otros_ingresos",          "Otros ingresos"),
    "GVTL":("prestamos_gobierno",      "Préstamos gubernamentales"),
    "GOVB":("becas_subsidios",         "Becas/Subsidios gubernamentales"),
    "OTHL":("becas_subsidios",         "Otros subsidios/ayudas"),
    "PVTL":("prestamos_privados",      "Préstamos privados"),
}

EXPENSE_CODE_TO_CATEGORY = {
    "5A":  ("vivienda",                "Renta/Vivienda"),
    "5B":  ("electricidad",            "Electricidad"),
    "5C":  ("calefaccion",             "Calefacción"),
    "5D":  ("telefono",                "Teléfono"),
    "5E":  ("internet",                "Internet"),
    "5F":  ("cable",                   "Cable/TV"),
    "5E1": ("otras_utilidades",        "Otras utilidades"),
    "5G":  ("hogar",                   "Artículos/servicios del hogar"),
    "5H":  ("cuidado_ninos",           "Cuidado de niños"),
    "5I":  ("transporte",              "Transporte"),
    "5J":  ("educacion_libros",        "Educación y libros"),
    "5K":  ("inversiones_personales",  "Inversiones personales"),
    "5L":  ("pagos_deuda",             "Pagos de deuda"),
    "5M":  ("otros_gastos",            "Otros gastos"),
    "6A":  ("alimentacion",            "Alimentación"),
    "6B":  ("cuidado_personal_salud",  "Cuidado personal y salud"),
    "6C":  ("entretenimiento",         "Entretenimiento"),
    "6D":  ("ropa_joyeria",            "Ropa y joyería"),
}

# o|n|d|j|f|m|a|y + (4A..4I / 5A..5M / 6A..6D / 5E1 / GVTL/GOVB/OTHL/PVTL)
COL_RE = re.compile(
    r"^(?P<mon>[ondjfmay])(?P<code>(?:[456][A-MD])|5E1|GVTL|GOVB|OTHL|PVTL)$",
    re.IGNORECASE
)

def _std_name(month: str, kind: str, category: str, code: str) -> str:
    # Evitar colisiones (p.ej. GOVB y OTHL misma categoría): agregamos el código
    return f"{month}_{kind}_{category}__{code.lower()}"

def _parse_col(col: str):
    m = COL_RE.match(str(col).strip())
    if not m:
        return None
    mon = MONTH_LETTER_TO_NAME.get(m.group("mon").lower())
    code = m.group("code").upper()
    if not mon:
        return None

    if code in INCOME_CODE_TO_CATEGORY:
        cat_key, desc = INCOME_CODE_TO_CATEGORY[code]
        return dict(
            original=col, month=mon, kind="ing", category=cat_key, code=code,
            description=desc, std=_std_name(mon, "ing", cat_key, code)
        )
    if code in EXPENSE_CODE_TO_CATEGORY:
        cat_key, desc = EXPENSE_CODE_TO_CATEGORY[code]
        return dict(
            original=col, month=mon, kind="gas", category=cat_key, code=code,
            description=desc, std=_std_name(mon, "gas", cat_key, code)
        )
    return None

def build_mapping(df: pd.DataFrame) -> dict:
    records = []
    for c in df.columns:
        r = _parse_col(c)
        if r:
            records.append(r)

    # rename_map: original -> std (con metadatos)
    rename_map = {r["original"]: r for r in records}

    # mapas por categoría (originales y estandarizados)
    income_map_orig, expense_map_orig = {}, {}
    income_map_std,  expense_map_std  = {}, {}

    for r in records:
        target_orig = income_map_orig if r["kind"] == "ing" else expense_map_orig
        target_std  = income_map_std  if r["kind"] == "ing" else expense_map_std
        target_orig.setdefault(r["category"], []).append(r["original"])
        target_std.setdefault(r["category"], []).append(r["std"])

    return {
        "rename_map": rename_map,
        "income_map_orig": income_map_orig,
        "expense_map_orig": expense_map_orig,
        "income_map_std": income_map_std,
        "expense_map_std": expense_map_std,
    }

def run() -> None:
    log.info(f"Leyendo raw CSV: {RAW_DATA}")
    df = pd.read_csv(RAW_DATA)
    mapping = build_mapping(df)
    MAPPING_FILE.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info(f"Mapping generado en {MAPPING_FILE}")
    # Resumen útil
    im = {k: len(v) for k, v in mapping["income_map_std"].items()}
    em = {k: len(v) for k, v in mapping["expense_map_std"].items()}
    log.info(f"Income cols detectadas: {im}")
    log.info(f"Expense cols detectadas: {em}")

if __name__ == "__main__":
    run()
