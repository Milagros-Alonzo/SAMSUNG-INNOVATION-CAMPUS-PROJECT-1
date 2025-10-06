from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

RAW_DATA      = BASE_DIR / "data" / "raw" / "dataset_estudiantes_modifcado.csv"
INTERIM_CSV   = BASE_DIR / "data" / "interim" / "dataset_clean.csv"
PROCESSED_CSV = BASE_DIR / "data" / "processed" / "student_monthly_agg.csv"

MAPPING_FILE  = BASE_DIR / "docs" / "mapping_columns.json"

# crear carpetas si no existen
INTERIM_CSV.parent.mkdir(parents=True, exist_ok=True)
PROCESSED_CSV.parent.mkdir(parents=True, exist_ok=True)
MAPPING_FILE.parent.mkdir(parents=True, exist_ok=True)
