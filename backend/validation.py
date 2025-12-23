import os
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, Set


DEFAULT_RESERVED_USERNAMES = {
    "admin",
    "root",
    "system",
    "support",
    "superuser",
    "administrator",
    "管理员",
}

DEFAULT_WEAK_PASSWORDS = {
    "123456",
    "12345678",
    "123456789",
    "111111",
    "11111111",
    "000000",
    "00000000",
    "password",
    "password1",
    "qwerty",
    "qwerty123",
    "abc123",
    "letmein",
    "iloveyou",
    "admin",
}


def _bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _int_env(name: str, default: int, *, minimum: int | None = None) -> int:
    raw = os.getenv(name)
    if raw is None:
        value = default
    else:
        try:
            value = int(raw)
        except ValueError:
            value = default
    if minimum is not None and value < minimum:
        value = minimum
    return value


def _split_env_list(name: str) -> Iterable[str]:
    raw = os.getenv(name, "")
    if not raw.strip():
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def _load_weak_passwords_from_file(path: str) -> Set[str]:
    passwords: Set[str] = set()
    try:
        with open(path, "r", encoding="utf-8") as handle:
            for line in handle:
                cleaned = line.strip()
                if not cleaned or cleaned.startswith("#"):
                    continue
                passwords.add(cleaned.casefold())
    except FileNotFoundError:
        pass
    except OSError:
        pass
    return passwords


@dataclass(frozen=True)
class ValidationConfig:
    username_min_len: int
    username_max_len: int
    username_pattern: re.Pattern[str]
    username_charset_desc: str
    username_reserved: Set[str]
    password_min_len: int
    password_max_len: int
    password_max_bytes: int
    password_require_complexity: bool
    password_min_classes: int
    weak_passwords: Set[str]


@lru_cache(maxsize=1)
def get_validation_config() -> ValidationConfig:
    username_min_len = _int_env("USERNAME_MIN_LEN", 4, minimum=1)
    username_max_len = _int_env("USERNAME_MAX_LEN", 20, minimum=username_min_len)
    allow_cjk = _bool_env("USERNAME_ALLOW_CJK", False)
    pattern_override = os.getenv("USERNAME_PATTERN", "").strip()
    charset_override = os.getenv("USERNAME_CHARSET_DESC", "").strip()

    if pattern_override:
        try:
            username_pattern = re.compile(pattern_override)
        except re.error:
            username_pattern = re.compile(r"^[A-Za-z0-9_]+$")
    elif allow_cjk:
        username_pattern = re.compile(r"^[A-Za-z0-9_\u4e00-\u9fff]+$")
    else:
        username_pattern = re.compile(r"^[A-Za-z0-9_]+$")

    if charset_override:
        username_charset_desc = charset_override
    elif allow_cjk and not pattern_override:
        username_charset_desc = "用户名仅允许字母、数字、下划线和中文"
    else:
        username_charset_desc = "用户名仅允许字母、数字和下划线"

    reserved_from_env = {item.casefold() for item in _split_env_list("USERNAME_RESERVED")}
    if reserved_from_env:
        username_reserved = reserved_from_env
    else:
        username_reserved = {item.casefold() for item in DEFAULT_RESERVED_USERNAMES}

    password_min_len = _int_env("PASSWORD_MIN_LEN", 8, minimum=1)
    password_max_len = _int_env("PASSWORD_MAX_LEN", 64, minimum=password_min_len)
    password_max_bytes = _int_env("PASSWORD_MAX_BYTES", 72, minimum=1)
    password_require_complexity = _bool_env("PASSWORD_REQUIRE_COMPLEXITY", False)
    password_min_classes = min(_int_env("PASSWORD_MIN_CLASSES", 3, minimum=1), 4)

    weak_passwords = {item.casefold() for item in DEFAULT_WEAK_PASSWORDS}
    weak_passwords.update(item.casefold() for item in _split_env_list("WEAK_PASSWORDS"))
    weak_passwords_file = os.getenv("WEAK_PASSWORDS_FILE", "").strip()
    if weak_passwords_file:
        weak_passwords.update(_load_weak_passwords_from_file(weak_passwords_file))

    return ValidationConfig(
        username_min_len=username_min_len,
        username_max_len=username_max_len,
        username_pattern=username_pattern,
        username_charset_desc=username_charset_desc,
        username_reserved=username_reserved,
        password_min_len=password_min_len,
        password_max_len=password_max_len,
        password_max_bytes=password_max_bytes,
        password_require_complexity=password_require_complexity,
        password_min_classes=password_min_classes,
        weak_passwords=weak_passwords,
    )


def _password_class_count(password: str) -> int:
    classes = 0
    if re.search(r"[A-Z]", password):
        classes += 1
    if re.search(r"[a-z]", password):
        classes += 1
    if re.search(r"\d", password):
        classes += 1
    if re.search(r"[^A-Za-z0-9]", password):
        classes += 1
    return classes


def validate_username(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("用户名必须是字符串")

    username = value.strip()
    if not username:
        raise ValueError("用户名不能为空")

    config = get_validation_config()

    if not (config.username_min_len <= len(username) <= config.username_max_len):
        raise ValueError(f"用户名长度应为 {config.username_min_len}~{config.username_max_len} 个字符")

    if not config.username_pattern.fullmatch(username):
        raise ValueError(config.username_charset_desc)

    normalized = username.casefold()
    for reserved in config.username_reserved:
        if reserved and reserved in normalized:
            raise ValueError("用户名包含保留词，不能使用")

    return username


def validate_password(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("密码必须是字符串")

    if not value.strip():
        raise ValueError("密码不能为空")

    config = get_validation_config()

    if len(value) < config.password_min_len or len(value) > config.password_max_len:
        raise ValueError(f"密码长度应为 {config.password_min_len}~{config.password_max_len} 个字符")

    if len(value.encode("utf-8")) > config.password_max_bytes:
        raise ValueError(f"密码过长（超过 {config.password_max_bytes} 字节）")

    if value.casefold() in config.weak_passwords:
        raise ValueError("密码过于简单，请更换")

    if config.password_require_complexity:
        if _password_class_count(value) < config.password_min_classes:
            raise ValueError("密码需包含大写/小写/数字/特殊符号中的足够组合")

    return value


def validate_password_not_equal(username: str, password: str) -> None:
    if username.casefold() == password.casefold():
        raise ValueError("密码不能与用户名相同")
