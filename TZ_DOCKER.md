# ТЕХНИЧЕСКОЕ ЗАДАНИЕ
## Vector Ray — Docker образ для переносимости

**Версия:** 1.0
**Дата:** 2026-03-24
**Статус:** На утверждении
**Планируемая реализация:** 2026-03-25 или 2026-03-26

---

## 1. Анализ текущего состояния

### Архитектура Vector Ray

```
┌─────────────────────────────────────────────────────────────┐
│                      Vector Ray Stack                        │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Vue 3 + Vite)     │  Порт 3000                  │
│  Backend (Flask + CAMEL-OASIS) │  Порт 5001                │
├─────────────────────────────────────────────────────────────┤
│  Ollama (локальные модели)    │  Порт 11434  ← НЕ в Docker │
│  Neo4j (graph database)       │  Порт 7687   ← НЕ в Docker │
└─────────────────────────────────────────────────────────────┘
```

### Текущие размеры компонентов

| Компонент | Размер | Статус в Docker |
|-----------|--------|-----------------|
| Python venv (CAMEL-OASIS + deps) | 7.7 GB | ✅ Включить |
| Node modules (Vue + Vite) | ~500 MB | ✅ Включить |
| Frontend code | ~50 MB | ✅ Включить |
| Backend code | ~50 MB | ✅ Включить |
| Ollama models | 10+ GB | ❌ Не включать |
| Neo4j data | ~1 GB | ❌ Не включать |

**Итого в Docker:** ~8.5 GB (без моделей и данных)

### Технологический стек

| Компонент | Версия | Примечания |
|-----------|--------|-----------|
| Python | 3.11+ | |
| Node.js | 18+ | |
| Flask | 3.0+ | |
| CAMEL-OASIS | 0.2.5 | |
| Neo4j driver | 5.15+ | |
| Vue | 3.5+ | |
| Vite | 7.2+ | |

---

## 2. Цели Docker образа

### Включить в образ

- ✅ Python 3.11 + все pip пакеты (CAMEL-OASIS, Flask, Neo4j driver, etc.)
- ✅ Node.js 18+ + npm пакеты (Vue 3, Vite, D3, Axios)
- ✅ Frontend (скомпилированный или в dev режиме)
- ✅ Backend (Flask приложение)
- ✅ Все shell-скрипты и конфиги
- ✅ Entrypoint для автоматического запуска

### Не включать в образ

- ❌ Ollama (должен быть на хосте)
- ❌ Neo4j (должен быть на хосте)
- ❌ Модели LLM (qwen3:8b, nomic-embed-text, etc.)
- ❌ Данные симуляций (uploads/)
- ❌ node_modules в volume (пересоздаются при сборке)

---

## 3. Структура Docker

### docker-compose.yml

```yaml
services:
  vector-ray:
    build: .
    container_name: vector-ray
    ports:
      - "3000:3000"      # Frontend
      - "5001:5001"      # Backend API
    environment:
      - FLASK_DEBUG=False
      - LLM_BASE_URL=http://host.docker.internal:11434/v1
      - NEO4J_URI=bolt://host.docker.internal:7687
      - EMBEDDING_BASE_URL=http://host.docker.internal:11434
    volumes:
      - ./uploads:/app/uploads        # Данные симуляций
      - ./logs:/app/logs             # Логи
    extra_hosts:
      - "host.docker.internal:host-gateway"
    restart: unless-stopped

networks:
  default:
    name: vector-ray-network
```

**Примечание:** `host.docker.internal` позволяет контейнеру обращаться к Ollama и Neo4j на хосте.

---

## 4. Dockerfile spec

```dockerfile
FROM python:3.11-slim

# Установка Node.js 18
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя (не root)
RUN useradd -m -s /bin/bash vector-ray

WORKDIR /app

# Копирование зависимостей
COPY backend/pyproject.toml backend/uv.lock ./
COPY frontend/package.json frontend/package-lock.json ./

# Python зависимости
RUN pip install uv
RUN uv sync --frozen

# Frontend зависимости
RUN npm ci

# Копирование исходников
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Переключаемся на пользователя
USER vector-ray

# Entrypoint
COPY docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 3000 5001

ENTRYPOINT ["/entrypoint.sh"]
CMD ["npm", "run", "dev"]
```

