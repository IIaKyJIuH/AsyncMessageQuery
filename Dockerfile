FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1 \
    UV_LINK_MODE=copy

WORKDIR /mq_task

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock /mq_task/
COPY .env.docker ./mq_task/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

ENV VIRTUAL_ENV=/mq_task/.venv
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

COPY app /mq_task/app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

CMD ["uvicorn", "mq_task.main:app", "--host", "0.0.0.0", "--port", "8000"]
