FROM python:3.12-slim-trixie

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock /app/

COPY main.py static/ templates/ /app/

WORKDIR /app

RUN uv sync --locked

CMD ["uv", "run", "python", "main.py"]