.PHONY: backend tunnel test config-check docker-up docker-down

backend:
	python run_backend.py

tunnel:
	npx -y cloudflared tunnel --url http://localhost:8001

test:
	pytest tests/ -q

config-check:
	python scripts/check_config.py

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down
