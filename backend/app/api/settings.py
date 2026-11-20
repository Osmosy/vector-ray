"""
Settings API Module
"""

from flask import Blueprint, jsonify, request
import os
from pathlib import Path

settings_bp = Blueprint('settings', __name__)

ENV_FILE = Path(__file__).parent.parent.parent.parent / '.env'

# Default settings
DEFAULT_SETTINGS = {
    'llmApiKey': '',
    'llmProvider': 'ollama',
    'llmModel': 'qwen3:8b',
    'llmBaseUrl': 'http://localhost:11434/v1',
    'embeddingModel': 'nomic-embed-text',
    'embeddingBaseUrl': 'http://localhost:11434',
    'neo4jUri': 'bolt://localhost:7687',
    'neo4jUser': 'neo4j',
    'neo4jPassword': '',
    # Параметры симуляции
    'testMode': True,
    'maxAgents': 5,
    'maxRounds': 5,
    'minutesPerRound': 1,
    # Параметры отчётов
    'reportTemperature': 0.5,
    'maxToolCalls': 5,
    'maxReflectionRounds': 2,
}

def load_env_settings():
    """Load settings from .env file"""
    settings = DEFAULT_SETTINGS.copy()
    
    # Map env vars to settings
    env_mapping = {
        'LLM_API_KEY': 'llmApiKey',
        'LLM_MODEL_NAME': 'llmModel',
        'LLM_BASE_URL': 'llmBaseUrl',
        'EMBEDDING_MODEL': 'embeddingModel',
        'EMBEDDING_BASE_URL': 'embeddingBaseUrl',
        'NEO4J_URI': 'neo4jUri',
        'NEO4J_USER': 'neo4jUser',
        'NEO4J_PASSWORD': 'neo4jPassword',
        # Параметры симуляции
        'VECTOR_RAY_TEST_MODE': 'testMode',
        'VECTOR_RAY_MAX_AGENTS': 'maxAgents',
        'OASIS_DEFAULT_MAX_ROUNDS': 'maxRounds',
        'VECTOR_RAY_MINUTES_PER_ROUND': 'minutesPerRound',
        # Параметры отчётов
        'REPORT_AGENT_TEMPERATURE': 'reportTemperature',
        'REPORT_AGENT_MAX_TOOL_CALLS': 'maxToolCalls',
        'REPORT_AGENT_MAX_REFLECTION_ROUNDS': 'maxReflectionRounds',
    }
    
    # Read from current env
    for env_key, setting_key in env_mapping.items():
        value = os.environ.get(env_key)
        if value:
            # Конвертация типов
            if setting_key in ('testMode',):
                settings[setting_key] = value.lower() in ('true', '1', 'yes')
            elif setting_key in ('maxAgents', 'maxRounds', 'maxToolCalls', 'maxReflectionRounds', 'minutesPerRound'):
                settings[setting_key] = int(value)
            elif setting_key in ('reportTemperature',):
                settings[setting_key] = float(value)
            else:
                settings[setting_key] = value
    
    # Determine provider
    if 'openrouter' in settings['llmBaseUrl'].lower():
        settings['llmProvider'] = 'openrouter'
    else:
        settings['llmProvider'] = 'ollama'
    
    return settings


@settings_bp.route('/settings', methods=['GET'])
def get_settings():
    """Get current settings"""
    settings = load_env_settings()
    return jsonify({'data': settings})


