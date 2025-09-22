FROM python:3.12-slim-bookworm

ARG GIT_SHA
ENV GIT_SHA=$GIT_SHA

RUN groupadd -r appuser && \
    useradd -d /home/appuser -m -l -r -g appuser appuser && \
    mkdir -p /opt/numerai_exporter/ && \
    chown appuser:appuser /opt/numerai_exporter/

WORKDIR /opt/numerai_exporter/

COPY requirements.txt .

RUN pip3 install --upgrade pip && \
    python3 -m pip install wheel && \
    python3 -m pip install --upgrade setuptools && \
    pip3 install -r requirements.txt && \
    rm -rf /root/.cache/pip*

COPY . .

USER appuser
