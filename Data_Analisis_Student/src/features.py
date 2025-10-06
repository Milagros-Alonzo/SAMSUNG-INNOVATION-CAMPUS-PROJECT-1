from __future__ import annotations
import json
import pandas as pd
from .config import INTERIM_CSV, PROCESSED_CSV, MAPPING_FILE
from .log import Logger

log = Logger("features")

def run() -> None:
    mapping = json.loads(MAPPING_FILE.read_text(encoding="utf-8"))
    df = pd.read_csv(INTERIM_CSV)
    agg = _monthly_aggregations(df, mapping)
    agg.to_csv(PROCESSED_CSV, index=False)
    log.info(f"Processed guardado en {PROCESSED_CSV} (shape={agg.shape})")

# -------- helpers --------

def _monthly_aggregations(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    result = pd.DataFrame(index=df.index)

    # Ingresos
    income_total = 0
    for alias, cols in mapping["income_map"].items():
        cols = [c for c in cols if c in df.columns]
        result[f"ing_{alias}"] = df[cols].sum(axis=1) if cols else 0
        income_total = income_total + result[f"ing_{alias}"]

    result["ingresos_totales"] = income_total

    # Gastos
    expense_total = 0
    for alias, cols in mapping["expense_map"].items():
        cols = [c for c in cols if c in df.columns]
        result[f"gas_{alias}"] = df[cols].sum(axis=1) if cols else 0
        expense_total = expense_total + result[f"gas_{alias}"]

    result["gastos_totales"] = expense_total
    result["balance_total"] = result["ingresos_totales"] - result["gastos_totales"]
    return result.reset_index(drop=True)
