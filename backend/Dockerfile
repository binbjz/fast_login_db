FROM python:3.13-slim

WORKDIR /app/backend
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

COPY pyproject.toml ./
RUN python - <<'PY'
import subprocess
import tomllib

with open("pyproject.toml", "rb") as handle:
    data = tomllib.load(handle)

deps = data.get("project", {}).get("dependencies", [])
if deps:
    subprocess.check_call(["pip", "install", "--no-cache-dir", *deps])
PY

COPY . .
EXPOSE 8000
