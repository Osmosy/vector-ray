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
  Entity: 'Сущность',
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

export const relationTranslations = {
  WORKS_FOR: 'Работает в',
  PURCHASES_FROM: 'Покупает у',
  REPORTS_ON: 'Отчёт о',
  ADVOCATES_AGAINST: 'Выступает против',
  REGULATES: 'Регулирует',
  OWNS: 'Владеет',
  SUPPLIES_TO: 'Поставляет',
  COMPETES_WITH: 'Конкурирует с',
  PREFERS: 'Предпочитает',
  CRITICIZES: 'Критикует',
  RELATED_TO: 'Связан с',
  PART_OF: 'Часть',
  LOCATED_IN: 'Находится в',
  OPPOSES: 'Против',
  SUPPORTS: 'Поддерживает',
  AFFILIATES_WITH: 'Связан с',
  HAS_INFLUENCE_OVER: 'Влияет на',
  EMPLOYS: 'Нанимает',
  MENTIONS: 'Упоминает',
  RESPONDS_TO: 'Отвечает на',
}

/** Тип связи по-русски: WORKS_FOR → Работает в. */
export const translateRelation = (name) =>
  relationTranslations[name] || (name ? name.replace(/_/g, ' ').toLowerCase() : '')
