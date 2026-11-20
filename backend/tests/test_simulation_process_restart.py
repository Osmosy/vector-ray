"""Принудительный перезапуск должен гасить процесс, оставшийся в режиме ожидания.

После завершения раундов подпроцесс OASIS живёт дальше (для интервью), а статус
в run_state уже «completed». Перезапуск с force=true смотрел только на статус,
не видел живой процесс и запускал второй рядом. Два процесса по очереди писали
в actions.jsonl: лог превращался в мусор, чтение падало с UnicodeDecodeError,
и прогресс симуляции переставал обновляться.
"""

import subprocess
import sys

from app.services.simulation_runner import SimulationRunner


def _spawn_sleeper() -> subprocess.Popen:
    return subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(60)"],
        start_new_session=True,
    )


def test_wait_mode_process_is_detected_regardless_of_status():
    simulation_id = "sim_test_wait_mode"
    process = _spawn_sleeper()
    try:
        SimulationRunner._processes[simulation_id] = process
        assert SimulationRunner.has_live_process(simulation_id) is True

        assert SimulationRunner.terminate_live_process(simulation_id) is True
        assert process.poll() is not None, "процесс должен быть погашен"
        assert SimulationRunner.has_live_process(simulation_id) is False
    finally:
        SimulationRunner._processes.pop(simulation_id, None)
        if process.poll() is None:
            process.kill()


def test_absent_process_is_not_an_error():
    assert SimulationRunner.terminate_live_process("sim_does_not_exist") is False


def test_finished_process_is_not_treated_as_live():
    simulation_id = "sim_test_finished"
    process = subprocess.Popen([sys.executable, "-c", "pass"], start_new_session=True)
    process.wait(timeout=30)
    try:
        SimulationRunner._processes[simulation_id] = process
        assert SimulationRunner.has_live_process(simulation_id) is False
        assert SimulationRunner.terminate_live_process(simulation_id) is False
    finally:
        SimulationRunner._processes.pop(simulation_id, None)
