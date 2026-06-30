FROM python:3.14-slim

# Install git for VS Code source control integration
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip && pip install build
RUN pip install --no-cache-dir \
    ipykernel \
    jupyterlab \
    pandas \
    matplotlib

COPY base.requirements.txt /tmp/
RUN pip install -r /tmp/base.requirements.txt && rm /tmp/base.requirements.txt

# Set the default shell to bash
ENV SHELL /bin/bash