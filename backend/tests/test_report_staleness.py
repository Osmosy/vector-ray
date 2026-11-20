"""Отчёт не должен молча отдаваться после перезапуска симуляции.

Перезапуск не удаляет отчёт, а `/api/report/generate` возвращал его как «готовый»:
пользователь получал текст по предыдущему прогону, без предупреждения. И
`/generate/status` с одним simulation_id отвечал completed, пока новый текст ещё
писался.
"""

from types import SimpleNamespace

from app.api.report import _report_is_stale


def _report(stamp):
    return SimpleNamespace(report_id="report_x", created_at=stamp, completed_at=stamp)


def _state(stamp, simulation_id="sim_stale_test"):
    return SimpleNamespace(updated_at=stamp, simulation_id=simulation_id)


def test_report_newer_than_run_is_fresh():
    assert _report_is_stale(_report("2026-11-20T16:12:00"), _state("2026-11-20T15:58:00")) is False


def test_report_older_than_run_is_stale():
    assert _report_is_stale(_report("2026-11-20T14:50:00"), _state("2026-11-20T15:58:00")) is True


def test_report_without_timestamps_is_treated_as_fresh():
    report = SimpleNamespace(report_id="report_x", created_at=None, completed_at=None)
    assert _report_is_stale(report, _state("2026-11-20T15:58:00")) is False


def test_unknown_simulation_falls_back_to_state_stamp():
    # get_run_state для несуществующей симуляции вернёт None — сравнение идёт по state
    assert _report_is_stale(_report("2026-11-20T10:00:00"), _state("2026-11-20T11:00:00", "sim_nope")) is True
