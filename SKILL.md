# SKILL.md — Skill Registry Documentation

> **Comprehensive documentation for the skill registration, resolution, execution, and validation system.**
> This document explains how skills are managed in the fighting-game-combo-optimizer system, including registration workflows, JSON schemas for input/output validation, and execution protocols.

---

## Table of Contents

1. [Overview](#overview)
2. [Skill Registration](#skill-registration)
3. [Skill Resolution](#skill-resolution)
4. [Skill Execution](#skill-execution)
5. [Input/Output Schemas](#inputoutput-schemas)
6. [Validation Protocols](#validation-protocols)
7. [Quality Gates](#quality-gates)
8. [Hooks Integration](#hooks-integration)
9. [State Management](#state-management)
10. [Event System](#event-system)

---

## Overview

The fighting-game-combo-optimizer uses a **dynamic skill registry** that provides:

- **Flexible Registration**: Skills can be registered with metadata, schemas, and trigger conditions
- **Intelligent Resolution**: Skills are resolved based on queries, context, and trigger confidence
- **Schema Validation**: Input and output schemas ensure data integrity
- **Lifecycle Management**: Hooks provide pre/post execution control
- **State Synchronization**: Shared state across skill executions
- **Event Emission**: Event-driven architecture for monitoring and coordination

### Key Components

```python
from config.skill_registry import (
    SkillRegistry,
    SkillMetadata,
    SkillInputSchema,
    SkillOutputSchema,
    TriggerType,
    SkillStatus
)

from hooks.lifecycle import LifecyclePhase, register_lifecycle_hook
from hooks.state_sync import StateManager, StateScope
from hooks.event_emitter import EventEmitter, EventType
```

---

## Skill Registration

### Registration Workflow

Skills are registered through the `SkillRegistry` using metadata objects:

```python
from config.skill_registry import register_skill, SkillMetadata, TriggerType

# Create skill metadata
metadata = SkillMetadata(
    name="sub-core-analysis",
    description="Analyze and propose optimal combo coordination for fighting games",
    version="1.0.0",
    trigger_type=TriggerType.MANUAL,
    trigger_keywords=["combo", "optimization", "frame data", "punish"],
    file_path="skills/sub-core-analysis.md"
)

# Register the skill
success = register_skill(metadata)
```

### Skill Metadata Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | str | Yes | Unique skill identifier |
| `description` | str | Yes | Human-readable description (used for triggering) |
| `version` | str | No | Semantic version (default: "1.0.0") |
| `author` | str | No | Author information |
| `tags` | List[str] | No | Category tags for organization |
| `trigger_type` | TriggerType | No | How the skill triggers (default: MANUAL) |
| `status` | SkillStatus | No | Current status (default: REGISTERED) |
| `dependencies` | List[str] | No | Other skills this skill depends on |
| `file_path` | str | No | Path to skill definition file |
| `trigger_keywords` | List[str] | No | Keywords for auto-triggering |
| `trigger_threshold` | float | No | Confidence threshold for triggering (default: 0.7) |

### Trigger Types

| Type | Description | Use Case |
|------|-------------|----------|
| `MANUAL` | Only invoked explicitly via `/skill-name` | Primary skills, main harness |
| `KEYWORD` | Triggered by keyword matching in queries | Specialized sub-skills |
| `CONTEXT` | Triggered by context analysis | Routing skills |
| `AUTO` | Automatically triggered by the system | Infrastructure skills |

### Automatic Discovery

Skills are automatically discovered from the `/skills` directory:

```python
from config.skill_registry import get_registry

# Get the registry instance
registry = get_registry()

# Skills are automatically discovered from:
# - skills/*.md files
# - skills/*/*.md subdirectories

# List all registered skills
all_skills = registry.list_skills()

# Filter by status
enabled_skills = registry.list_skills(status=SkillStatus.REGISTERED)

# Filter by tag
analysis_skills = registry.list_skills(tag="analysis")
```

---

## Skill Resolution

### Resolution Process

Skills are resolved based on name or query analysis:

```python
from config.skill_registry import resolve_skill

# Exact name resolution
skill = resolve_skill(name="sub-core-analysis")

# Query-based resolution (automatic)
skill = resolve_skill(
    query="What's the optimal combo for Sol Badguy?",
    context={"character": "Sol Badguy"}
)

# The system analyzes the query and finds the best-matching skill
```

### Confidence Scoring

Each skill computes a confidence score (0.0 to 1.0) for queries:

```python
# Internal scoring in SkillMetadata
def should_trigger(self, query: str, context: Optional[Dict] = None) -> float:
    """
    Calculate trigger confidence for a query.
    Returns: float (0.0 to 1.0)
    """
    # Keyword matching
    # Description matching
    # Context analysis
    return confidence_score
```

### Resolution Priority

When multiple skills match a query:

1. **Higher confidence score** wins
2. **Earlier registration** wins ties
3. **Manual trigger type** wins over automatic types

---

## Skill Execution

### Execution Protocol

Skills execute through a structured lifecycle:

```python
from hooks.lifecycle import execute_pre_hooks, execute_post_hooks
from hooks.event_emitter import emit_event, EventType

# Pre-execution hooks
results = execute_pre_hooks(LifecyclePhase.PRE_EXECUTION, context)

# Emit invocation event
emit_event(
    EventType.SKILL_INVOKED,
    payload={"skill": skill_name, "context": context}
)

# Execute skill logic
# ...

# Post-execution hooks
results = execute_post_hooks(LifecyclePhase.POST_EXECUTION, context)

# Emit completion event
emit_event(
    EventType.SKILL_COMPLETED,
    payload={"skill": skill_name, "result": result}
)
```

### Context Structure

The execution context contains:

```python
context = {
    # Input data
    "input": {...},

    # Configuration
    "config": {...},

    # State references
    "state": {
        "session": {...},
        "task": {...},
        "skill": {...}
    },

    # Metadata
    "metadata": {
        "skill_name": str,
        "execution_id": str,
        "timestamp": float,
        "correlation_id": str
    }
}
```

### Error Handling

Execution errors are handled with retry logic:

```python
max_retries = 2
retry_count = 0

while retry_count <= max_retries:
    try:
        result = execute_skill(context)
        break
    except Exception as e:
        retry_count += 1

        if retry_count > max_retries:
            # Emit error event
            emit_event(
                EventType.SKILL_FAILED,
                payload={"error": str(e), "retries": retry_count}
            )
            raise

        # Emit retry event
        emit_event(
            EventType.SKILL_RETRY,
            payload={"attempt": retry_count, "error": str(e)}
        )
```

---

## Input/Output Schemas

### Input Schema Definition

Input schemas validate skill input data:

```python
from config.skill_registry import SkillInputSchema

# Define input schema
input_schema = SkillInputSchema(
    required_fields=["game", "character", "situation"],
    optional_fields={
        "meter_available": 0,
        "screen_position": "midscreen"
    },
    field_types={
        "game": "str",
        "character": "str",
        "situation": "dict",
        "meter_available": "int"
    },
    validation_rules={
        "meter_available": {"min": 0, "max": 100},
        "screen_position": {"enum": ["midscreen", "corner", "wall"]}
    }
)

# Validate input
is_valid, errors = input_schema.validate(input_data)
```

### Output Schema Definition

Output schemas validate skill output:

```python
from config.skill_registry import SkillOutputSchema

# Define output schema
output_schema = SkillOutputSchema(
    required_sections=[
        "## Analysis",
        "## Verdict",
        "## Sources",
        "## Disclosure"
    ],
    output_format="markdown",
    field_types={
        "verdict": "str",
        "confidence": "float",
        "sources": "list"
    }
)

# Validate output
is_valid, errors = output_schema.validate(output_data)
```

### JSON Schema Files

Complete JSON schemas are defined in `/assets/schemas/`:

- `skill_input.json` — Universal input schema
- `skill_output.json` — Universal output schema
- `evidence_data.json` — Evidence validation schema

Example from `skill_input.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "FightingGameComboOptimizerInput",
  "type": "object",
  "required": ["analysis_request"],
  "properties": {
    "analysis_request": {
      "type": "string",
      "minLength": 10
    },
    "game": {"type": "string"},
    "character": {"type": "string"},
    "analysis_type": {
      "type": "string",
      "enum": ["combo_optimization", "punish_analysis", "frame_data", "comprehensive"]
    }
  }
}
```

---

## Validation Protocols

### Input Validation Flow

```python
def validate_skill_input(skill_name: str, input_data: Dict) -> tuple[bool, List[str]]:
    """
    Validate input data against skill schema.

    Args:
        skill_name: Name of the skill
        input_data: Input data to validate

    Returns:
        tuple: (is_valid, error_messages)
    """
    registry = get_registry()
    return registry.validate_skill_input(skill_name, input_data)
```

### Output Validation Flow

```python
def validate_skill_output(skill_name: str, output_data: Any) -> tuple[bool, List[str]]:
    """
    Validate output data against skill schema.

    Args:
        skill_name: Name of the skill
        output_data: Output data to validate

    Returns:
        tuple: (is_valid, error_messages)
    """
    registry = get_registry()
    return registry.validate_skill_output(skill_name, output_data)
```

### Validation Rules

Common validation rules:

| Rule | Type | Example |
|------|------|---------|
| `min` | Numeric | `{"min": 0}` — Value must be ≥ 0 |
| `max` | Numeric | `{"max": 100}` — Value must be ≤ 100 |
| `pattern` | String | `{"pattern": "^10\\."}` — DOI format |
| `enum` | Any | `{"enum": ["easy", "medium", "hard"]}` |
| `minLength` | String | `{"minLength": 10}` — Minimum length |
| `required` | Any | Field must be present |

---

## Quality Gates

### Universal Gates (U1-U6)

These gates apply to all skills:

| Gate | Check | Auto-Fix |
|------|-------|----------|
| U1 | ≥3 sources cited, ≥1 academic/authoritative | Fetch from knowledge base |
| U2 | Disclosure/limitations before recommendation | Prepend standard disclosure |
| U3 | Evidence hierarchy stated per source | Tag sources with tier labels |
| U4 | Language matches user preference | Translate output |
| U5 | Output uses declared template | Reformat to template |
| U6 | Every claim traceable to source or flagged | Mark claims with sources |

### Domain Gates (G1-G4)

Specific to fighting game analysis:

| Gate | Check | Auto-Fix |
|------|-------|----------|
| G1 | Frame advantage computed | Calculate frame data |
| G2 | Combo routes optimized for damage/meter | Optimize combo selections |
| G3 | Punish routes from frame data | Add punish analysis |
| G4 | Execution difficulty vs consistency noted | Add execution tradeoff |

### Gate Enforcement

```python
def apply_quality_gates(output: Dict, strict: bool = True) -> Dict:
    """
    Apply quality gates to output.

    Args:
        output: Output data to check
        strict: Whether to enforce all gates (default: True)

    Returns:
        dict: Output with gates applied
    """
    # Check each gate
    # Apply auto-fix if available
    # Flag limitations if unfixable
    # Return validated output
```

---

## Hooks Integration

### Registering Hooks

Hooks are registered for lifecycle phases:

```python
from hooks.lifecycle import register_lifecycle_hook, LifecyclePhase

def log_execution(context: Dict) -> None:
    """Log skill execution details."""
    logger.info(f"Executing skill: {context['metadata']['skill_name']}")

register_lifecycle_hook(
    phase=LifecyclePhase.PRE_EXECUTION,
    name="log_execution",
    handler=log_execution,
    priority=10
)
```

### Hook Decorators

Convenience decorators for common phases:

```python
from hooks.lifecycle import pre_execution, post_execution

@pre_execution(name="validate_context", priority=100)
def validate_context_before(context: Dict) -> Dict:
    """Validate execution context."""
    if "input" not in context:
        raise ValueError("Missing input in context")
    return context

@post_execution(name="log_result", priority=10)
def log_execution_result(context: Dict) -> None:
    """Log execution result."""
    result = context.get("result")
    logger.info(f"Execution result: {result}")
```

### Hook Results

Hook execution returns results:

```python
results = execute_pre_hooks(LifecyclePhase.PRE_EXECUTION, context)

for result in results:
    print(f"{result.hook_name}: {'PASS' if result.success else 'FAIL'} ({result.duration_ms:.2f}ms)")
```

---

## State Management

### State Scopes

State is organized into scopes:

```python
from hooks.state_sync import StateScope, get_state_manager

state_manager = get_state_manager()

# Set state in different scopes
state_manager.set("user_id", "12345", scope=StateScope.SESSION)
state_manager.set("current_analysis", {...}, scope=StateScope.TASK)
state_manager.set("skill_cache", {...}, scope=StateScope.SKILL)
```

### State Synchronization

State can be synchronized across scopes:

```python
from hooks.state_sync import sync_state

# Sync task state to session scope
synced_count = sync_state(
    source_scope=StateScope.TASK,
    target_scope=StateScope.SESSION,
    keys=["analysis_result", "character_data"],
    overwrite=False
)
```

### State Validation

State entries can be validated:

```python
from hooks.state_sync import StateValidationStatus

# Register validator for a key
state_manager.register_validator("meter_available", lambda x: 0 <= x <= 100)

# Validate state entry
result = state_manager.validate("meter_available", scope=StateScope.TASK)

if result.status == StateValidationStatus.VALID:
    print("State is valid")
```

---

## Event System

### Emitting Events

Events are emitted for key actions:

```python
from hooks.event_emitter import emit_event, EventType

# Emit skill invocation event
emit_event(
    EventType.SKILL_INVOKED,
    payload={
        "skill": "sub-core-analysis",
        "character": "Sol Badguy",
        "game": "Guilty Gear -Strive-"
    },
    source="main_harness"
)
```

### Subscribing to Events

Subscriptions receive events:

```python
from hooks.event_emitter import subscribe_to_event, Event

def handle_skill_completion(event: Event) -> None:
    """Handle skill completion events."""
    skill_name = event.payload.get("skill")
    print(f"Skill '{skill_name}' completed")

subscription = subscribe_to_event(
    event_type=EventType.SKILL_COMPLETED,
    handler=handle_skill_completion
)
```

### Event Filtering

Subscriptions can filter events:

```python
# Filter events by specific skill
def filter_sol_badguy_events(event: Event) -> bool:
    return event.payload.get("character") == "Sol Badguy"

subscription = subscribe_to_event(
    event_type=EventType.ANALYSIS_STARTED,
    handler=handle_sol_analysis,
    filter_func=filter_sol_badguy_events
)
```

---

## Complete Example

### Full Skill Execution Flow

```python
from config.skill_registry import resolve_skill, validate_skill_input, validate_skill_output
from hooks.lifecycle import execute_pre_hooks, execute_post_hooks, LifecyclePhase
from hooks.state_sync import get_state_manager, StateScope
from hooks.event_emitter import emit_event, EventType

def execute_skill_with_full_stack(query: str) -> Dict:
    """Execute a skill with full stack integration."""

    # 1. Resolve skill
    skill = resolve_skill(query=query)
    if not skill:
        raise ValueError(f"No skill found for query: {query}")

    # 2. Prepare context
    context = {
        "input": parse_query(query),
        "metadata": {
            "skill_name": skill.name,
            "execution_id": generate_id(),
            "timestamp": time.time()
        }
    }

    # 3. Pre-execution hooks
    emit_event(EventType.SKILL_INVOKED, payload={"skill": skill.name})
    execute_pre_hooks(LifecyclePhase.PRE_EXECUTION, context)

    # 4. Validate input
    is_valid, errors = validate_skill_input(skill.name, context["input"])
    if not is_valid:
        raise ValueError(f"Input validation failed: {errors}")

    # 5. Execute skill logic
    try:
        result = execute_skill_logic(skill, context)

        # 6. Validate output
        is_valid, errors = validate_skill_output(skill.name, result)
        if not is_valid:
            logger.warning(f"Output validation failed: {errors}")

        # 7. Post-execution hooks
        context["result"] = result
        execute_post_hooks(LifecyclePhase.POST_EXECUTION, context)

        # 8. Emit completion
        emit_event(
            EventType.SKILL_COMPLETED,
            payload={"skill": skill.name, "result": result}
        )

        return result

    except Exception as e:
        emit_event(
            EventType.SKILL_FAILED,
            payload={"skill": skill.name, "error": str(e)}
        )
        raise
```

---

## Metadata

**Document Version**: 1.0.0
**Last Updated**: 2026-07-28
**Maintainer**: fighting-game-combo-optimizer skill

**Related Documents**:
- `/references/evidence_schemas.md` — Complete JSON schema definitions
- `/config/skill_registry.py` — Registry implementation
- `/hooks/` — Hook, state, and event system implementations

---

*This document is maintained as part of the skill system. Update as features are added.*
