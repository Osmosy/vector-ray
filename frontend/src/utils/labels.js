/**
 * Русские подписи для типов сущностей и позиций.
 *
 * Типы приходят из онтологии, которую генерирует модель, — они английские
 * (Person, GovernmentOfficial, …), и в интерфейсе это выглядело как чужие
 * ярлыки: «GovernmentOfficial» рядом с русским текстом. Словарь общий, чтобы
 * один тип не переводился по-разному в разных панелях.
 */

export const entityTranslations = {
  // базовые типы
  Person: 'Человек',
  Organization: 'Организация',
  Company: 'Компания',
  GovernmentOfficial: 'Госслужащий',
  GovernmentAgency: 'Госучреждение',
  NGO: 'НКО',
  Executive: 'Руководитель',
  Resident: 'Житель',
  Citizen: 'Горожанин',
  Activist: 'Активист',
  Journalist: 'Журналист',
  Blogger: 'Блогер',
  MediaOutlet: 'СМИ',
  Analyst: 'Аналитик',
  Expert: 'Эксперт',
  Business: 'Бизнес',
  Enterprise: 'Предприятие',
  RetailChain: 'Розничная сеть',
  BrandStore: 'Бренд-магазин',
  Manufacturer: 'Производитель',
  Consumer: 'Потребитель',
  Product: 'Продукт',
  Service: 'Сервис',
  Infrastructure: 'Инфраструктура',
  Transport: 'Транспорт',
  Technology: 'Технология',
  Event: 'Событие',
  Location: 'Локация',
  Policy: 'Решение',
  Law: 'Закон',
  Regulation: 'Норматив',
  HealthAdvocate: 'Адвокат здоровья',
}

export const stanceTranslations = {
  neutral: 'Нейтральный',
  supportive: 'Поддерживающий',
  opposing: 'Противник',
  observer: 'Наблюдатель',
}

/** Тип сущности по-русски; незнакомый тип показываем как есть. */
export const translateEntity = (name) => entityTranslations[name] || name || ''

/** Позиция агента по-русски. */
export const translateStance = (stance) => stanceTranslations[stance] || stance || ''
