# fast_login_db frontend

## Install dependencies

```sh
npm install
```

## Development server

```sh
npm run serve
```

Frontend default URL: `http://127.0.0.1:8080`

## Build for production

```sh
npm run build
```

## Lint

```sh
npm run lint
```

## API base URL

Use either `VITE_API_BASE_URL` or `VUE_APP_API_BASE_URL`.

Example (`.env.local`):

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Session behavior (single-account)

- Single-account mode only; no recent-account list and no quick-switch UI.
- After login, title uses account history: first login shows `登录成功`, later logins show `欢迎回来`.
- `退出登录` invalidates current bearer token and clears active login state.

## Local storage keys

- `fast_login_db_auth`: current active session (`accessToken`, `username`, `expiresAt`)
- `fast_login_db_login_history`: per-account login history used by title behavior

To reset local frontend session state quickly:

```js
localStorage.removeItem('fast_login_db_auth');
localStorage.removeItem('fast_login_db_login_history');
location.reload();
```
