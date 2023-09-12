FROM python:3.11
WORKDIR /workdir
COPY pyproject.toml /workdir
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --only main
COPY src /workdir/src
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]