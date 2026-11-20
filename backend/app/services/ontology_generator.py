"""
Ontology generation service
Interface 1: Analyze text content and generate entity and relationship type definitions suitable for social simulation
"""

import json
from typing import Dict, Any, List, Optional
from ..utils.llm_client import LLMClient


# System prompt for ontology generation
ONTOLOGY_SYSTEM_PROMPT = """Вы — эксперт по проектированию онтологии графов знаний. Ваша задача — проанализировать данный текст и требования симуляции, и разработать типы сущностей и типы отношений, подходящие для **симуляции мнений в социальных медиа**.

**Важно: Вывод должен быть на русском языке в формате JSON, ничего кроме JSON не выводить.**

## Фоновая информация о задаче

Мы строим **систему симуляции мнений в социальных медиа**. В этой системе:
- Каждая сущность — это "аккаунт" или "субъект", который может высказываться, взаимодействовать и распространять информацию в социальных медиа
- Сущности влияют друг на друга, делают репосты, комментируют и отвечают
- Нам нужно моделировать реакции различных сторон в событиях общественного мнения и пути распространения информации

Поэтому **сущности должны быть реальными сущностями, которые могут высказываться и взаимодействовать в социальных медиа**:

**Могут быть**:
- Конкретные люди (общественные деятели, стейкхолдеры, лидеры мнений, эксперты, обычные люди)
- Компании и предприятия (включая их официальные аккаунты)
- Организации (университеты, ассоциации, НКО, профсоюзы и т.д.)
- Государственные учреждения и регулирующие органы
- Медиа-учреждения (газеты, телеканалы, самостоятельные медиа, сайты)
- Сами платформы социальных медиа
- Представители конкретных групп (например, ассоциации выпускников, фанатские группы, группы защиты прав)

**Не могут быть**:
- Абстрактные концепции (такие как "общественное мнение", "эмоция", "тренд")
- Темы/предметы (такие как "академическая честность", "реформа образования")
- Взгляды/отношения (такие как "сторонники", "противники")

## Формат вывода

Выведите JSON в следующей структуре:

```json
{
    "entity_types": [
        {
            "name": "Название типа сущности (английский, PascalCase)",
            "description": "Краткое описание (русский, не более 100 символов)",
            "attributes": [
                {
                    "name": "Название атрибута (английский, snake_case)",
                    "type": "text",
                    "description": "Описание атрибута (русский)"
                }
            ],
            "examples": ["Пример сущности 1", "Пример сущности 2"]
        }
    ],
    "edge_types": [
        {
            "name": "Название типа отношения (английский, UPPER_SNAKE_CASE)",
            "description": "Краткое описание (русский, не более 100 символов)",
            "source_targets": [
                {"source": "Тип исходной сущности", "target": "Тип целевой сущности"}
            ],
            "attributes": []
        }
    ],
    "analysis_summary": "Краткий анализ и объяснение содержания текста (на русском)"
}
```

## Руководство по проектированию (Крайне важно!)

### 1. Проектирование типов сущностей — Строго соблюдать

**Требование к количеству: Ровно 10 типов сущностей**

**Требование к иерархической структуре (должны быть конкретные типы и резервные типы)**:

Ваши 10 типов сущностей должны включать следующую иерархию:

A. **Резервные типы (обязательно включить, поместить в последние 2 позиции списка)**:
   - `Person`: Резервный тип для любого физического лица. Когда человек не подходит под другие более конкретные типы людей, используйте этот.
   - `Organization`: Резервный тип для любой организации. Когда организация не подходит под другие более конкретные типы организаций, используйте этот.

B. **Конкретные типы (8, проектируются на основе содержания текста)**:
   - Проектируйте более конкретные типы для главных персонажей, появляющихся в тексте
   - Пример: Если текст касается академических событий, могут быть `Student`, `Professor`, `University`
   - Пример: Если текст касается бизнес-событий, могут быть `Company`, `CEO`, `Employee`

**Зачем нужны резервные типы**:
- В тексте появятся различные люди, такие как "учителя начальных классов", "случайный человек", "некий пользователь сети"
- Если нет подходящего конкретного типа, они должны быть классифицированы как `Person`
- Аналогично, небольшие организации и временные группы должны быть классифицированы как `Organization`

**Принципы проектирования конкретных типов**:
- Определите типы с высокой частотой или ключевой ролью из текста
- Каждый конкретный тип должен иметь чёткие границы, избегать перекрытий
- Описание должно чётко объяснять разницу между этим типом и резервным типом

### 2. Relationship Type Design

- Quantity: 6-10
- Relationships should reflect real connections in social media interactions
- Ensure relationship source_targets cover your defined entity types

### 3. Attribute Design

- 1-3 key attributes per entity type
- **Note**: Attribute names cannot use `name`, `uuid`, `group_id`, `created_at`, `summary` (these are system reserved words)
- Recommended: `full_name`, `title`, `role`, `position`, `location`, `description`, etc.

## Entity Type Reference

**Individual types (specific)**:
- Student: Student
- Professor: Professor/Scholar
- Journalist: Journalist
- Celebrity: Celebrity/Internet celebrity
- Executive: Executive
- Official: Government official
- Lawyer: Lawyer
- Doctor: Doctor

**Individual types (fallback)**:
- Person: Any natural person (use when not fitting other specific types)

**Organization types (specific)**:
- University: University
- Company: Company/Enterprise
- GovernmentAgency: Government agency
- MediaOutlet: Media institution
- Hospital: Hospital
- School: Primary/Secondary school
- NGO: Non-governmental organization

**Organization types (fallback)**:
- Organization: Any organization (use when not fitting other specific types)

## Relationship Type Reference

- WORKS_FOR: Works for
- STUDIES_AT: Studies at
- AFFILIATED_WITH: Affiliated with
- REPRESENTS: Represents
- REGULATES: Regulates
- REPORTS_ON: Reports on
- COMMENTS_ON: Comments on
- RESPONDS_TO: Responds to
- SUPPORTS: Supports
- OPPOSES: Opposes
- COLLABORATES_WITH: Collaborates with
- COMPETES_WITH: Competes with
"""


