<template>
  <div class="settings-page">
    <!-- Navbar -->
    <nav class="navbar">
      <button class="btn-back" @click="goBack">
        <span class="btn-icon">←</span>
        <span class="btn-text">Назад</span>
      </button>
      <div class="nav-center">
        <span class="page-title">Настройки</span>
      </div>
      <div class="nav-status">
        <span class="status-badge" :class="saveStatus">{{ saveStatusText }}</span>
      </div>
    </nav>

    <div class="settings-content">
      <!-- Режим тестирования -->
      <section class="settings-section">
        <div class="section-header">
          <h2>🧪 Режим тестирования</h2>
          <span class="section-badge" :class="{ active: settings.testMode }">
            {{ settings.testMode ? 'Включён' : 'Выключен' }}
          </span>
        </div>
        <p class="section-desc">
          Ускоренный режим для быстрого тестирования. Уменьшает количество агентов и раундов симуляции.
        </p>
        
        <div class="setting-item">
          <label class="toggle-label">
            <input type="checkbox" v-model="settings.testMode">
            <span class="toggle-switch"></span>
            <span class="toggle-text">Быстрое тестирование</span>
          </label>
          <p class="setting-hint">Симуляция завершится за 1-2 минуты с минимальным количеством агентов</p>
        </div>

        <div class="test-mode-info" v-if="settings.testMode">
          <div class="info-card">
            <h4>📋 Параметры тестового режима</h4>
            <ul>
              <li>Агентов: <strong>3-5</strong> (вместо 50-100)</li>
              <li>Раундов: <strong>5</strong> (вместо 40-72)</li>
              <li>Время симуляции: <strong>~1 минута</strong></li>
              <li>Генерация отчёта: <strong>~30 сек</strong></li>
            </ul>
          </div>
        </div>
      </section>

      <!-- Пресеты -->
      <section class="settings-section">
        <div class="section-header">
          <h2>📋 Пресеты</h2>
        </div>
        <p class="section-desc">
          Быстрый выбор готовых конфигураций для разных сценариев.
        </p>
        
        <div class="presets-grid">
          <button 
            v-for="preset in presets" 
            :key="preset.id"
            class="preset-card" 
            :class="{ active: activePreset === preset.id }"
            @click="applyPreset(preset.id)"
          >
            <span class="preset-name">{{ preset.name }}</span>
            <span class="preset-desc">{{ preset.desc }}</span>
            <span class="preset-stats">{{ preset.stats }}</span>
          </button>
        </div>
      </section>

      <!-- Параметры симуляции -->
      <section class="settings-section">
        <div class="section-header">
          <h2>⚙️ Параметры симуляции</h2>
        </div>
        
        <div class="setting-group">
          <div class="setting-item">
            <label class="setting-label">
              <span class="label-text">Максимум агентов</span>
              <span class="label-value">{{ settings.maxAgents }}</span>
            </label>
            <input 
              type="range" 
              :min="testModeValues.agents.min" 
              :max="testModeValues.agents.max" 
              v-model="settings.maxAgents"
              :disabled="settings.testMode"
            >
            <div v-if="settings.testMode" class="setting-locked">
              🔒 Заблокировано тестовым режимом
            </div>
          </div>

          <div class="setting-item">
            <label class="setting-label">
              <span class="label-text">Максимум раундов</span>
              <span class="label-value">{{ settings.maxRounds }}</span>
            </label>
            <input 
              type="range" 
              :min="testModeValues.rounds.min" 
              :max="testModeValues.rounds.max" 
              v-model="settings.maxRounds"
              :disabled="settings.testMode"
            >
            <div v-if="settings.testMode" class="setting-locked">
              🔒 Заблокировано тестовым режимом
            </div>
          </div>

          <div class="setting-item">
            <label class="setting-label">
              <span class="label-text">Минут на раунд</span>
              <span class="label-value">{{ settings.minutesPerRound }}</span>
            </label>
            <input 
              type="range" 
              :min="testModeValues.minutes.min" 
              :max="testModeValues.minutes.max" 
              v-model="settings.minutesPerRound"
              :disabled="settings.testMode"
            >
            <div v-if="settings.testMode" class="setting-locked">
              🔒 Заблокировано тестовым режимом
            </div>
          </div>
        </div>
      </section>

      <!-- LLM модель -->
      <section class="settings-section">
        <div class="section-header">
          <h2>🤖 LLM модель</h2>
        </div>
        
        <div class="setting-item model-select">
          <label class="setting-label">Выбор модели</label>
          <div class="model-options">
            <label 
              v-for="model in availableModels" 
              :key="model.id"
              class="model-option"
              :class="{ selected: settings.llmModel === model.id }"
            >
              <input 
                type="radio" 
                :value="model.id" 
                v-model="settings.llmModel"
                @change="onModelChange"
              >
              <div class="model-card">
                <span class="model-name">{{ model.name }}</span>
                <span class="model-size">{{ model.size }}</span>
                <span class="model-type">{{ model.type }}</span>
              </div>
            </label>
          </div>
        </div>

        <div class="setting-item">
          <label class="setting-label">Ollama URL</label>
          <input 
            type="text" 
            class="text-input" 
            v-model="settings.llmBaseUrl"
            placeholder="http://localhost:11434/v1"
          >
          <p class="setting-hint">
            URL сервера Ollama для генерации онтологии и отчётов
          </p>
        </div>
      </section>

      <!-- Graphiti / Neo4j -->
      <section class="settings-section">
        <div class="section-header">
          <h2>🗃️ База данных</h2>
        </div>
        
        <div class="setting-item">
          <label class="setting-label">Neo4j URI</label>
          <input 
            type="text" 
            class="text-input" 
            v-model="settings.neo4jUri"
            placeholder="bolt://localhost:7687"
          >
        </div>
        
        <div class="setting-group inline">
          <div class="setting-item">
            <label class="setting-label">Пользователь</label>
            <input 
              type="text" 
              class="text-input" 
              v-model="settings.neo4jUser"
              placeholder="neo4j"
            >
          </div>
          <div class="setting-item">
            <label class="setting-label">Пароль</label>
            <input 
              type="password" 
              class="text-input" 
              v-model="settings.neo4jPassword"
              placeholder="••••••••"
            >
          </div>
        </div>

        <div class="db-status" :class="{ connected: neo4jConnected }">
          <span class="status-icon">{{ neo4jConnected ? '✓' : '✗' }}</span>
          <span>{{ neo4jConnected ? 'Подключено к Neo4j' : 'Не подключено к Neo4j' }}</span>
        </div>
      </section>

      <!-- Кнопки действий -->
      <div class="settings-actions">
        <button class="btn-primary" @click="saveSettings" :disabled="saving">
          <span class="btn-icon">✓</span>
          {{ saving ? 'Сохранение...' : 'Сохранить настройки' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const settings = ref({
  testMode: true,
  maxAgents: 5,
  maxRounds: 5,
  minutesPerRound: 1,
  llmModel: 'qwen3:8b',
  llmBaseUrl: 'http://localhost:11434/v1',
  neo4jUri: 'bolt://localhost:7687',
  neo4jUser: 'neo4j',
  neo4jPassword: '',
})

const saving = ref(false)
const hasChanges = ref(false)
const neo4jConnected = ref(false)
const activePreset = ref('test')

const saveStatus = computed(() => {
  if (saving.value) return 'saving'
  return hasChanges.value ? 'pending' : 'saved'
})

const saveStatusText = computed(() => {
  if (saving.value) return 'Сохранение...'
  return hasChanges.value ? 'Не сохранено' : 'Сохранено'
})

// Динамические лимиты для слайдеров в зависимости от режима
const testModeValues = computed(() => {
  if (settings.value.testMode) {
    return {
      agents: { min: 3, max: 10 },
      rounds: { min: 3, max: 10 },
      minutes: { min: 1, max: 5 }
    }
  }
  return {
    agents: { min: 10, max: 200 },
    rounds: { min: 10, max: 100 },
    minutes: { min: 1, max: 10 }
  }
})

// Доступные модели
const availableModels = [
  { id: 'qwen3:8b', name: 'Qwen 3 8B', size: '5.2 GB', type: 'Локальная' },
  { id: 'qwen2.5:7b', name: 'Qwen 2.5 7B', size: '4.7 GB', type: 'Локальная' },
  { id: 'glm-4-flash', name: 'GLM-4 Flash', size: 'Cloud', type: 'Облачная' },
  { id: 'gemini-3-flash', name: 'Gemini 3 Flash', size: 'Cloud', type: 'Облачная' },
]

// Пресеты
const presets = [
  { 
    id: 'test', 
    name: 'Тестовый', 
    desc: 'Быстрое тестирование', 
    stats: '5 агентов · 5 раундов' 
  },
  { 
    id: 'standard', 
    name: 'Стандартный', 
    desc: 'Базовая симуляция', 
    stats: '50 агентов · 40 раундов' 
  },
  { 
    id: 'extended', 
    name: 'Расширенный', 
    desc: 'Детальная симуляция', 
    stats: '100 агентов · 60 раундов' 
  },
  { 
    id: 'maximum', 
    name: 'Максимальный', 
    desc: 'Полная симуляция', 
    stats: '200 агентов · 100 раундов' 
  },
]

const presetConfigs = {
  test: { testMode: true, maxAgents: 5, maxRounds: 5, minutesPerRound: 1 },
  standard: { testMode: false, maxAgents: 50, maxRounds: 40, minutesPerRound: 2 },
  extended: { testMode: false, maxAgents: 100, maxRounds: 60, minutesPerRound: 3 },
  maximum: { testMode: false, maxAgents: 200, maxRounds: 100, minutesPerRound: 5 },
}

const applyPreset = (presetId) => {
  activePreset.value = presetId
  const config = presetConfigs[presetId]
  if (config) {
    Object.assign(settings.value, config)
    hasChanges.value = true
  }
}

const onModelChange = () => {
  hasChanges.value = true
  // Автоматическая настройка URL для облачных моделей
  if (settings.value.llmModel === 'glm-4-flash') {
    settings.value.llmBaseUrl = 'https://open.bigmodel.cn/api/paas/v4/'
  } else if (settings.value.llmModel === 'gemini-3-flash') {
    settings.value.llmBaseUrl = 'https://generativelanguage.googleapis.com/v1/'
  } else {
    settings.value.llmBaseUrl = 'http://localhost:11434/v1'
  }
}

const loadSettings = async () => {
  try {
    const res = await fetch('/api/settings')
    if (res.ok) {
      const data = await res.json()
      if (data.data) {
        Object.assign(settings.value, data.data)
        // Определить активный пресет
        for (const [id, config] of Object.entries(presetConfigs)) {
          if (config.maxAgents === settings.value.maxAgents && 
              config.maxRounds === settings.value.maxRounds) {
            activePreset.value = id
            break
          }
        }
      }
    }
    
    // Проверить подключение к Neo4j
    const healthRes = await fetch('/api/graph/health')
    neo4jConnected.value = healthRes.ok
  } catch (e) {
    console.log('Using default settings')
  }
}

const saveSettings = async () => {
  saving.value = true
  try {
    const res = await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings.value)
    })
    if (res.ok) {
      hasChanges.value = false
    }
  } catch (e) {
    console.error('Save error:', e)
  }
  saving.value = false
}

