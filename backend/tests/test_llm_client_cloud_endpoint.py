"""Резервная цепочка моделей не должна срабатывать на облачном эндпоинте.

Цепочка MODEL_CASCADE — это локальные имена Ollama (qwen3:8b, qwen2.5:7b,
llama3.2). Если базовый URL указывает на облачного провайдера, подстановка этих
имён даёт не «второй шанс», а серию заведомо провальных запросов и маскирует
настоящую ошибку сообщением «All models in cascade failed».
"""

from types import SimpleNamespace

import pytest

from app.utils.llm_client import LLMClient


class _Recorder:
    """Подменяет chat.completions.create и запоминает запрошенные модели."""

    def __init__(self, fail: bool = True):
        self.models = []
        self._fail = fail

    def __call__(self, **kwargs):
        self.models.append(kwargs["model"])
        if self._fail:
            raise RuntimeError("upstream 400: unknown model")
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="готово"))]
        )


def _client_with(recorder: _Recorder, base_url: str, model: str) -> LLMClient:
    client = LLMClient(api_key="test", base_url=base_url, model=model)
    client.client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=recorder))
    )
    return client


def test_cloud_endpoint_reports_the_real_error_without_local_fallbacks():
    recorder = _Recorder()
    client = _client_with(recorder, "https://api.example.com/v1", "cloud-model")

    with pytest.raises(Exception) as exc:
        client.chat([{"role": "user", "content": "привет"}])

    assert recorder.models == ["cloud-model"], "к облаку нельзя подставлять локальные имена"
    message = str(exc.value)
    assert "cloud-model" in message
    assert "unknown model" in message, "исходная ошибка провайдера должна сохраниться"
    assert "cascade" not in message.lower()


def test_cloud_endpoint_keeps_its_model_on_reset():
    recorder = _Recorder(fail=False)
    client = _client_with(recorder, "https://api.example.com/v1", "cloud-model")

    client.reset_to_primary()

    assert client.model == "cloud-model"


def test_local_ollama_still_falls_back_through_the_cascade():
    recorder = _Recorder()
    client = _client_with(recorder, "http://localhost:11434/v1", "qwen3:8b")

    with pytest.raises(Exception):
        client.chat([{"role": "user", "content": "привет"}])

    assert recorder.models[0] == "qwen3:8b"
    assert len(recorder.models) > 1, "локальная цепочка резерва должна сохраниться"
    assert recorder.models[1] == "qwen2.5:7b"
