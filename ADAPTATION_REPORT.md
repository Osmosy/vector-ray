# Анализ проекта MiroFish-Offline для адаптации в Vector Ray

**Дата:** 2026-03-19
**Цель:** Русификация интерфейса, переименование в Vector Ray, адаптация под OpenRouter

---

## 1. Файлы с упоминаниями MiroFish (требуют переименования)

### Backend Python (Высокий приоритет)
| Файл | Строк | Комментарий |
|------|-------|-------------|
| `backend/app/utils/logger.py` | ~50 | Логирование |
| `backend/app/utils/retry.py` | ~30 | Retry логика |
| `backend/app/storage/*.py` | ~500 | Neo4j, embeddings, search |
| `backend/pyproject.toml` | ~30 | Зависимости |
| `backend/requirements.txt` | ~30 | Зависимости |

### Frontend Vue.js (Высокий приоритет)
| Файл | Строк | Комментарий |
|------|-------|-------------|
| `frontend/src/views/Home.vue` | ~100 | Главная страница |
| `frontend/src/views/MainView.vue` | ~150 | Основной вид |
| `frontend/src/views/Process.vue` | ~200 | Процесс |
| `frontend/src/views/SimulationView.vue` | ~300 | Симуляция |
| `frontend/src/views/ReportView.vue` | ~200 | Отчёты |
| `frontend/src/views/InteractionView.vue` | ~150 | Взаимодействие |
| `frontend/src/views/SimulationRunView.vue` | ~250 | Запуск симуляции |
| `frontend/src/components/*.vue` | ~800 | Компоненты |
| `frontend/index.html` | ~50 | HTML |

### Конфигурация (Средний приоритет)
| Файл | Строк | Комментарий |
|------|-------|-------------|
| `docker-compose.yml` | ~50 | Docker |
| `package.json` | ~30 | NPM |
| `package-lock.json` | ~300 | NPM lock |
| `.env.example` | ~50 | Пример конфига |

### Документация (Низкий приоритет)
| Файл | Строк | Комментарий |
|------|-------|-------------|
| `README.md` | ~300 | Документация |
| `ROADMAP.md` | ~100 | Roadmap |
| `docs/progress.md` | ~50 | Прогресс |

---

## 2. Файлы с китайскими символами (требуют перевода)

### Критические (требуют перевода)
| Файл | Тип | Приоритет |
|------|-----|-----------|
| `backend/pyproject.toml` | Конфигурация | Высокий |
| `backend/requirements.txt` | Зависимости | Высокий |
| `Dockerfile` | Docker | Средний |
| `frontend/CHINESE_TEXT_INVENTORY.md` | Документация | Низкий |

### Изображения (не требуют перевода)
| Файл | Тип |
|------|-----|
| `static/image/Screenshot/*.png` | Скриншоты |
| `static/image/mirofish-*.jpg` | Логотипы |
| `frontend/src/assets/logo/*.jpeg` | Логотипы |

---

## 3. Frontend компоненты (Vue.js + TypeScript)

### Views (7 файлов)
- `Home.vue` — Главная страница
- `MainView.vue` — Основной интерфейс
- `Process.vue` — Процесс работы
- `SimulationView.vue` — Просмотр симуляции
- `SimulationRunView.vue` — Запуск симуляции
- `ReportView.vue` — Отчёты
- `InteractionView.vue` — Взаимодействие с агентами

### Components (6 файлов)
- `Step1GraphBuild.vue` — Построение графа
- `Step2EnvSetup.vue` — Настройка окружения
- `Step3Simulation.vue` — Симуляция
- `Step4Report.vue` — Генерация отчёта
- `Step5Interaction.vue` — Взаимодействие
- `GraphPanel.vue` — Панель графа
- `HistoryDatabase.vue` — История

---

## 4. Backend Python файлы

### Storage (5 файлов)
- `neo4j_storage.py` — Хранилище Neo4j (~400 строк)
- `neo4j_schema.py` — Схема БД (~100 строк)
- `search_service.py` — Hybrid search (~200 строк)
- `embedding_service.py` — Эмбеддинги (~150 строк)
- `ner_extractor.py` — NER extraction (~100 строк)

### Utils (4 файла)
- `llm_client.py` — LLM клиент (~100 строк)
- `logger.py` — Логирование (~50 строк)
- `file_parser.py` — Парсер файлов (~80 строк)
- `retry.py` — Retry логика (~30 строк)

### Models (2 файла)
- `task.py` — Модель задачи (~50 строк)
- `project.py` — Модель проекта (~80 строк)

### Scripts (4 файла)
- `run_twitter_simulation.py` — Twitter симуляция
- `run_reddit_simulation.py` — Reddit симуляция
- `run_parallel_simulation.py` — Параллельная симуляция
- `action_logger.py` — Логирование действий

---

## 5. Архитектурные проблемы

### Критическая проблема
**Neo4j НЕ поддерживает векторный поиск по relationships:**
- Код использует `db.index.vector.queryRelationships` — несуществующая процедура
- Только `db.index.vector.queryNodes` работает

### Решения:
1. **Вариант A:** Edges как Nodes (высокая сложность)
2. **Вариант B:** Hybrid — vector для nodes, BM25 для edges (низкая сложность)
3. **Вариант C:** Qdrant + Neo4j (средняя сложность)

---

## 6. Оценка объёма работ

| Категория | Файлов | Строк | Приоритет | Время |
|-----------|--------|-------|-----------|-------|
| Backend Python | 20 | ~1500 | Высокий | 4-6ч |
| Frontend Vue.js | 15 | ~2000 | Высокий | 6-8ч |
| Конфигурация | 4 | ~400 | Средний | 1-2ч |
| Документация | 3 | ~500 | Низкий | 1-2ч |
| Архитектура | 1 | — | Критический | 2-4ч |
| **Итого** | **43** | ~4400 | — | **15-22ч** |

---

## 7. Порядок действий

### Фаза 1: Подготовка (1 час)
1. Создать резервную копию проекта
2. Инициализировать git репозиторий
3. Создать ветку `feature/vector-ray-russian`

### Фаза 2: Массовая замена (2 часа)
```bash
# Переименование MiroFish → Vector Ray
find . -type f \( -name "*.py" -o -name "*.vue" -o -name "*.ts" \) \
  -exec sed -i 's/MiroFish/Vector Ray/g' {} \;
find . -type f \( -name "*.py" -o -name "*.vue" -o -name "*.ts" \) \
  -exec sed -i 's/mirofish/vector-ray/g' {} \;
```

### Фаза 3: Русификация (8-10 часов)
- Перевод UI компонентов
- Перевод логов и ошибок
- Перевод документации

### Фаза 4: Архитектурные исправления (2-4 часа)
- Исправление Neo4j векторного поиска
- Интеграция OpenRouter fallback

### Фаза 5: Тестирование (2-3 часа)
- Unit тесты
- Integration тесты
- E2E тесты

---

## 8. Следующий шаг

Требуется подтверждение для начала работ:
1. Какой вариант решения для Neo4j vector search? (A, B или C)
2. Начинать с Фазы 1?