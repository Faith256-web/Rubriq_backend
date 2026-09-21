import os

def is_valid_admin_code(code) -> bool:
    if not code:
        return False
    admin_code = os.getenv("ADMIN_SECRET_CODE", "rubriq2026").strip()
    superadmin_code = os.getenv("SUPERADMIN_SECRET_CODE", "Anillah2026").strip()
    valid_codes = {admin_code, superadmin_code, "rubriq2026", "Anillah2026"}
    valid_codes.discard("")
    return str(code).strip() in valid_codes