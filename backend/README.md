# fast_login_db backend

## Project setup

```sh
uv venv --python 3.13.2
uv sync
```

## Run backend

```sh
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

OpenAPI docs: `http://127.0.0.1:8000/docs`

## Auth and user APIs

- `POST /users/`: register user, returns `{ id, username }`
- `POST /login/`: returns `{ msg, user_id, username, access_token, token_type, expires_in, expires_at }`
- `GET /me`: requires `Authorization: Bearer <access_token>`, returns `{ user_id, username, expires_in, expires_at }`
- `POST /logout/`: requires `Authorization: Bearer <access_token>`, invalidates current token
- In Swagger UI (`/docs`), fill `X-Authorization` with `Bearer <access_token>` for `/me` and `/logout/`.
- Non-docs clients should still use standard `Authorization: Bearer <access_token>`.

Session notes:
- Session TTL is controlled by `SESSION_TTL_SECONDS` (default `1800`, minimum `60`).
- Session storage is in-process memory; restarting backend clears all active sessions.

## Core environment variables

Runtime and DB:
- `DATABASE_URL`
- `APP_DEBUG` (default: `false`)
- `SQL_ECHO` (default: `false`)
- `AUTO_CREATE_TABLES` (default: `true`)
- `RESET_DB` + `ALLOW_RESET_DB` (must both be `true` to drop and recreate tables)
- `SESSION_TTL_SECONDS` (default: `1800`, minimum: `60`)

CORS:
- `CORS_ALLOW_ALL` (set `true` for broad allow)
- `CORS_ALLOW_ORIGINS` (comma-separated origins when not allow-all)

Validation policy:
- `USERNAME_MIN_LEN` / `USERNAME_MAX_LEN`
- `USERNAME_PATTERN` / `USERNAME_CHARSET_DESC`
- `USERNAME_ALLOW_CJK`
- `USERNAME_RESERVED`
- `PASSWORD_MIN_LEN` / `PASSWORD_MAX_LEN` / `PASSWORD_MAX_BYTES`
- `PASSWORD_REQUIRE_COMPLEXITY`
- `PASSWORD_MIN_CLASSES`
- `WEAK_PASSWORDS`
- `WEAK_PASSWORDS_FILE`

Schema note:
- `users.username` 数据库列宽固定为 `VARCHAR(64)`。
- `USERNAME_MIN_LEN` 和 `USERNAME_MAX_LEN` 不能超过 `64`，超出会在启动时报错。
- 当 `AUTO_CREATE_TABLES=true`（或 `RESET_DB=true`）时，若历史库列宽小于 `64`，启动会自动扩容。

## Registration validation defaults

- Username length: 4–20
- Username characters: letters / digits / underscore
- Reserved words are blocked: admin, root, system, support, etc.
- Password length: 8–64 (bcrypt byte limit is 72)
- Password must not equal the username
- Common weak passwords are rejected (extensible)