const resetSettings = () => {
  applyPreset('test')
  settings.value.llmModel = 'qwen3:8b'
  settings.value.llmBaseUrl = 'http://localhost:11434/v1'
  settings.value.neo4jUri = 'bolt://localhost:7687'
  settings.value.neo4jUser = 'neo4j'
  settings.value.neo4jPassword = ''
}

const goBack = () => {
  router.push('/')
}

onMounted(loadSettings)
</script>

<style scoped>
.settings-page {
  min-height: 100vh;
  background: #fafafa;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Navbar */
.navbar {
  background: #000;
  color: #fff;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-brand {
  font-size: 0.875rem;
  font-weight: 600;
  letter-spacing: 0.05em;
}

.btn-back {
  display: flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  border: 1px solid rgba(255,255,255,0.3);
  color: #fff;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8125rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-back:hover {
  background: rgba(255,255,255,0.1);
  border-color: rgba(255,255,255,0.5);
}

.btn-icon {
  font-size: 1rem;
}

.btn-text {
  font-size: 0.8125rem;
}

.nav-center {
  flex: 1;
  text-align: center;
}

.page-title {
  font-size: 0.875rem;
  font-weight: 500;
}

.nav-status {
  min-width: 120px;
  text-align: right;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.pending {
  background: #fff3e0;
  color: #e65100;
}

.status-badge.saved {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-badge.saving {
  background: #e3f2fd;
  color: #1565c0;
}

/* Content */
.settings-content {
  max-width: 640px;
  margin: 0 auto;
  padding: 32px 24px;
}

/* Sections */
.settings-section {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 16px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.section-header h2 {
  font-size: 1rem;
  font-weight: 600;
  color: #111;
}

.section-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  background: #f5f5f5;
  color: #666;
}

.section-badge.active {
  background: #e8f5e9;
  color: #2e7d32;
}

.section-desc {
  font-size: 0.875rem;
  color: #666;
  line-height: 1.5;
  margin-bottom: 20px;
}

/* Toggle */
.setting-item {
  margin-bottom: 16px;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.toggle-label input {
  display: none;
}

.toggle-switch {
  width: 44px;
  height: 24px;
  background: #e0e0e0;
  border-radius: 12px;
  position: relative;
  transition: background 0.2s;
}

.toggle-switch::after {
  content: '';
  position: absolute;
  width: 20px;
  height: 20px;
  background: #fff;
  border-radius: 50%;
  top: 2px;
  left: 2px;
  transition: transform 0.2s;
}

.toggle-label input:checked + .toggle-switch {
  background: #2196f3;
}

.toggle-label input:checked + .toggle-switch::after {
  transform: translateX(20px);
}

.toggle-text {
  font-size: 0.875rem;
  font-weight: 500;
}

.setting-hint {
  font-size: 0.75rem;
  color: #999;
  margin-top: 8px;
  margin-left: 56px;
}

/* Test Mode Info */
.test-mode-info {
  margin-top: 16px;
}

.info-card {
  background: #f5f5f5;
  border-radius: 8px;
  padding: 16px;
}

.info-card h4 {
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 12px;
}

.info-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.info-card li {
  font-size: 0.8125rem;
  color: #666;
  margin-bottom: 6px;
}

.info-card strong {
  color: #111;
}

/* Presets */
.presets-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.preset-card {
  background: #fafafa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
}

.preset-card:hover {
  border-color: #bdbdbd;
}

.preset-card.active {
  border-color: #2196f3;
  background: #e3f2fd;
}

.preset-name {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 4px;
}

.preset-desc {
  display: block;
  font-size: 0.75rem;
  color: #666;
  margin-bottom: 8px;
}

.preset-stats {
  display: block;
  font-size: 0.6875rem;
  color: #999;
}

/* Sliders */
.setting-group {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.setting-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.label-text {
  font-size: 0.875rem;
  font-weight: 500;
}

.label-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: #2196f3;
  font-family: 'JetBrains Mono', monospace;
}

.setting-item input[type="range"] {
  width: 100%;
  height: 4px;
  background: #e0e0e0;
  border-radius: 2px;
  appearance: none;
  cursor: pointer;
}

.setting-item input[type="range"]::-webkit-slider-thumb {
  appearance: none;
  width: 16px;
  height: 16px;
  background: #2196f3;
  border-radius: 50%;
  cursor: pointer;
}

.setting-item input[type="range"]:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.setting-locked {
  font-size: 0.75rem;
  color: #ff9800;
  margin-top: 6px;
}

/* Model Select */
.model-select {
  margin-bottom: 20px;
}

.model-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-top: 8px;
}

.model-option {
  cursor: pointer;
}

.model-option input {
  display: none;
}

.model-card {
  background: #fafafa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 12px;
  transition: all 0.2s;
}

.model-option:hover .model-card {
  border-color: #bdbdbd;
}

.model-option.selected .model-card {
  border-color: #2196f3;
  background: #e3f2fd;
}

.model-name {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 4px;
}

.model-size {
  display: inline-block;
  font-size: 0.6875rem;
  color: #666;
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 4px;
  margin-right: 6px;
}

.model-type {
  display: inline-block;
  font-size: 0.6875rem;
  color: #2196f3;
  background: #e3f2fd;
  padding: 2px 6px;
  border-radius: 4px;
}

/* Text Input */
.text-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 0.875rem;
  background: #fafafa;
  transition: border-color 0.2s;
}

.text-input:focus {
  outline: none;
  border-color: #2196f3;
  background: #fff;
}

/* Setting Group Inline */
.setting-group.inline {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

/* DB Status */
.db-status {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 10px 12px;
  background: #ffebee;
  border-radius: 6px;
  font-size: 0.8125rem;
  color: #c62828;
}

.db-status.connected {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-icon {
  font-size: 1rem;
}

/* Actions */
.settings-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.btn-primary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 24px;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
  background: #000;
  color: #fff;
  border: none;
}

.btn-primary:hover {
  background: #333;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-icon {
  font-size: 1rem;
}

/* Responsive */
@media (max-width: 600px) {
  .presets-grid {
    grid-template-columns: 1fr;
  }
  
  .model-options {
    grid-template-columns: 1fr;
  }
  
  .setting-group.inline {
    grid-template-columns: 1fr;
  }
  
  .settings-actions {
    flex-direction: column;
  }
}
</style>