"""環境變數與本機 .env 載入輔助。"""
from pathlib import Path
import os


def load_dotenv_file(path=".env"):
    dotenv_path = Path(path)
    if not dotenv_path.exists():
        return

    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value


load_dotenv_file()


def get_required_env(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"缺少必要環境變數：{name}")
    return value