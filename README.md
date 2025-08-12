# Yelp
Sample FastAPI application
Uses:
* Clean architecture with dependency injection
* docker
* poetry
* sqlalchemy (with asyncpg driver)
* alembic
* pytest (with factoryboy for model generation)
* pre-commit (mypy, ruff)

## Run instructions

Clone code to local machine:

```shell
git clone git@github.com:alexbobrow/yelp.git
```

Create database tables:

```shell
docker compose run --rm web alembic upgrade head
```

Fill with some demo DB entries:

```shell
docker compose run --rm web python -m scripts.fill_demo
```

Run the app:

```shell
docker compose up
```

Run tests:

```shell
docker compose run --rm -e DB_NAME=test web pytest
```

## Application

Application provides two endpoints:

Retrieve company information by its ID:

```
http://127.0.0.1:8000/api/v1/companies/{id}/
```

List and search companies:

```
http://127.0.0.1:8000/api/v1/companies/
```

More detailed API description can be found in Swagger UI:
```
http://127.0.0.1:8000/docs
```

Application endpoints are protected with static API key. To authorize the client need to provide `Authorisation`
header, with key followed by word `Token`. API key is configured via environment variable `API_KEY` and initially
set as ```123456789```.

Example request:
```
curl -X 'GET' \
  'http://127.0.0.1:8000/api/v1/companies/' \
  -H 'accept: application/json' \
  -H 'authorization: Token 123456789'
```
