from __future__ import annotations
import json
import pandas as pd
import matplotlib.pyplot as plt
from .config import INTERIM_CSV, PROCESSED_CSV, MAPPING_FILE, FIG_DIR
from .log import Logger

log = Logger("features")

from .config import INTERIM_CSV, PROCESSED_CSV, MAPPING_FILE
try:
    from .config import FIG_DIR
except Exception:
    # Fallback por si FIG_DIR no está en config (evita otro ImportError)
    from pathlib import Path
    from .config import BASE_DIR
    FIG_DIR = (BASE_DIR / "docs" / "figures")
    FIG_DIR.mkdir(parents=True, exist_ok=True)

def run() -> None:
    mapping = json.loads(MAPPING_FILE.read_text(encoding="utf-8"))
    df = pd.read_csv(INTERIM_CSV)

    agg = _aggregate(df, mapping)
    agg.to_csv(PROCESSED_CSV, index=False)
    log.info(f"Processed guardado en {PROCESSED_CSV} (shape={agg.shape})")

    _print_quick_checks(agg)
    _make_plots(agg)

# -------- helpers --------

def _aggregate(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    result = pd.DataFrame(index=df.index)

    ing_total = 0
    for alias, cols in mapping.get("income_map_std", {}).items():
        cols = [c for c in cols if c in df.columns]
        result[f"ing_{alias}"] = df[cols].sum(axis=1) if cols else 0
        ing_total = ing_total + result[f"ing_{alias}"]

    gas_total = 0
    for alias, cols in mapping.get("expense_map_std", {}).items():
        cols = [c for c in cols if c in df.columns]
        result[f"gas_{alias}"] = df[cols].sum(axis=1) if cols else 0
        gas_total = gas_total + result[f"gas_{alias}"]

    result["ingresos_totales"] = ing_total
    result["gastos_totales"]   = gas_total
    result["balance_total"]    = result["ingresos_totales"] - result["gastos_totales"]
    return result.reset_index(drop=True)

def _print_quick_checks(agg: pd.DataFrame) -> None:
    print("\n== HEAD PROCESSED ==")
    cols = [c for c in agg.columns if c.startswith(("ing_","gas_"))][:10]
    cols += [c for c in ["ingresos_totales","gastos_totales","balance_total"] if c in agg.columns]
    print(agg[cols].head(5))

    print("\n== RESUMEN ==")
    print(agg[["ingresos_totales","gastos_totales","balance_total"]].describe())

    # Top categorías
    ing_cols = [c for c in agg.columns if c.startswith("ing_") and c!="ingresos_totales"]
    gas_cols = [c for c in agg.columns if c.startswith("gas_") and c!="gastos_totales"]
    print("\nTop ingresos por suma:")
    print(agg[ing_cols].sum().sort_values(ascending=False).head(10))
    print("\nTop gastos por suma:")
    print(agg[gas_cols].sum().sort_values(ascending=False).head(10))

def _make_plots(agg: pd.DataFrame) -> None:
    ing_cols = [c for c in agg.columns if c.startswith("ing_") and c!="ingresos_totales"]
    gas_cols = [c for c in agg.columns if c.startswith("gas_") and c!="gastos_totales"]

    if not ing_cols and not gas_cols:
        log.warn("No hay columnas de ingresos/gastos para graficar.")
        return

    ing_sum = agg[ing_cols].sum().sort_values(ascending=False) if ing_cols else None
    gas_sum = agg[gas_cols].sum().sort_values(ascending=False) if gas_cols else None

    # Barras ingresos
    if ing_sum is not None and ing_sum.sum() != 0:
        fig, ax = plt.subplots()
        ing_sum.head(10).plot(kind="bar", ax=ax)
        ax.set_title("Top ingresos por categoría (suma global)")
        ax.set_ylabel("Monto")
        fig.savefig(FIG_DIR / "ingresos_top10.png", bbox_inches="tight"); plt.close(fig)

    # Barras gastos
    if gas_sum is not None and gas_sum.sum() != 0:
        fig, ax = plt.subplots()
        gas_sum.head(10).plot(kind="bar", ax=ax)
        ax.set_title("Top gastos por categoría (suma global)")
        ax.set_ylabel("Monto")
        fig.savefig(FIG_DIR / "gastos_top10.png", bbox_inches="tight"); plt.close(fig)

    # Histograma balance
    if "balance_total" in agg.columns:
        fig, ax = plt.subplots()
        agg["balance_total"].plot(kind="hist", bins=30, ax=ax)
        ax.set_title("Histograma de balance_total")
        ax.set_xlabel("balance_total")
        fig.savefig(FIG_DIR / "hist_balance_total.png", bbox_inches="tight"); plt.close(fig)

    log.info(f"Gráficas guardadas en {FIG_DIR}")
