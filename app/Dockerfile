FROM python:3.12-slim-trixie

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml /app/pyproject.toml

COPY uv.lock /app/uv.lock 

COPY main.py /app/main.py

COPY config.py /app/config.py

COPY chat /app/chat

COPY static /app/static

COPY templates /app/templates
 
RUN uv sync --locked

CMD ["uv", "run", "python", "main.py"]