@settings_bp.route('/settings', methods=['POST'])
def save_settings():
    """Save settings to .env file"""
    try:
        data = request.get_json()
        
        # Read existing .env
        env_content = ''
        if ENV_FILE.exists():
            env_content = ENV_FILE.read_text()
        
        # Map settings to env vars
        env_mapping = {
            'llmApiKey': 'LLM_API_KEY',
            'llmModel': 'LLM_MODEL_NAME',
            'llmBaseUrl': 'LLM_BASE_URL',
            'embeddingModel': 'EMBEDDING_MODEL',
            'embeddingBaseUrl': 'EMBEDDING_BASE_URL',
            'neo4jUri': 'NEO4J_URI',
            'neo4jUser': 'NEO4J_USER',
            'neo4jPassword': 'NEO4J_PASSWORD',
            # Параметры симуляции
            'testMode': 'VECTOR_RAY_TEST_MODE',
            'maxAgents': 'VECTOR_RAY_MAX_AGENTS',
            'maxRounds': 'OASIS_DEFAULT_MAX_ROUNDS',
            'minutesPerRound': 'VECTOR_RAY_MINUTES_PER_ROUND',
            # Параметры отчётов
            'reportTemperature': 'REPORT_AGENT_TEMPERATURE',
            'maxToolCalls': 'REPORT_AGENT_MAX_TOOL_CALLS',
            'maxReflectionRounds': 'REPORT_AGENT_MAX_REFLECTION_ROUNDS',
        }
        
        lines = env_content.split('\n')
        updated_keys = set()
        
        # Update existing lines
        for i, line in enumerate(lines):
            for setting_key, env_key in env_mapping.items():
                if setting_key in data:
                    if line.startswith(f'{env_key}='):
                        # Конвертация boolean
                        if isinstance(data[setting_key], bool):
                            lines[i] = f'{env_key}={"true" if data[setting_key] else "false"}'
                        else:
                            lines[i] = f'{env_key}={data[setting_key]}'
                        updated_keys.add(env_key)
        
        # Add new lines for missing keys
        for setting_key, env_key in env_mapping.items():
            if setting_key in data and env_key not in updated_keys:
                if isinstance(data[setting_key], bool):
                    lines.append(f'{env_key}={"true" if data[setting_key] else "false"}')
                else:
                    lines.append(f'{env_key}={data[setting_key]}')
        
        # Write back
        ENV_FILE.write_text('\n'.join(lines))
        
        # Update current process env
        for setting_key, env_key in env_mapping.items():
            if setting_key in data:
                os.environ[env_key] = str(data[setting_key])
        
        return jsonify({'status': 'ok', 'message': 'Настройки сохранены'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@settings_bp.route('/settings/presets', methods=['GET'])
def get_presets():
    """Get available presets"""
    presets = {
        'test': {
            'name': 'Тестовый',
            'desc': 'Быстрое тестирование',
            'settings': {
                'testMode': True,
                'maxAgents': 5,
                'maxRounds': 5,
                'minutesPerRound': 1,
            }
        },
        'standard': {
            'name': 'Стандартный',
            'desc': 'Базовая симуляция',
            'settings': {
                'testMode': False,
                'maxAgents': 50,
                'maxRounds': 40,
                'minutesPerRound': 2,
            }
        },
        'extended': {
            'name': 'Расширенный',
            'desc': 'Детальная симуляция',
            'settings': {
                'testMode': False,
                'maxAgents': 100,
                'maxRounds': 60,
                'minutesPerRound': 3,
            }
        },
        'maximum': {
            'name': 'Максимальный',
            'desc': 'Полная симуляция',
            'settings': {
                'testMode': False,
                'maxAgents': 200,
                'maxRounds': 100,
                'minutesPerRound': 5,
            }
        }
    }
    return jsonify({'presets': presets})


@settings_bp.route('/settings/presets/<preset_id>', methods=['POST'])
def apply_preset(preset_id):
    """Apply a preset and save to .env"""
    presets_data = {
        'test': {
            'testMode': True,
            'maxAgents': 5,
            'maxRounds': 5,
            'minutesPerRound': 1,
        },
        'standard': {
            'testMode': False,
            'maxAgents': 50,
            'maxRounds': 40,
            'minutesPerRound': 2,
        },
        'extended': {
            'testMode': False,
            'maxAgents': 100,
            'maxRounds': 60,
            'minutesPerRound': 3,
        },
        'maximum': {
            'testMode': False,
            'maxAgents': 200,
            'maxRounds': 100,
            'minutesPerRound': 5,
        }
    }
    
    if preset_id not in presets_data:
        return jsonify({'status': 'error', 'message': f'Пресет "{preset_id}" не найден'}), 404
    
    # Сохраняем пресет в .env через существующую логику
    request_data = presets_data[preset_id]
    
    # Read existing .env
    env_content = ''
    if ENV_FILE.exists():
        env_content = ENV_FILE.read_text()
    
    env_mapping = {
        'testMode': 'VECTOR_RAY_TEST_MODE',
        'maxAgents': 'VECTOR_RAY_MAX_AGENTS',
        'maxRounds': 'OASIS_DEFAULT_MAX_ROUNDS',
        'minutesPerRound': 'VECTOR_RAY_MINUTES_PER_ROUND',
    }
    
    lines = env_content.split('\n')
    updated_keys = set()
    
    for i, line in enumerate(lines):
        for setting_key, env_key in env_mapping.items():
            if setting_key in request_data:
                if line.startswith(f'{env_key}='):
                    if isinstance(request_data[setting_key], bool):
                        lines[i] = f'{env_key}={"true" if request_data[setting_key] else "false"}'
                    else:
                        lines[i] = f'{env_key}={request_data[setting_key]}'
                    updated_keys.add(env_key)
    
    for setting_key, env_key in env_mapping.items():
        if setting_key in request_data and env_key not in updated_keys:
            if isinstance(request_data[setting_key], bool):
                lines.append(f'{env_key}={"true" if request_data[setting_key] else "false"}')
            else:
                lines.append(f'{env_key}={request_data[setting_key]}')
    
    ENV_FILE.write_text('\n'.join(lines))
    
    # Update current process env
    for setting_key, env_key in env_mapping.items():
        if setting_key in request_data:
            os.environ[env_key] = str(request_data[setting_key])
    
    return jsonify({'status': 'ok', 'message': f'Пресет "{preset_id}" применён', 'settings': request_data})