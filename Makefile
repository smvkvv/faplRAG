.PHONY: init-db create-user start

init-db:
	docker-compose run airflow-webserver airflow db init

create-user:
	docker-compose run airflow-webserver airflow users create \
		--username admin \
		--firstname Admin \
		--lastname User \
		--role Admin \
		--email admin@example.com \
		--password admin

start:
	docker-compose up

clean-volume:
	docker volume rm faplrag_postgres_data


setup: init-db create-user start
