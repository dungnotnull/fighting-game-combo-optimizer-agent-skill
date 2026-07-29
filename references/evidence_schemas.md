# Evidence Schemas Reference — Fighting-Game Combo & Frame-Data Optimization

> This document contains JSON schemas and validation rules for all evidence types, skill inputs/outputs, and data structures used in the fighting game combo optimization system.

---

## Schema Overview

### Schema Categories

1. **Input Schemas**: Validation for skill input data
2. **Output Schemas**: Validation for skill output data
3. **Evidence Schemas**: Validation for evidence and citations
4. **Analysis Schemas**: Validation for analysis results
5. **Configuration Schemas**: Validation for system configuration

---

## Input Schemas

### Schema 1: Gather Requirements Input

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "GatherRequirementsInput",
  "description": "Input schema for the requirements gathering sub-skill",
  "type": "object",
  "required": ["user_query"],
  "properties": {
    "user_query": {
      "type": "string",
      "minLength": 1,
      "description": "The user's raw query or request"
    },
    "provided_inputs": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string"},
          "content": {"type": "string"},
          "type": {"type": "string", "enum": ["file", "text", "url", "data"]}
        }
      },
      "description": "Optional pre-provided inputs or context"
    },
    "language": {
      "type": "string",
      "enum": ["en", "vi", "auto"],
      "default": "auto",
      "description": "Output language preference"
    }
  }
}
```

### Schema 2: Evidence Collector Input

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "EvidenceCollectorInput",
  "description": "Input schema for the evidence collection sub-skill",
  "type": "object",
  "required": ["requirements"],
  "properties": {
    "requirements": {
      "$ref": "#/definitions/RequirementsObject"
    },
    "max_sources": {
      "type": "integer",
      "minimum": 1,
      "maximum": 20,
      "default": 10,
      "description": "Maximum number of sources to fetch"
    },
    "source_types": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["frame_data", "combo_guide", "academic", "news", "video"]
      },
      "description": "Preferred source types to prioritize"
    }
  },
  "definitions": {
    "RequirementsObject": {
      "type": "object",
      "required": ["object_of_analysis"],
      "properties": {
        "object_of_analysis": {
          "type": "string",
          "description": "What is being analyzed"
        },
        "scope": {
          "type": "string",
          "description": "Analysis scope and boundaries"
        },
        "timeframe": {
          "type": "string",
          "description": "Time frame for the analysis"
        },
        "available_inputs": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Available input materials"
        },
        "target_audience": {
          "type": "string",
          "description": "Who will consume the analysis"
        },
        "language": {
          "type": "string",
          "enum": ["en", "vi"],
          "description": "Preferred output language"
        }
      }
    }
  }
}
```

