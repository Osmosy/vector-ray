"""Симулированное время прогона: с какого часа он начинается.

Прогон всегда стартовал в 00:00 симулированных суток. У агентов есть
``active_hours`` (обычно 7–23), поэтому короткий прогон — например максимум
5 раундов по часу — целиком попадал в ночь: каждый раунд пропускался молча,
и симуляция завершалась «успешно» без единого действия агентов. Ноль постов,
ноль споров, отчёт по пустой сцене.

Час начала берётся из ``time_config.start_hour``, иначе — первый пиковый час
из конфигурации, иначе 8 утра.
"""

from typing import Any, Dict

DEFAULT_START_HOUR = 8


def resolve_start_hour(time_config: Dict[str, Any]) -> int:
    """Вернуть час (0–23), с которого начинается симулированное время."""
    explicit = time_config.get("start_hour")
    if isinstance(explicit, int) and 0 <= explicit <= 23:
        return explicit

    peaks = [
        hour for hour in (time_config.get("peak_hours") or [])
        if isinstance(hour, int) and 0 <= hour <= 23
    ]
    if peaks:
        return min(peaks)

    return DEFAULT_START_HOUR
