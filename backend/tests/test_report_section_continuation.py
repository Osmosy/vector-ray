"""Раздел отчёта не должен обрываться на полуслове.

В реальном прогоне разделы 4 и 5 заканчивались так: «…списанные без подтвер» и
«…деэскалация получается частичной и замедленной: ко». Модель упиралась в лимит
вывода (4096 токенов), а обрубок уезжал в отчёт как есть.
"""

from types import SimpleNamespace

from app.services.report_agent import ReportAgent


class _ScriptedLLM:
    """LLM, который отдаёт заранее заданные ответы по очереди."""

    def __init__(self, parts):
        self.parts = list(parts)
        self.calls = 0
        self._last_finish_reason = None
        self.seen_messages = []

    def chat(self, messages=None, temperature=0.5, max_tokens=4096):
        self.seen_messages.append(list(messages or []))
        self.calls += 1
        part = self.parts.pop(0) if self.parts else None
        self._last_finish_reason = "stop"
        return part


def _agent(llm):
    agent = object.__new__(ReportAgent)
    agent.llm = llm
    return agent


def test_continuation_appends_tail_without_repeating():
    llm = _ScriptedLLM(["Февраль 2027 — фаза укоренившегося недоверия."])
    agent = _agent(llm)

    cut = "Динамика настроений: декабрь — фаза замешательства, январь — консолидация"
    llm._last_finish_reason = "length"          # как после обрыва по лимиту вывода

    result = agent._complete_answer(cut, [{"role": "user", "content": "напиши раздел"}])

    assert llm.calls == 1
    assert result.startswith(cut)
    assert result.endswith("Февраль 2027 — фаза укоренившегося недоверия.")
    assert result.count("Динамика настроений") == 1
    # в продолжение уходит сам обрывок, чтобы модель видела, откуда писать
    assert llm.seen_messages[0][-2]["content"] == cut
    assert "Продолжи" in llm.seen_messages[0][-1]["content"]


def test_long_text_without_terminal_punctuation_is_continued():
    llm = _ScriptedLLM(["конец раздела."])
    agent = _agent(llm)
    llm._last_finish_reason = "stop"

    long_cut = "Симуляция показывает, что " + ("декабрь собирает жалобы, " * 20) + "январь копит"
    result = agent._complete_answer(long_cut, [])

    assert llm.calls == 1
    assert result.endswith("конец раздела.")


def test_complete_answer_leaves_finished_text_alone():
    llm = _ScriptedLLM([])
    agent = _agent(llm)
    llm._last_finish_reason = "stop"

    text = "Раздел закончен полностью. Вывод сформулирован."
    assert agent._complete_answer(text, []) == text
    assert llm.calls == 0


def test_truncation_detected_by_finish_reason_even_on_polite_ending():
    llm = _ScriptedLLM([])
    llm._last_finish_reason = "length"
    agent = _agent(llm)

    assert agent._answer_looks_cut("Короткий, но оборванный по лимиту текст.") is True


def test_empty_continuation_keeps_original_text():
    llm = _ScriptedLLM([None])
    agent = _agent(llm)
    llm._last_finish_reason = "length"

    text = "Раздел, который модель оборвала на лимите"
    assert agent._complete_answer(text, []) == text
    assert llm.calls == 1