### Schema 3: Core Analysis Input

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "CoreAnalysisInput",
  "description": "Input schema for the core fighting game analysis sub-skill",
  "type": "object",
  "required": ["game", "character", "situation"],
  "properties": {
    "game": {
      "type": "string",
      "minLength": 1,
      "description": "Fighting game title"
    },
    "character": {
      "type": "string",
      "minLength": 1,
      "description": "Character name to analyze"
    },
    "opponent_character": {
      "type": "string",
      "description": "Opponent's character (optional)"
    },
    "situation": {
      "$ref": "#/definitions/SituationObject"
    },
    "meter_available": {
      "type": "integer",
      "minimum": 0,
      "default": 0,
      "description": "Available meter amount"
    },
    "screen_position": {
      "type": "string",
      "enum": ["midscreen", "corner", "wall", "custom"],
      "default": "midscreen",
      "description": "Screen position"
    },
    "analysis_type": {
      "type": "string",
      "enum": ["combo_optimization", "punish_analysis", "frame_data", "meter_economy", "okizeme", "comprehensive"],
      "default": "comprehensive",
      "description": "Type of analysis to perform"
    }
  },
  "definitions": {
    "SituationObject": {
      "type": "object",
      "required": ["type"],
      "properties": {
        "type": {
          "type": "string",
          "enum": ["on_block", "on_hit", "on_whiff", "on_counter_hit", "neutral"]
        },
        "move": {
          "type": "string",
          "description": "Relevant move for the situation"
        },
        "frame_advantage": {
          "type": "integer",
          "description": "Known frame advantage (if available)"
        }
      }
    }
  }
}
```

---

## Output Schemas

### Schema 4: Analysis Output

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AnalysisOutput",
  "description": "Standard output schema for fighting game analysis results",
  "type": "object",
  "required": [
    "verdict",
    "evidence_summary",
    "disclosure",
    "analysis_details"
  ],
  "properties": {
    "verdict": {
      "type": "string",
      "enum": [
        "optimal_combo_plan",
        "conditional_execution_risk",
        "suboptimal_routes",
        "inconclusive"
      ],
      "description": "Final verdict category"
    },
    "confidence": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "description": "Confidence score in the verdict"
    },
    "evidence_summary": {
      "$ref": "#/definitions/EvidenceSummary"
    },
    "disclosure": {
      "type": "string",
      "minLength": 50,
      "description": "Risk/limitation disclosure (mandatory, before verdict)"
    },
    "analysis_details": {
      "$ref": "#/definitions/AnalysisDetails"
    },
    "recommended_actions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["action", "priority"],
        "properties": {
          "action": {"type": "string"},
          "priority": {
            "type": "string",
            "enum": ["high", "medium", "low"]
          },
            "reasoning": {"type": "string"}
          }
        }
    },
    "scenarios": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/Scenario"
      },
      "minItems": 1,
      "maxItems": 5,
      "description": "Best/base/worst case scenarios"
    },
    "sources": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/Source"
      },
      "minItems": 3,
      "description": "Cited sources (minimum 3)"
    }
  },
  "definitions": {
    "EvidenceSummary": {
      "type": "object",
      "required": ["total_sources", "academic_sources", "domain_sources"],
      "properties": {
        "total_sources": {"type": "integer", "minimum": 3},
        "academic_sources": {"type": "integer", "minimum": 1},
        "domain_sources": {"type": "integer", "minimum": 1},
        "tier_distribution": {
          "type": "object",
          "properties": {
            "tier_1": {"type": "integer"},
            "tier_2": {"type": "integer"},
            "tier_3": {"type": "integer"},
            "tier_4": {"type": "integer"}
          }
        }
      }
    },
    "AnalysisDetails": {
      "type": "object",
      "properties": {
        "game": {"type": "string"},
        "character": {"type": "string"},
        "analysis_type": {"type": "string"},
        "metrics": {
          "type": "object",
          "properties": {
            "damage": {"type": "number"},
            "meter_efficiency": {"type": "number"},
            "execution_difficulty": {"type": "string"},
            "consistency_rating": {"type": "number"}
          }
        }
      }
    },
    "Scenario": {
      "type": "object",
      "required": ["name", "description", "probability"],
      "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "probability": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0
        },
        "outcome": {"type": "string"}
      }
    },
    "Source": {
      "type": "object",
      "required": ["name", "url", "tier"],
      "properties": {
        "name": {"type": "string"},
        "url": {"type": "string", "format": "uri"},
        "tier": {
          "type": "string",
          "enum": ["tier_1", "tier_2", "tier_3", "tier_4"]
        },
        "date_accessed": {
          "type": "string",
          "format": "date"
        },
        "relevance_score": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 10.0
        }
      }
    }
  }
}
```

