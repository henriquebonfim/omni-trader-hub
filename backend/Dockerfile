# Build stage
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ARG TALIB_VERSION=0.6.4
ARG TALIB_SHA256=aa04066d17d69c73b1baaef0883414d3d56ab3775872d82916d1cdb376a3ae86

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fSL "https://github.com/TA-Lib/ta-lib/releases/download/v${TALIB_VERSION}/ta-lib-${TALIB_VERSION}-src.tar.gz" -o /tmp/ta-lib.tar.gz && \
    echo "${TALIB_SHA256}  /tmp/ta-lib.tar.gz" | sha256sum -c - && \
    tar -xzf /tmp/ta-lib.tar.gz -C /tmp && \
    cd /tmp/ta-lib-${TALIB_VERSION} && \
    ./configure --prefix=/usr && \
    make -j$(nproc) && \
    make install && \
    rm -rf /tmp/ta-lib*

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir --prefix=/install -r requirements-dev.txt
RUN pip install --no-cache-dir --prefix=/install --ignore-installed packaging==26.0


# Runtime image
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LD_LIBRARY_PATH=/usr/lib

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/lib/libta-lib* /usr/lib/
COPY --from=builder /install /usr/local

COPY src/ ./src/
COPY config/ ./config/

RUN mkdir -p data && \
    useradd -m appuser && \
    chown -R appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["python", "-m", "src.main"]
