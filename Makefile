.PHONY: init-db create-user start clean-volume setup interface streamlit

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

interface:
	sudo docker compose up -d interface
	@echo "Waiting for interface to be ready..."
	@until sudo docker logs interface 2>&1 | grep -q "Ready to serve"; do \
		sleep 1; \
	done
	@echo "Interface is ready."

streamlit:
	sudo docker compose up -d streamlit

start:
	docker-compose up

clean-volume:
	docker volume rm faplrag_postgres_data

setup: init-db create-user start

run:
	$(MAKE) interface
	$(MAKE) streamlit
