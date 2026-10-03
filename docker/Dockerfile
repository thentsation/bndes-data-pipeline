# CI (o Jenkins roda docker build --target test): ruff, mypy e pytest com cobertura
# mínima de 90% em Python 3.11 e 3.12, nas versões fixadas em config/requirements-dev.txt
# (atualizadas pelo Renovate). pip-audit e Trivy rodam no pipeline da plataforma, fora do
# cache de build, porque o resultado muda com as bases de vulnerabilidades.
FROM python:3.11-slim AS lint

WORKDIR /app

COPY config/requirements.txt config/requirements-dev.txt ./config/

RUN pip install --no-cache-dir -r ./config/requirements.txt \
    $(grep -E '^(ruff|mypy|types-requests|boto3-stubs\[s3\])==' ./config/requirements-dev.txt)

COPY . .

RUN ruff check . && ruff format --check . && mypy && touch /ok

FROM python:3.11-slim AS pytest-py311

WORKDIR /app

COPY config/requirements.txt config/requirements-dev.txt ./config/

RUN pip install --no-cache-dir -r ./config/requirements.txt \
    $(grep -E '^(pytest|pytest-cov)==' ./config/requirements-dev.txt)

COPY . .

RUN pytest --cov=src --cov-report=term-missing --cov-fail-under=90 && touch /ok

FROM python:3.12-slim AS pytest-py312

WORKDIR /app

COPY config/requirements.txt config/requirements-dev.txt ./config/

RUN pip install --no-cache-dir -r ./config/requirements.txt \
    $(grep -E '^(pytest|pytest-cov)==' ./config/requirements-dev.txt)

COPY . .

RUN pytest --cov=src --cov-report=term-missing --cov-fail-under=90 && touch /ok

FROM scratch AS test

COPY --from=lint /ok /lint.ok
COPY --from=pytest-py311 /ok /pytest-py311.ok
COPY --from=pytest-py312 /ok /pytest-py312.ok

# Imagem da Lambda (publicada no ECR pelo Terraform, fora do Jenkins).
FROM public.ecr.aws/lambda/python:3.11 AS runtime

RUN yum update -y && \
    yum clean all && \
    rm -rf /var/cache/yum

RUN pip install --no-cache-dir --upgrade pip setuptools

COPY config/requirements.txt ./
RUN pip install --no-cache-dir --default-timeout=1000 --only-binary=:all: -r requirements.txt -t "/var/task"

COPY src/ ./

ARG APP_VERSION=dev
ENV APP_VERSION=$APP_VERSION

CMD ["app.lambda_handler"]

# Fora da AWS a imagem sobe o Runtime Interface Emulator na 8080: o healthcheck só
# confirma que ele está aceitando conexões (invocar o handler buscaria dados do BNDES).
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import socket; socket.create_connection(('127.0.0.1', 8080), timeout=4).close()"]
