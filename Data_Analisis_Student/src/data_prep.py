from __future__ import annotations
import json
import pandas as pd
from .config import RAW_DATA, INTERIM_CSV, MAPPING_FILE
from .log import Logger

log = Logger("data_prep")

def run() -> None:
    mapping = _load_mapping()
    df = _read_raw()

    # Renombrar SOLO columnas monetarias (según mapping)
    rename_map = {orig: meta["std"] for orig, meta in mapping["rename_map"].items()}
    df = df.rename(columns=rename_map)

    # Columnas monetarias estandarizadas
    money_std_cols = sorted(set(
        sum(mapping["income_map_std"].values(), []) +
        sum(mapping["expense_map_std"].values(), [])
    ))

    if not money_std_cols:
        log.warn("No se detectaron columnas monetarias. Revisa mapping_builder.")
    else:
        df = _clean_monetary(df, money_std_cols)

    log.info(f"Escribiendo CSV limpio en: {INTERIM_CSV}")
    df.to_csv(INTERIM_CSV, index=False)
    log.info(f"Interim guardado (shape={df.shape})")

# -------- helpers --------

def _load_mapping() -> dict:
    if not MAPPING_FILE.exists():
        raise FileNotFoundError(f"No existe {MAPPING_FILE}. Corre: python -m src.mapping_builder")
    return json.loads(MAPPING_FILE.read_text(encoding="utf-8"))

def _read_raw() -> pd.DataFrame:
    log.info(f"Leyendo raw: {RAW_DATA}")
    return pd.read_csv(RAW_DATA)

def _is_expense_std(col: str) -> bool:
    # por convención en std_name: *_gas_*__
    return "_gas_" in col

def _winsorize(s: pd.Series, lower=0.0, upper=0.99) -> pd.Series:
    s2 = pd.to_numeric(s, errors="coerce")
    if s2.dropna().empty:
        return s2
    lo, hi = s2.quantile(lower), s2.quantile(upper)
    return s2.clip(lower=lo, upper=hi)

def _clean_monetary(df: pd.DataFrame, money_cols: list[str]) -> pd.DataFrame:
    for c in money_cols:
        s = pd.to_numeric(df.get(c), errors="coerce")
        if _is_expense_std(c):
            s = s.abs()
        s = _winsorize(s, upper=0.99).fillna(0.0)
        df[c] = s
    return df
