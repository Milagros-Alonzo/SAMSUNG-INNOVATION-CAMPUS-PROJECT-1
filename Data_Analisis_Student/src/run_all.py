from . import mapping_builder, data_prep, features

if __name__ == "__main__":
    # 1) Detectar columnas y generar mapping
    mapping_builder.run()
    # 2) Limpieza del CSV
    data_prep.run()
    # 3) Agregados finales
    features.run()
