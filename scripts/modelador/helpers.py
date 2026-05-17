def str2float(value):
    """Converte string para float tratando exceções e valores vazios."""
    if value is None:
        return None
    try:
        val_clean = str(value).strip().replace(",", ".")
        if val_clean == "" or val_clean.lower() in ["none", "null", "nan"]:
            return None
        return float(val_clean)
    except ValueError:
        return None
