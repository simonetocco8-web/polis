FROM python:3.12.14-slim
WORKDIR /simulation
COPY requirements.lock .
RUN --mount=type=secret,id=build_ca \
    if [ -s /run/secrets/build_ca ]; then export PIP_CERT=/run/secrets/build_ca; fi \
    && pip install --no-cache-dir -r requirements.lock
COPY demos ./demos
COPY oikonomia ./oikonomia
COPY config ./config
COPY sources ./sources
ENTRYPOINT ["python", "-m", "demos.cli"]
