FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jdk-headless \
    curl \
    wget \
    bash \
    tini \
    procps \
    && rm -rf /var/lib/apt/lists/*

RUN JAVA_PATH="$(dirname "$(dirname "$(readlink -f "$(which javac)")")")" \
    && ln -s "${JAVA_PATH}" /opt/java-home

ENV JAVA_HOME=/opt/java-home
ENV PYSPARK_PYTHON=python3
ENV SPARK_LOCAL_IP=127.0.0.1

WORKDIR /workspace

COPY requirements.txt /tmp/requirements.txt

RUN pip install --upgrade pip setuptools wheel && \
    pip install -r /tmp/requirements.txt

RUN mkdir -p /opt/spark-jars

RUN wget -O /opt/spark-jars/iceberg-spark-runtime-3.5_2.12-1.10.1.jar \
    https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.10.1/iceberg-spark-runtime-3.5_2.12-1.10.1.jar

RUN wget -O /opt/spark-jars/postgresql-42.7.5.jar \
    https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.5/postgresql-42.7.5.jar

EXPOSE 8888

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["tini", "--", "/usr/local/bin/docker-entrypoint.sh"]