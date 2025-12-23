# fast_login_db backend

## Project setup

```sh
$ uv venv --python 3.13.2
$ uv sync
```

## Registration Validation Rules (Configurable)

Default policy:

- Username length: 4–20
- Username characters: letters / digits / underscore
- Reserved words are blocked: admin, root, system, support, etc.
- Password length: 8–64 (bcrypt byte limit is 72)
- Password must not equal the username
- Common weak passwords are rejected (extensible)

Environment variables:

- `USERNAME_MIN_LEN` / `USERNAME_MAX_LEN`
- `USERNAME_PATTERN` (custom regex) and `USERNAME_CHARSET_DESC` (error message for the charset)
- `USERNAME_ALLOW_CJK` (allow CJK characters)
- `USERNAME_RESERVED` (comma-separated)
- `PASSWORD_MIN_LEN` / `PASSWORD_MAX_LEN` / `PASSWORD_MAX_BYTES`
- `PASSWORD_REQUIRE_COMPLEXITY` (enable traditional complexity rules)
- `PASSWORD_MIN_CLASSES` (required character class count)
- `WEAK_PASSWORDS` (comma-separated)
- `WEAK_PASSWORDS_FILE` (one password per line)
