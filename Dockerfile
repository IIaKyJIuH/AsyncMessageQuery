FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1 \
    UV_LINK_MODE=copy

WORKDIR /bobr_task

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock /bobr_task/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY app /bobr_task/app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

ENV PATH="/bobr_task/.venv/bin:$PATH"

CMD ["uvicorn", "bobr_task.main:app", "--host", "0.0.0.0", "--port", "8000"]
