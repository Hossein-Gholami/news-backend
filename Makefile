
deps-export:
	poetry export --without-hashes --format=requirements.txt > requirements.txt

stop-app:
	docker-compose stop news-web news-worker

up-infra:
	docker-compose up -d mongodb redis minio

up-web:
	docker-compose up -d --build news-web
	docker logs -f news-web-1

run-web:
	poetry run python -m uvicorn src.api:app --host 0.0.0.0 --reload

exec-redis:
	docker exec -it news-redis-1 redis-cli -a 'test'

crawl:
	cd news_crawl/news_crawl && poetry run python main.py
