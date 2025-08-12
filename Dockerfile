FROM python:3.12.3-slim

ARG PROJECT_ROOT="/app"
ARG SYSTEM_VENV_DIR="${PROJECT_ROOT}/system_venv"
ARG PROJECT_VENV_DIR="${PROJECT_ROOT}/.venv"

RUN mkdir $PROJECT_ROOT
RUN mkdir $SYSTEM_VENV_DIR

RUN python3 -m venv $SYSTEM_VENV_DIR
RUN ${SYSTEM_VENV_DIR}/bin/pip install -U pip setuptools
RUN ${SYSTEM_VENV_DIR}/bin/pip install poetry==1.8.4

WORKDIR $PROJECT_ROOT
COPY . .

RUN POETRY_VIRTUALENVS_IN_PROJECT=true ${SYSTEM_VENV_DIR}/bin/poetry install --compile

ENV PATH=${PROJECT_VENV_DIR}/bin:$PATH
