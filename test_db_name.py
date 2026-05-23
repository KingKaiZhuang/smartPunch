import sqlitecloud
from urllib.parse import urlsplit, urlunsplit
from env_config import get_required_env

db_names = ["personnel_data", "personnel_data.sqlite", "personnel_data.db"]

for db_name in db_names:
    try:
        base_url = get_required_env("SQLITECLOUD_URL")
        parts = urlsplit(base_url)
        conn = sqlitecloud.connect(urlunsplit((parts.scheme, parts.netloc, f"/{db_name}", parts.query, parts.fragment)))
        print(f"Success with {db_name}")
        break
    except Exception as e:
        print(f"Failed with {db_name}: {e}")

