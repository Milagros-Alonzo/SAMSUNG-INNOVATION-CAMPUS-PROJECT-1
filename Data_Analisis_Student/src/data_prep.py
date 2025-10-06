from __future__ import annotations
import json
import pandas as pd
from .config import RAW_DATA, INTERIM_CSV, MAPPING_FILE
from .log import Logger

log = Logger("data_prep")

def run() -> None:
    mapping = _load_or_fail_mapping()
    df = _read_raw()

    money_cols = _resolve_money_cols(df, mapping)
    df = _clean_monetary(df, money_cols)

    df.to_csv(INTERIM_CSV, index=False)
    log.info(f"Interim guardado en {INTERIM_CSV} (shape={df.shape})")

# -------- helpers --------

def _load_or_fail_mapping() -> dict:
    if not MAPPING_FILE.exists():
        raise FileNotFoundError(
            f"No existe {MAPPING_FILE}. Ejecuta antes: python -m src.mapping_builder"
        )
    return json.loads(MAPPING_FILE.read_text(encoding="utf-8"))

def _read_raw() -> pd.DataFrame:
    log.info(f"Leyendo raw: {RAW_DATA}")
    df = pd.read_csv(RAW_DATA)
    df.columns = [c.strip().replace(" ", "_").upper() for c in df.columns]
    return df

def _resolve_money_cols(df: pd.DataFrame, mapping: dict) -> list[str]:
    income = sum(mapping["income_map"].values(), [])
    expense = sum(mapping["expense_map"].values(), [])
    all_cols = sorted(set(income + expense))
    return [c for c in all_cols if c in df.columns]

def _winsorize(s: pd.Series, lower=0.0, upper=0.99) -> pd.Series:
    if s.dropna().empty:
        return s
    lo, hi = s.quantile(lower), s.quantile(upper)
    return s.clip(lower=lo, upper=hi)

def _is_expense_col(col: str) -> bool:
    return col.endswith(("5A","5B","5C","5D","5E","5F","5E1","5G","5H","5I","5J","5K","5L","5M",
                         "6A","6B","6C","6D"))

def _clean_monetary(df: pd.DataFrame, money_cols: list[str]) -> pd.DataFrame:
    for c in money_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
        if _is_expense_col(c):
            df[c] = df[c].abs()
        df[c] = df[c].fillna(0.0)
        df[c] = _winsorize(df[c], upper=0.99)
    return df
