# computers_api
Implementations REST API Service For Computers NoSQL database

## Запуск сервиса:

```bash
docker-compose up
```

## Файл конфигурации

Для быстрого изменения хоста и порта, на котором работает сервер cassandra, сделать JSON файл конфигурации conf.json.

```json
{
    "cassandra" : {
	    "host" : "cassandra",
	    "port" : "9042"
    }
}
```