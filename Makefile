.PHONY: bot-compose-up
bot-compose-up:
	docker compose up -d --build

.PHONY: bot-compose-down
bot-compose-down:
	docker compose down --remove-orphans

.PHONY: chat-compose-up
chat-compose-up:
	docker compose -f chat_infrastructure/docker-compose.yml up -d --build

.PHONY: chat-compose-down
chat-compose-down:
	docker compose -f chat_infrastructure/docker-compose.yml down --remove-orphans

.PHONY: load-chat-dump
load-chat-dump:
	docker cp ./dump chat_infrastructure-mongodb-1:/dump
	docker exec -it chat_infrastructure-mongodb-1 mongorestore --drop /dump
