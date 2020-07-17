FROM python:3.7

# System deps:
RUN pip install poetry

# Copy only requirements to cache them in docker layer
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

# Project initialization:
RUN POETRY_VIRTUALENVS_CREATE=false poetry install --no-interaction --no-ansi

# Creating folders, and files for a project:
COPY . /code