### Schema 5: Frame Data Output

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "FrameDataOutput",
  "description": "Output schema for frame data analysis",
  "type": "object",
  "required": [
    "move_name",
    "character",
    "game",
    "frame_data",
    "punish_analysis"
  ],
  "properties": {
    "move_name": {"type": "string"},
    "character": {"type": "string"},
    "game": {"type": "string"},
    "frame_data": {
      "$ref": "#/definitions/FrameData"
    },
    "punish_analysis": {
      "$ref": "#/definitions/PunishAnalysis"
    },
    "sources": {
      "type": "array",
      "items": {"type": "string"}
    }
  },
  "definitions": {
    "FrameData": {
      "type": "object",
      "required": ["startup", "active", "recovery"],
      "properties": {
        "startup": {
          "type": "integer",
          "minimum": 1,
          "description": "Frames before move becomes active"
        },
        "active": {
          "type": "integer",
          "minimum": 1,
          "description": "Frames during which move can hit"
        },
        "recovery": {
          "type": "integer",
          "minimum": 0,
          "description": "Frames after active until full recovery"
        },
        "total": {
          "type": "integer",
          "description": "Total frame count (startup + active + recovery)"
        },
        "advantage_on_block": {
          "type": "integer",
          "description": "Frame advantage when blocked"
        },
        "advantage_on_hit": {
          "type": "integer",
          "description": "Frame advantage when hit"
        },
        "advantage_on_counter_hit": {
          "type": "integer",
          "description": "Frame advantage on counter hit"
        },
        "cancel_window": {
          "type": "integer",
          "description": "Frames during which move can be cancelled"
        },
        "properties": {
          "type": "array",
          "items": {
            "type": "string",
            "enum": ["overhead", "low", "mid", "throw", "projectile", "invincible"]
          }
        }
      }
    },
    "PunishAnalysis": {
      "type": "object",
      "properties": {
        "safety_status": {
          "type": "string",
          "enum": ["safe", "unsafe", "conditional"]
        },
        "punish_on_block": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "punish": {"type": "string"},
              "startup_requirement": {"type": "integer"},
              "damage": {"type": "integer"},
              "difficulty": {"type": "string"}
            }
          }
        },
        "conversion_on_hit": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "route": {"type": "string"},
              "damage": {"type": "integer"},
              "meter_cost": {"type": "integer"},
              "difficulty": {"type": "string"}
            }
          }
        }
      }
    }
  }
}
```

---

## Evidence Schemas

### Schema 6: Evidence Item

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "EvidenceItem",
  "description": "Schema for a single evidence item",
  "type": "object",
  "required": [
    "content",
    "source",
    "tier",
    "retrieval_date"
  ],
  "properties": {
    "content": {
      "type": "string",
      "minLength": 1,
      "description": "The evidence content or finding"
    },
    "source": {
      "$ref": "#/definitions/EvidenceSource"
    },
    "tier": {
      "$ref": "#/definitions/EvidenceTier"
    },
    "retrieval_date": {
      "type": "string",
      "format": "date-time",
      "description": "When this evidence was retrieved"
    },
    "confidence": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "description": "Confidence in this evidence"
    },
    "applicability": {
      "type": "string",
      "enum": ["direct", "supporting", "contextual"],
      "description": "How directly this evidence applies"
    },
    "notes": {
      "type": "string",
      "description": "Additional context or notes"
    }
  },
  "definitions": {
    "EvidenceSource": {
      "type": "object",
      "required": ["name", "url"],
      "properties": {
        "name": {"type": "string"},
        "url": {"type": "string", "format": "uri"},
        "type": {
          "type": "string",
          "enum": ["academic_paper", "database", "guide", "video", "forum", "news"]
        },
        "authors": {
          "type": "array",
          "items": {"type": "string"}
        },
        "publication_date": {
          "oneOf": [
            {"type": "string", "format": "date"},
            {"type": "string", "format": "date-time"},
            {"type": "null"}
          ]
        },
        "doi": {
          "type": "string",
          "pattern": "^10\\..+",
          "description": "Digital Object Identifier for academic papers"
        },
        "access_date": {
          "type": "string",
          "format": "date"
        }
      }
    },
    "EvidenceTier": {
      "type": "string",
      "enum": ["tier_1", "tier_2", "tier_3", "tier_4"],
      "description": "Evidence tier per hierarchy"
    }
  }
}
```

