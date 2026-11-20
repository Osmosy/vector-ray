"""Думающая модель не должна молча отдавать пустой ответ.

При max_tokens=4096 рассуждающая модель тратит весь бюджет на размышления,
возвращает finish_reason='length' и пустой content. Наверху это превращалось
в «Invalid JSON format from LLM:» — без единого намёка на причину.
"""

from types import SimpleNamespace

from app.utils.llm_client import LLMClient


def _response(content: str, finish_reason: str):
    return SimpleNamespace(
        choices=[SimpleNamespace(
            finish_reason=finish_reason,
            message=SimpleNamespace(content=content),
        )]
    )


class _Scripted:
    """Отдаёт заранее заданные ответы и запоминает бюджеты запросов."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.budgets = []

    def __call__(self, **kwargs):
        self.budgets.append(kwargs["max_tokens"])
        return self._responses.pop(0)


def _client(scripted):
    client = LLMClient(api_key="k", base_url="http://localhost:11434/v1", model="m")
    client.client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=scripted))
    )
    return client


def test_empty_answer_after_reasoning_budget_is_retried_with_more_tokens():
    scripted = _Scripted([
        _response("", "length"),
        _response('{"ok": true}', "stop"),
    ])
    client = _client(scripted)

    result = client.chat_json([{"role": "user", "content": "дай JSON"}], max_tokens=4096)

    assert result == {"ok": True}
    assert scripted.budgets == [4096, 12288], "повтор должен идти с запасом втрое"


def test_second_empty_answer_raises_a_readable_error():
    scripted = _Scripted([
        _response("", "length"),
        _response("", "length"),
    ])
    client = _client(scripted)

    try:
        client.chat_json([{"role": "user", "content": "дай JSON"}], max_tokens=4096)
    except Exception as exc:
        message = str(exc)
        assert "finish_reason=length" in message
        assert "12288" in message
    else:
        raise AssertionError("ожидалась ошибка о нехватке бюджета")


def test_normal_answer_is_not_retried():
    scripted = _Scripted([_response('{"ok": true}', "stop")])
    client = _client(scripted)

    assert client.chat_json([{"role": "user", "content": "дай JSON"}]) == {"ok": True}
    assert scripted.budgets == [4096]


def test_json_in_markdown_fence_is_parsed():
    scripted = _Scripted([_response('```json\n{"ok": true}\n```', "stop")])
    client = _client(scripted)

    assert client.chat_json([{"role": "user", "content": "дай JSON"}]) == {"ok": True}
