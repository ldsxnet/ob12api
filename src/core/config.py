"""Config loader with hot-reload support."""
import os
import shutil
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
import tomli_w

_CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "config", "setting.toml")
)

# 镜像内置的默认配置备份路径
_DEFAULT_CONFIG_PATH = "/app/config.default/setting.toml"


def _ensure_config():
    """确保配置文件存在。如果挂载的空卷覆盖了 config 目录，则从镜像备份中恢复。"""
    if os.path.exists(_CONFIG_PATH):
        return
    config_dir = os.path.dirname(_CONFIG_PATH)
    os.makedirs(config_dir, exist_ok=True)
    # 优先从镜像内置备份复制
    if os.path.exists(_DEFAULT_CONFIG_PATH):
        shutil.copy2(_DEFAULT_CONFIG_PATH, _CONFIG_PATH)
        print(f"[config] 已从镜像默认配置恢复: {_CONFIG_PATH}")
    else:
        # 本地开发环境兜底：生成最小默认配置
        default_cfg = {
            "global": {"api_key": "your-api-key"},
            "server": {"host": "0.0.0.0", "port": 8081},
            "admin": {"username": "admin", "password": "admin"},
            "proxy": {"url": ""},
            "retry": {"max_retries": 3, "retry_delay": 1},
            "ob1": {
                "credentials_path": "",
                "workos_auth_url": "https://api.workos.com/user_management/authenticate",
                "workos_client_id": "client_01K8YDZSSKDMK8GYTEHBAW4N4S",
                "api_base": "https://dashboard.openblocklabs.com/api/v1",
                "refresh_buffer_seconds": 600,
                "rotation_mode": "balanced",
                "refresh_interval": 60,
            },
            "logging": {"level": "INFO"},
        }
        with open(_CONFIG_PATH, "wb") as f:
            tomli_w.dump(default_cfg, f)
        print(f"[config] 已生成默认配置文件: {_CONFIG_PATH}")
        print(f"[config] 请通过管理后台修改 API Key 和管理员密码")


def _load():
    _ensure_config()
    with open(_CONFIG_PATH, "rb") as f:
        return tomllib.load(f)


def _save(cfg: dict):
    with open(_CONFIG_PATH, "wb") as f:
        tomli_w.dump(cfg, f)


_cfg = _load()

API_KEY = _cfg["global"]["api_key"]
HOST = _cfg["server"]["host"]
PORT = _cfg["server"]["port"]

# Admin credentials
ADMIN_USERNAME = _cfg.get("admin", {}).get("username", "admin")
ADMIN_PASSWORD = _cfg.get("admin", {}).get("password", "admin")

# Proxy
PROXY_URL = _cfg.get("proxy", {}).get("url", "")

# Retry
MAX_RETRIES = _cfg.get("retry", {}).get("max_retries", 3)
RETRY_DELAY = _cfg.get("retry", {}).get("retry_delay", 1)

# OB-1 config
OB1_CREDENTIALS_PATH = _cfg["ob1"].get("credentials_path", "")
OB1_WORKOS_AUTH_URL = _cfg["ob1"]["workos_auth_url"]
OB1_WORKOS_CLIENT_ID = _cfg["ob1"]["workos_client_id"]
OB1_API_BASE = _cfg["ob1"]["api_base"]
OB1_REFRESH_BUFFER = _cfg["ob1"].get("refresh_buffer_seconds", 600)
OB1_ROTATION_MODE = _cfg["ob1"].get("rotation_mode", "cache-first")
OB1_REFRESH_INTERVAL = _cfg["ob1"].get("refresh_interval", 0)

# Logging
LOG_LEVEL = _cfg.get("logging", {}).get("level", "INFO")


def reload():
    """Reload config from disk into module-level variables."""
    global _cfg, API_KEY, ADMIN_USERNAME, ADMIN_PASSWORD, PROXY_URL, MAX_RETRIES, RETRY_DELAY, OB1_ROTATION_MODE, OB1_REFRESH_INTERVAL, LOG_LEVEL
    _cfg = _load()
    API_KEY = _cfg["global"]["api_key"]
    ADMIN_USERNAME = _cfg.get("admin", {}).get("username", "admin")
    ADMIN_PASSWORD = _cfg.get("admin", {}).get("password", "admin")
    PROXY_URL = _cfg.get("proxy", {}).get("url", "")
    MAX_RETRIES = _cfg.get("retry", {}).get("max_retries", 3)
    RETRY_DELAY = _cfg.get("retry", {}).get("retry_delay", 1)
    OB1_ROTATION_MODE = _cfg["ob1"].get("rotation_mode", "cache-first")
    OB1_REFRESH_INTERVAL = _cfg["ob1"].get("refresh_interval", 0)
    LOG_LEVEL = _cfg.get("logging", {}).get("level", "INFO")


def update_setting(section: str, key: str, value):
    """Update a single setting, persist to disk, and reload."""
    cfg = _load()
    if section not in cfg:
        cfg[section] = {}
    cfg[section][key] = value
    _save(cfg)
    reload()