### Schema 7: Evidence Collection

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "EvidenceCollection",
  "description": "Schema for a collection of evidence items",
  "type": "object",
  "required": ["items", "metadata"],
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "$ref": "evidence_item.json#/definitions/EvidenceItem"
      },
      "minItems": 3
    },
    "metadata": {
      "$ref": "#/definitions/EvidenceMetadata"
    }
  },
  "definitions": {
    "EvidenceMetadata": {
      "type": "object",
      "properties": {
        "collection_date": {
          "type": "string",
          "format": "date-time"
        },
        "query_used": {"type": "string"},
        "sources_searched": {
          "type": "array",
          "items": {"type": "string"}
        },
        "total_results": {"type": "integer"},
        "tier_distribution": {
          "type": "object",
          "properties": {
            "tier_1": {"type": "integer"},
            "tier_2": {"type": "integer"},
            "tier_3": {"type": "integer"},
            "tier_4": {"type": "integer"}
          }
        }
      }
    }
  }
}
```

---

## Configuration Schemas

### Schema 8: Knowledge Update Config

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "KnowledgeUpdateConfig",
  "description": "Configuration for the knowledge update pipeline",
  "type": "object",
  "required": ["domain", "keywords"],
  "properties": {
    "domain": {
      "type": "string",
      "description": "Domain name for this configuration"
    },
    "keywords": {
      "type": "array",
      "items": {"type": "string"},
      "minItems": 1,
      "description": "Keywords for relevance matching"
    },
    "arxiv_categories": {
      "type": "array",
      "items": {"type": "string"},
      "description": "ArXiv categories to search"
    },
    "semantic_scholar_keywords": {
      "type": "array",
      "items": {"type": "string"}
    },
    "rss_feeds": {
      "type": "array",
      "items": {"type": "string", "format": "uri"}
    },
    "authoritative_docs": {
      "type": "array",
      "items": {"type": "string"}
    },
    "scoring_weights": {
      "$ref": "#/definitions/ScoringWeights"
    },
    "max_results_per_source": {
      "type": "integer",
      "minimum": 1,
      "default": 10
    },
    "max_new_entries_per_run": {
      "type": "integer",
      "minimum": 1,
      "default": 20
    }
  },
  "definitions": {
    "ScoringWeights": {
      "type": "object",
      "required": ["recency", "keyword_relevance", "citation_count"],
      "properties": {
        "recency": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0,
          "default": 0.4
        },
        "keyword_relevance": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0,
          "default": 0.4
        },
        "citation_count": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0,
          "default": 0.2
        }
      }
    }
  }
}
```

---

## Validation Rules

### Validation Functions

```python
def validate_input_schema(schema_name: str, input_data: dict) -> tuple[bool, list]:
    """
    Validate input data against a named schema.

    Args:
        schema_name: Name of the schema to validate against
        input_data: Input data to validate

    Returns:
        tuple: (is_valid, error_messages)
    """
    # Implementation uses jsonschema library
    pass

def validate_output_schema(schema_name: str, output_data: any) -> tuple[bool, list]:
    """
    Validate output data against a named schema.

    Args:
        schema_name: Name of the schema to validate against
        output_data: Output data to validate

    Returns:
        tuple: (is_valid, error_messages)
    """
    # Implementation
    pass

def validate_evidence_tier(source: dict) -> str:
    """
    Determine evidence tier for a source.

    Args:
        source: Source information

    Returns:
        str: Tier classification (tier_1, tier_2, tier_3, tier_4)
    """
    # Implementation based on evidence hierarchy
    pass
```

---

## Schema Metadata

**Schema Version**: 1.0.0
**JSON Schema Draft**: draft-07
**Validation Library**: jsonschema
**Last Updated**: 2026-07-28

---

## Usage Examples

### Validating Input

```python
from config.skill_registry import SkillInputSchema

# Create input schema
schema = SkillInputSchema(
    required_fields=["game", "character", "situation"],
    field_types={
        "game": "str",
        "character": "str",
        "situation": "dict"
    }
)

# Validate input
input_data = {
    "game": "Guilty Gear -Strive-",
    "character": "Sol Badguy",
    "situation": {"type": "on_hit", "move": "5H"}
}

is_valid, errors = schema.validate(input_data)
if not is_valid:
    print("Validation errors:", errors)
```

### Creating Custom Schema

```python
from config.skill_registry import SkillOutputSchema

# Define output schema
output_schema = SkillOutputSchema(
    required_sections=["## Analysis", "## Verdict", "## Sources"],
    output_format="markdown"
)

# Validate output
output_text = """
## Analysis
Analysis content here...

## Verdict
Final verdict here...

## Sources
- Source 1
- Source 2
"""

is_valid, errors = output_schema.validate(output_text)
```

---

*This document defines all schemas used in the system. Add new schemas as features are added.*
