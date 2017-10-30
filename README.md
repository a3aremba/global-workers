# Global-workers

### How to build

`$ docker build --rm --no-cache -t global-workers .`


### How to develop

* make sure that `redis` is available
* install `virtualenv` via `pip`, `apt`, etc
* activate `virtualenv`
* install requirements: `$ pip install -r requirements-dev.txt`
* run an app: `$ celery worker -A core.app --loglevel=info` in case if
  `redis` is running at `localhost:6379`
* or use env variables:
`$ CELERY_BROKER_URL=${REDIS_URL} DUMP_URL=${REDIS_URL} celery worker -A core.app --loglevel=info`


### How to test
...