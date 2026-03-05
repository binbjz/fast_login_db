# fast register and login with FastAPI、PostgreSQL and Vue.js

---

### Start the FastAPI backend  
Open a command line window in the project root directory and run the command  
```sh
uvicorn backend.main:app --reload
```

### Start the Vue.js frontend  
Open another command line window in the frontend project directory, first run
```sh
npm install
```
(if it's the first time you are running the project), then run 
```sh
npm run serve
```

---

Starting the FastAPI backend and Vue.js frontend for a typical web application project.

---

### Start everything with Docker (frontend + backend + database)

```sh
docker compose up -d --build
```

Then open the app at:
- Frontend: http://127.0.0.1:8080
- OpenAPI: http://127.0.0.1:8000/docs

More backend runtime/config details are documented in `backend/README.md`.
