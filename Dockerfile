FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

COPY ./app /app/app
COPY ./alembic /app/alembic
COPY ./alembic.ini /app/

COPY ./requirements.txt /app/requirements.txt
COPY ./tests /app/tests
COPY ./run_tests.sh /app/
COPY ./entrypoint.sh /app/

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
RUN pip install --no-cache-dir geopy exponent_server_sdk

CMD ["bash", "/app/entrypoint.sh"]