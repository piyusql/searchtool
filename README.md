# searchtool
A scalable tool to make web search for given text using different search engine.

## Features
* Given a simple string to search, it will look for available 3 search engines.
* It will return the searh_id quickly and then backend process will start.
* All intermediate results will be stored in redis-cache, on completion will be written to disk.
* Django celery worker will be responsible for running the async tasks scheduled.

## Steps
* Application runs with python-3.7 and the package dependencies are listed on requirements.txt.
* Docker setup is done using python-3.7 and postgres-11.3 to make the deployment experience better.
* Load testing has been performed using the `locust.io` module to make sure the app scales well.
* Unittest and coverage for the app is enabled to get quality check-in with each and every commits.

## Important commands
* `docker-compose up -d` to do the docker setup and run app
* `$ celery -A searchtool worker -l info` to start celery worker