---

## 5. Entrypoint script

```bash
#!/bin/bash
set -e

echo "=========================================="
echo "Vector Ray Starting..."
echo "=========================================="

# Проверка Neo4j
echo "Checking Neo4j connection..."
until nc -z host.docker.internal 7687; do
  echo "Waiting for Neo4j..."
  sleep 2
done
echo "Neo4j OK"

# Проверка Ollama
echo "Checking Ollama connection..."
until nc -z host.docker.internal 11434; do
  echo "Waiting for Ollama..."
  sleep 2
done
echo "Ollama OK"

# Запуск
echo "Starting Vector Ray..."
exec "$@"
```

---

## 6. Конфигурация для нового компьютера

### .env.example для Docker

```bash
# ===== LLM Configuration (OLLAMA НА ХОСТЕ) =====
LLM_BASE_URL=http://host.docker.internal:11434/v1
LLM_MODEL_NAME=qwen3:8b

# ===== Neo4j Configuration (NEO4J НА ХОСТЕ) =====
NEO4J_URI=bolt://host.docker.internal:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=mirofish

# ===== Embedding =====
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_BASE_URL=http://host.docker.internal:11434

# ===== Flask =====
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
```

---

## 7. Инструкция по переносу

### На текущем компьютере

```bash
cd ~/projects/vector-ray

# Собрать Docker образ
docker build -t vector-ray:latest .

# Экспортировать в файл
docker save vector-ray:latest | gzip > vector-ray.tar.gz
# Размер: ~8GB

# Скопировать на внешний диск/другой компьютер
cp vector-ray.tar.gz /path/to/backup/
```

### На новом компьютере

```bash
# Установить зависимости
sudo apt install docker.io docker-compose

# Загрузить образ
docker load < vector-ray.tar.gz

# Настроить .env (указать IP хоста с Ollama/Neo4j)
nano .env

# Запустить
docker-compose up -d
```

---

## 8. Требования к новому компьютеру

| Ресурс | Минимум | Рекомендуется |
|--------|---------|---------------|
| **RAM** | 16 GB | 32 GB |
| **Диск** | 50 GB | 100 GB |
| **Ollama** | Версия 0.1+ | Последняя |
| **Neo4j** | 5.x | 5.x |
| **Docker** | 20.10+ | 24.0+ |

### Поддерживаемые ОС

| ОС | Поддержка | Примечание |
|----|-----------|------------|
| Linux (Ubuntu 20.04+) | ✅ Полная | Лучший выбор |
| macOS (Intel/Apple Silicon) | ✅ Полная | |
| Windows (WSL2) | ✅ Полная | Рекомендуется WSL2 |
| Windows (native) | ❌ | Не поддерживается |

---

## 9. Roadmap реализации

| Этап | Описание | Время |
|------|---------|-------|
| 1 | Создать Dockerfile | 30 мин |
| 2 | Создать docker-compose.yml | 15 мин |
| 3 | Написать entrypoint.sh | 15 мин |
| 4 | Тестирование локально | 30 мин |
| 5 | Экспорт и проверка на another PC | 1 час |

---

## 10. Критерии приёмки

- ✅ `docker build` завершается без ошибков
- ✅ `docker-compose up` запускает frontend и backend
- ✅ Frontend доступен на http://localhost:3000
- ✅ Backend API отвечает на http://localhost:5001/api/simulation/list
- ✅ Образ можно перенести через `docker save/load`
- ✅ При переносе на другой ПК с Ollama/Neo4j — работает без правки кода

---

## 11. Файлы для создания

| Файл | Путь | Описание |
|------|------|---------|
| Dockerfile | `./Dockerfile` | Образ контейнера |
| docker-compose.yml | `./docker-compose.yml` | Orchestration |
| docker-entrypoint.sh | `./docker-entrypoint.sh` | Startup script |
| .env.example | `./.env.example` | Пример конфигурации |

---

## 12. Known Issues

1. **FLASK_DEBUG=True** — currently set in .env, must be False for Docker
2. **semaphore=30** — may be too high for MiniMax cloud, consider reducing
3. **Path separators** — backend code uses forward slashes, Linux only

---

**Ожидание:** 2-3 часа на реализацию.
