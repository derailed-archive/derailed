FROM python:3.11.4-slim

WORKDIR /
COPY . .

RUN pip install gunicorn
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction
RUN rm -rf /root/.cache/pypoetry

EXPOSE 14000

CMD [ "gunicorn", "-k", "uvicorn.workers.UvicornWorker" ]