class OntologyGenerator:
    """
    Ontology generator
    Analyze text content and generate entity and relationship type definitions
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()

    def generate(
        self,
        document_texts: List[str],
        simulation_requirement: str,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate ontology definition

        Args:
            document_texts: List of document texts
            simulation_requirement: Description of simulation requirements
            additional_context: Additional context

        Returns:
            Ontology definition (entity_types, edge_types, etc.)
        """
        # Build user message
        user_message = self._build_user_message(
            document_texts,
            simulation_requirement,
            additional_context
        )

        messages = [
            {"role": "system", "content": ONTOLOGY_SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]

        # Call LLM
        result = self.llm_client.chat_json(
            messages=messages,
            temperature=0.3,
            max_tokens=4096
        )

        # Validate and post-process
        result = self._validate_and_process(result)

        return result

    # Maximum text length for LLM (50,000 characters)
    MAX_TEXT_LENGTH_FOR_LLM = 50000

    def _build_user_message(
        self,
        document_texts: List[str],
        simulation_requirement: str,
        additional_context: Optional[str]
    ) -> str:
        """Build user message"""

        # Combine texts
        combined_text = "\n\n---\n\n".join(document_texts)
        original_length = len(combined_text)

        # If text exceeds 50,000 characters, truncate (only affects LLM input, not graph construction)
        if len(combined_text) > self.MAX_TEXT_LENGTH_FOR_LLM:
            combined_text = combined_text[:self.MAX_TEXT_LENGTH_FOR_LLM]
            combined_text += f"\n\n...(Исходный текст содержит {original_length} символов, извлечено первых {self.MAX_TEXT_LENGTH_FOR_LLM} символов для анализа онтологии)..."

        message = f"""## Требования к симуляции

{simulation_requirement}

## Содержание документа

{combined_text}
"""

        if additional_context:
            message += f"""
## Дополнительное пояснение

{additional_context}
"""

        message += """
На основе вышеуказанного содержания разработайте типы сущностей и типы отношений, подходящие для симуляции общественного мнения.

**Правила, которые нужно соблюдать**:
1. Должно быть ровно 10 типов сущностей
2. Последние 2 должны быть резервными типами: Person (резерв для людей) и Organization (резерв для организаций)
3. Первые 8 — конкретные типы, разработанные на основе содержания текста
4. Все типы сущностей должны быть реальными субъектами, которые могут высказывать мнения, а не абстрактными концепциями
5. Имена атрибутов не могут использовать заррезервированные слова name, uuid, group_id, используйте full_name, org_name и т.д.
"""

        return message
    
    def _validate_and_process(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and post-process result"""

        # Ensure necessary fields exist
        if "entity_types" not in result:
            result["entity_types"] = []
        if "edge_types" not in result:
            result["edge_types"] = []
        if "analysis_summary" not in result:
            result["analysis_summary"] = ""

        # Validate entity types
        for entity in result["entity_types"]:
            if "attributes" not in entity:
                entity["attributes"] = []
            if "examples" not in entity:
                entity["examples"] = []
            # Ensure description doesn't exceed 100 characters
            if len(entity.get("description", "")) > 100:
                entity["description"] = entity["description"][:97] + "..."

        # Validate relationship types
        for edge in result["edge_types"]:
            if "source_targets" not in edge:
                edge["source_targets"] = []
            if "attributes" not in edge:
                edge["attributes"] = []
            if len(edge.get("description", "")) > 100:
                edge["description"] = edge["description"][:97] + "..."

        # Zep API limit: maximum 10 custom entity types, maximum 10 custom edge types
        MAX_ENTITY_TYPES = 10
        MAX_EDGE_TYPES = 10

        # Fallback type definitions
        person_fallback = {
            "name": "Person",
            "description": "Any individual person not fitting other specific person types.",
            "attributes": [
                {"name": "full_name", "type": "text", "description": "Full name of the person"},
                {"name": "role", "type": "text", "description": "Role or occupation"}
            ],
            "examples": ["ordinary citizen", "anonymous netizen"]
        }

        organization_fallback = {
            "name": "Organization",
            "description": "Any organization not fitting other specific organization types.",
            "attributes": [
                {"name": "org_name", "type": "text", "description": "Name of the organization"},
                {"name": "org_type", "type": "text", "description": "Type of organization"}
            ],
            "examples": ["small business", "community group"]
        }

        # Check if fallback types already exist
        entity_names = {e["name"] for e in result["entity_types"]}
        has_person = "Person" in entity_names
        has_organization = "Organization" in entity_names

        # Fallback types to add
        fallbacks_to_add = []
        if not has_person:
            fallbacks_to_add.append(person_fallback)
        if not has_organization:
            fallbacks_to_add.append(organization_fallback)

        if fallbacks_to_add:
            current_count = len(result["entity_types"])
            needed_slots = len(fallbacks_to_add)

            # If adding would exceed 10, need to remove some existing types
            if current_count + needed_slots > MAX_ENTITY_TYPES:
                # Calculate how many to remove
                to_remove = current_count + needed_slots - MAX_ENTITY_TYPES
                # Remove from end (keep more important specific types in front)
                result["entity_types"] = result["entity_types"][:-to_remove]

            # Add fallback types
            result["entity_types"].extend(fallbacks_to_add)

        # Final check to ensure limits not exceeded (defensive programming)
        if len(result["entity_types"]) > MAX_ENTITY_TYPES:
            result["entity_types"] = result["entity_types"][:MAX_ENTITY_TYPES]

        if len(result["edge_types"]) > MAX_EDGE_TYPES:
            result["edge_types"] = result["edge_types"][:MAX_EDGE_TYPES]

        return result
    
    def generate_python_code(self, ontology: Dict[str, Any]) -> str:
        """
        [DEPRECATED] Convert ontology definition to Zep-format Pydantic code.
        Not used in Vector Ray-Offline (ontology stored as JSON in Neo4j).
        Kept for reference only.
        """
        code_lines = [
            '"""',
            'Custom entity type definitions',
            'Auto-generated by Vector Ray for social opinion simulation',
            '"""',
            '',
            'from pydantic import Field',
            'from zep_cloud.external_clients.ontology import EntityModel, EntityText, EdgeModel',
            '',
            '',
            '# ============== Entity Type Definitions ==============',
            '',
        ]

        # Generate entity types
        for entity in ontology.get("entity_types", []):
            name = entity["name"]
            desc = entity.get("description", f"A {name} entity.")

            code_lines.append(f'class {name}(EntityModel):')
            code_lines.append(f'    """{desc}"""')

            attrs = entity.get("attributes", [])
            if attrs:
                for attr in attrs:
                    attr_name = attr["name"]
                    attr_desc = attr.get("description", attr_name)
                    code_lines.append(f'    {attr_name}: EntityText = Field(')
                    code_lines.append(f'        description="{attr_desc}",')
                    code_lines.append(f'        default=None')
                    code_lines.append(f'    )')
            else:
                code_lines.append('    pass')

            code_lines.append('')
            code_lines.append('')

        code_lines.append('# ============== Relationship Type Definitions ==============')
        code_lines.append('')

        # Generate relationship types
        for edge in ontology.get("edge_types", []):
            name = edge["name"]
            # Convert to PascalCase class name
            class_name = ''.join(word.capitalize() for word in name.split('_'))
            desc = edge.get("description", f"A {name} relationship.")

            code_lines.append(f'class {class_name}(EdgeModel):')
            code_lines.append(f'    """{desc}"""')

            attrs = edge.get("attributes", [])
            if attrs:
                for attr in attrs:
                    attr_name = attr["name"]
                    attr_desc = attr.get("description", attr_name)
                    code_lines.append(f'    {attr_name}: EntityText = Field(')
                    code_lines.append(f'        description="{attr_desc}",')
                    code_lines.append(f'        default=None')
                    code_lines.append(f'    )')
            else:
                code_lines.append('    pass')

            code_lines.append('')
            code_lines.append('')

        # Generate type dictionaries
        code_lines.append('# ============== Type Configuration ==============')
        code_lines.append('')
        code_lines.append('ENTITY_TYPES = {')
        for entity in ontology.get("entity_types", []):
            name = entity["name"]
            code_lines.append(f'    "{name}": {name},')
        code_lines.append('}')
        code_lines.append('')
        code_lines.append('EDGE_TYPES = {')
        for edge in ontology.get("edge_types", []):
            name = edge["name"]
            class_name = ''.join(word.capitalize() for word in name.split('_'))
            code_lines.append(f'    "{name}": {class_name},')
        code_lines.append('}')
        code_lines.append('')

        # Generate source_targets mapping for edges
        code_lines.append('EDGE_SOURCE_TARGETS = {')
        for edge in ontology.get("edge_types", []):
            name = edge["name"]
            source_targets = edge.get("source_targets", [])
            if source_targets:
                st_list = ', '.join([
                    f'{{"source": "{st.get("source", "Entity")}", "target": "{st.get("target", "Entity")}"}}'
                    for st in source_targets
                ])
                code_lines.append(f'    "{name}": [{st_list}],')
        code_lines.append('}')

        return '\n'.join(code_lines)

