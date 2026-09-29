# Быстрый деплой на VPS

Нужен любой VPS с Ubuntu 22.04/24.04 и публичным IPv4. На сервере должны быть установлены Git и Docker.

## 1. Запуск на сервере

```bash
git clone <URL-репозитория> bacteries
cd bacteries
docker compose up -d --build
```

Проверить запуск:

```bash
docker compose ps
docker compose logs -f server
```

В логе должна появиться строка `сервер слушает 0.0.0.0:22867`.

Если на VPS включён UFW, открыть TCP-порт:

```bash
sudo ufw allow 22867/tcp
```

Такой же TCP-порт нужно разрешить в firewall/security group хостинга, если он есть.

## 2. Запуск клиента на своём компьютере

Linux/macOS:

```bash
python3 -m pip install -r requirements.txt
BACTERIES_HOST=<IP-сервера> python3 client.py
```

Windows PowerShell:

```powershell
py -m pip install -r requirements.txt
$env:BACTERIES_HOST="<IP-сервера>"
py client.py
```

## Обновление

```bash
cd bacteries
git pull
docker compose up -d --build
```

## Остановка

```bash
docker compose down
```

Данные SQLite живут в Docker volume `bacteries-data` и не удаляются при обычном `docker compose down`.
