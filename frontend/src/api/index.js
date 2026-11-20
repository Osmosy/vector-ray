import axios from 'axios'

// Create axios instance
const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001',
  timeout: 300000, // 5 minute timeout (ontology generation may require longer time)
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
service.interceptors.request.use(
  config => {
    return config
  },
  error => {
    console.error('Ошибка запроса:', error)
    return Promise.reject(error)
  }
)

// Response interceptor (fault-tolerant retry mechanism)
service.interceptors.response.use(
  response => {
    const res = response.data

    // If the returned status code is not success, throw error
    if (!res.success && res.success !== undefined) {
      console.error('Ошибка API:', res.error || res.message || 'неизвестная ошибка')
      return Promise.reject(new Error(res.error || res.message || 'Ошибка запроса'))
    }

    return res
  },
  error => {
    console.error('Ошибка ответа:', error)

    // Текст ошибки уходит в логи интерфейса — переводим технические сообщения axios
    if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
      error.message = 'Сервер не ответил вовремя'
    } else if (error.message === 'Network Error') {
      error.message = 'Нет связи с сервером — проверьте, запущен ли бэкенд'
    } else if (error.response?.status === 404) {
      error.message = error.response?.data?.error || 'Запрошенный объект не найден'
    } else if (error.response?.status >= 500) {
      error.message = error.response?.data?.error || 'Внутренняя ошибка сервера'
    }

    return Promise.reject(error)
  }
)

// Request function with retry
export const requestWithRetry = async (requestFn, maxRetries = 3, delay = 1000) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await requestFn()
    } catch (error) {
      if (i === maxRetries - 1) throw error

      console.warn(`Request failed, retrying (${i + 1}/${maxRetries})...`)
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)))
    }
  }
}

export default service
