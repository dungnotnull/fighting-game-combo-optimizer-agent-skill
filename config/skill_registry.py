"""
Skill Registry Module — Dynamic skill registration, resolution, and execution
Provides a flexible skill management system with registration, resolution, validation, and execution workflows.
"""

import os
import json
import hashlib
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Callable, Type, TypeVar
from enum import Enum
from pathlib import Path
import re


class SkillStatus(str, Enum):
    """Status of a skill in the registry."""
    REGISTERED = "registered"
    LOADED = "loaded"
    VALIDATED = "validated"
    DISABLED = "disabled"
    ERROR = "error"


class TriggerType(str, Enum):
    """Types of skill triggering mechanisms."""
    MANUAL = "manual"  # Explicit invocation via /skill-name
    KEYWORD = "keyword"  # Triggered by keyword matching
    CONTEXT = "context"  # Triggered by context analysis
    AUTO = "auto"  # Automatically triggered by the system


@dataclass
class SkillInputSchema:
    """
    Input schema definition for a skill.
    Defines the expected structure, types, and validation rules for skill inputs.
    """
    required_fields: List[str] = field(default_factory=list)
    optional_fields: Dict[str, Any] = field(default_factory=dict)
    field_types: Dict[str, str] = field(default_factory=dict)
    validation_rules: Dict[str, Any] = field(default_factory=dict)

    def validate(self, input_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate input data against the schema.

        Args:
            input_data: Input data to validate

        Returns:
            tuple: (is_valid, error_messages)
        """
        errors = []

        # Check required fields
        for field_name in self.required_fields:
            if field_name not in input_data:
                errors.append(f"Missing required field: {field_name}")

        # Check field types if specified
        for field_name, expected_type in self.field_types.items():
            if field_name in input_data:
                value = input_data[field_name]
                if not self._check_type(value, expected_type):
                    errors.append(
                        f"Field '{field_name}' has incorrect type. "
                        f"Expected {expected_type}, got {type(value).__name__}"
                    )

        # Apply validation rules
        for field_name, rule in self.validation_rules.items():
            if field_name in input_data:
                if not self._apply_validation(input_data[field_name], rule):
                    errors.append(
                        f"Field '{field_name}' failed validation: {rule}"
                    )

        return (len(errors) == 0, errors)

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type."""
        type_map = {
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
            "any": type(None)  # Accept any type
        }

        expected = type_map.get(expected_type)
        if expected is None:
            return True  # Unknown type, accept

        if expected_type == "any":
            return True

        return isinstance(value, expected)

    def _apply_validation(self, value: Any, rule: Any) -> bool:
        """Apply validation rule to a value."""
        if isinstance(rule, dict):
            if "min" in rule and isinstance(value, (int, float)):
                if value < rule["min"]:
                    return False
            if "max" in rule and isinstance(value, (int, float)):
                if value > rule["max"]:
                    return False
            if "pattern" in rule and isinstance(value, str):
                if not re.match(rule["pattern"], value):
                    return False
            if "enum" in rule:
                if value not in rule["enum"]:
                    return False

        return True


@dataclass
class SkillOutputSchema:
    """
    Output schema definition for a skill.
    Defines the expected structure and types for skill outputs.
    """
    required_sections: List[str] = field(default_factory=list)
    output_format: str = "markdown"  # markdown, json, html
    field_types: Dict[str, str] = field(default_factory=dict)

    def validate(self, output_data: Any) -> tuple[bool, List[str]]:
        """
        Validate output data against the schema.

        Args:
            output_data: Output data to validate

        Returns:
            tuple: (is_valid, error_messages)
        """
        errors = []

        if self.output_format == "json":
            if not isinstance(output_data, dict):
                errors.append(f"Expected JSON output, got {type(output_data).__name__}")
                return (False, errors)

            # Check required fields
            for field in self.required_sections:
                if field not in output_data:
                    errors.append(f"Missing required output field: {field}")

        elif self.output_format == "markdown":
            if not isinstance(output_data, str):
                errors.append(f"Expected markdown string output, got {type(output_data).__name__}")
                return (False, errors)

            # Check for required sections
            for section in self.required_sections:
                if section not in output_data:
                    errors.append(f"Missing required section: {section}")

        return (len(errors) == 0, errors)


@dataclass
class SkillMetadata:
    """
    Metadata for a registered skill.
    """
    name: str
    description: str
    version: str = "1.0.0"
    author: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    trigger_type: TriggerType = TriggerType.MANUAL
    status: SkillStatus = SkillStatus.REGISTERED
    dependencies: List[str] = field(default_factory=list)
    file_path: Optional[str] = None

    # Quality gate configuration
    has_quality_gates: bool = False
    gate_definitions: List[str] = field(default_factory=list)

    # Schemas
    input_schema: Optional[SkillInputSchema] = None
    output_schema: Optional[SkillOutputSchema] = None

    # Trigger keywords (for keyword-based triggering)
    trigger_keywords: List[str] = field(default_factory=list)
    trigger_threshold: float = 0.7  # Confidence threshold for triggering

    # Execution metadata
    execution_count: int = 0
    average_duration_ms: float = 0.0
    average_tokens: int = 0
    success_rate: float = 1.0
    last_execution: Optional[str] = None

    def compute_content_hash(self) -> str:
        """Compute a hash of the skill content for caching/validation."""
        content = f"{self.name}:{self.description}:{self.version}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def should_trigger(self, query: str, context: Optional[Dict] = None) -> float:
        """
        Calculate trigger confidence for a given query.

        Args:
            query: User query to check
            context: Optional context information

        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        if self.trigger_type == TriggerType.MANUAL:
            # Manual skills don't auto-trigger
            return 0.0

        query_lower = query.lower()

        # Keyword matching
        if self.trigger_keywords:
            matches = sum(
                1 for keyword in self.trigger_keywords
                if keyword.lower() in query_lower
            )
            if matches > 0:
                # Score based on number of keyword matches
                return min(matches / len(self.trigger_keywords), 1.0)

        # Description matching (fallback)
        desc_words = set(self.description.lower().split())
        query_words = set(query_lower.split())
        overlap = desc_words & query_words

        if overlap:
            return len(overlap) / max(len(query_words), 1)

        return 0.0


T = TypeVar('T', bound=Callable)


class SkillRegistry:
    """
    Central registry for managing skills in the system.
    Provides registration, resolution, validation, and execution workflows.
    """

    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize the skill registry.

        Args:
            project_root: Root path of the project (for finding skill files)
        """
        if project_root is None:
            project_root = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )

        self.project_root = Path(project_root)
        self.skills_dir = self.project_root / "skills"

        # Registered skills by name
        self._skills: Dict[str, SkillMetadata] = {}

        # Trigger index (for fast lookups)
        self._trigger_index: Dict[str, List[str]] = {}

        # Execution hooks
        self._pre_execution_hooks: List[Callable] = []
        self._post_execution_hooks: List[Callable] = []

        # Load skills from directory if it exists
        if self.skills_dir.exists():
            self._discover_skills()

    def register_skill(
        self,
        metadata: SkillMetadata,
        validate: bool = True
    ) -> bool:
        """
        Register a skill in the registry.

        Args:
            metadata: Skill metadata to register
            validate: Whether to validate the skill

        Returns:
            bool: True if registration succeeded
        """
        # Validate skill if requested
        if validate and metadata.file_path:
            if not self._validate_skill_file(metadata.file_path):
                metadata.status = SkillStatus.ERROR
                return False

        # Add to registry
        self._skills[metadata.name] = metadata
        metadata.status = SkillStatus.REGISTERED

        # Update trigger index
        for keyword in metadata.trigger_keywords:
            if keyword not in self._trigger_index:
                self._trigger_index[keyword] = []
            self._trigger_index[keyword].append(metadata.name)

        return True

    def resolve_skill(
        self,
        name: Optional[str] = None,
        query: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Optional[SkillMetadata]:
        """
        Resolve a skill by name or query.

        Args:
            name: Exact skill name to resolve
            query: Query for automatic skill resolution
            context: Optional context for resolution

        Returns:
            SkillMetadata: Resolved skill metadata or None
        """
        # Exact name match
        if name:
            return self._skills.get(name)

        # Query-based resolution
        if query:
            candidates = []

            for skill_name, metadata in self._skills.items():
                confidence = metadata.should_trigger(query, context)
                if confidence >= metadata.trigger_threshold:
                    candidates.append((confidence, skill_name))

            if candidates:
                # Sort by confidence and return highest
                candidates.sort(key=lambda x: x[0], reverse=True)
                return self._skills[candidates[0][1]]

        return None

    def get_skill(self, name: str) -> Optional[SkillMetadata]:
        """
        Get a skill by name.

        Args:
            name: Skill name

        Returns:
            SkillMetadata: Skill metadata or None if not found
        """
        return self._skills.get(name)

    def list_skills(
        self,
        status: Optional[SkillStatus] = None,
        tag: Optional[str] = None
    ) -> List[SkillMetadata]:
        """
        List registered skills with optional filtering.

        Args:
            status: Filter by status
            tag: Filter by tag

        Returns:
            list: Filtered list of skill metadata
        """
        skills = list(self._skills.values())

        if status:
            skills = [s for s in skills if s.status == status]

        if tag:
            skills = [s for s in skills if tag in s.tags]

        return skills

    def validate_skill_input(
        self,
        skill_name: str,
        input_data: Dict[str, Any]
    ) -> tuple[bool, List[str]]:
        """
        Validate input data for a skill.

        Args:
            skill_name: Name of the skill
            input_data: Input data to validate

        Returns:
            tuple: (is_valid, error_messages)
        """
        skill = self.get_skill(skill_name)
        if not skill or not skill.input_schema:
            return (True, [])  # No validation available, accept

        return skill.input_schema.validate(input_data)

    def validate_skill_output(
        self,
        skill_name: str,
        output_data: Any
    ) -> tuple[bool, List[str]]:
        """
        Validate output data for a skill.

        Args:
            skill_name: Name of the skill
            output_data: Output data to validate

        Returns:
            tuple: (is_valid, error_messages)
        """
        skill = self.get_skill(skill_name)
        if not skill or not skill.output_schema:
            return (True, [])  # No validation available, accept

        return skill.output_schema.validate(output_data)

    def record_execution(
        self,
        skill_name: str,
        duration_ms: float,
        tokens_used: int,
        success: bool
    ):
        """
        Record execution statistics for a skill.

        Args:
            skill_name: Name of the skill
            duration_ms: Execution duration in milliseconds
            tokens_used: Tokens consumed
            success: Whether execution succeeded
        """
        skill = self.get_skill(skill_name)
        if not skill:
            return

        skill.execution_count += 1
        skill.last_execution = str(os.times())

        # Update averages
        n = skill.execution_count
        skill.average_duration_ms = (
            (skill.average_duration_ms * (n - 1) + duration_ms) / n
        )
        skill.average_tokens = (
            (skill.average_tokens * (n - 1) + tokens_used) / n
        )

        # Update success rate
        if not success:
            skill.success_rate = (skill.success_rate * (n - 1)) / n
        else:
            skill.success_rate = (
                (skill.success_rate * (n - 1) + 1.0) / n
            )

    def add_pre_execution_hook(self, hook: Callable):
        """Add a pre-execution hook."""
        self._pre_execution_hooks.append(hook)

    def add_post_execution_hook(self, hook: Callable):
        """Add a post-execution hook."""
        self._post_execution_hooks.append(hook)

    def _discover_skills(self):
        """Discover and register skills from the skills directory."""
        if not self.skills_dir.exists():
            return

        # Find all .md files in the skills directory
        for skill_file in self.skills_dir.glob("*.md"):
            self._parse_and_register_skill(skill_file)

        # Also look for subdirectories
        for subdir in self.skills_dir.iterdir():
            if subdir.is_dir():
                for skill_file in subdir.glob("*.md"):
                    self._parse_and_register_skill(skill_file)

    def _parse_and_register_skill(self, skill_file: Path):
        """Parse a skill file and register it."""
        try:
            content = skill_file.read_text(encoding="utf-8")

            # Parse YAML frontmatter
            frontmatter_match = re.match(
                r"^---\n(.*?)\n---",
                content,
                re.DOTALL
            )

            if not frontmatter_match:
                return

            frontmatter_text = frontmatter_match.group(1)
            metadata = {}

            # Simple YAML parsing (for the fields we need)
            for line in frontmatter_text.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip()

            name = metadata.get("name", skill_file.stem)
            description = metadata.get("description", "")

            # Create SkillMetadata
            skill_metadata = SkillMetadata(
                name=name,
                description=description,
                version=metadata.get("version", "1.0.0"),
                author=metadata.get("author"),
                file_path=str(skill_file)
            )

            # Register the skill
            self.register_skill(skill_metadata)

        except Exception as e:
            print(f"[WARN] Failed to parse skill file {skill_file}: {e}")

    def _validate_skill_file(self, file_path: str) -> bool:
        """Validate a skill file for correctness."""
        path = Path(file_path)

        if not path.exists():
            return False

        content = path.read_text(encoding="utf-8")

        # Basic checks
        if not content.strip():
            return False

        if "---" not in content:
            return False

        return True

    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        return {
            "total_skills": len(self._skills),
            "registered": len([s for s in self._skills.values() if s.status == SkillStatus.REGISTERED]),
            "loaded": len([s for s in self._skills.values() if s.status == SkillStatus.LOADED]),
            "disabled": len([s for s in self._skills.values() if s.status == SkillStatus.DISABLED]),
            "total_executions": sum(s.execution_count for s in self._skills.values()),
            "average_success_rate": (
                sum(s.success_rate for s in self._skills.values()) / max(len(self._skills), 1)
            )
        }

    def export_registry(self, output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Export the registry to JSON.

        Args:
            output_file: Optional file path to write to

        Returns:
            dict: Registry data as dictionary
        """
        export_data = {
            "version": "1.0.0",
            "export_date": str(os.times()),
            "statistics": self.get_statistics(),
            "skills": {
                name: {
                    "name": metadata.name,
                    "description": metadata.description,
                    "version": metadata.version,
                    "author": metadata.author,
                    "tags": metadata.tags,
                    "status": metadata.status.value,
                    "dependencies": metadata.dependencies,
                    "trigger_type": metadata.trigger_type.value,
                    "trigger_keywords": metadata.trigger_keywords,
                    "execution_count": metadata.execution_count,
                    "average_duration_ms": metadata.average_duration_ms,
                    "average_tokens": metadata.average_tokens,
                    "success_rate": metadata.success_rate,
                }
                for name, metadata in self._skills.items()
            }
        }

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

        return export_data


# Global registry instance
_registry: Optional[SkillRegistry] = None


def get_registry() -> SkillRegistry:
    """Get the global skill registry instance (singleton)."""
    global _registry
    if _registry is None:
        _registry = SkillRegistry()
    return _registry


def register_skill(metadata: SkillMetadata) -> bool:
    """Convenience function to register a skill."""
    return get_registry().register_skill(metadata)


def resolve_skill(
    name: Optional[str] = None,
    query: Optional[str] = None,
    context: Optional[Dict] = None
) -> Optional[SkillMetadata]:
    """Convenience function to resolve a skill."""
    return get_registry().resolve_skill(name, query, context)


def reset_registry():
    """Reset the global registry instance (mainly for testing)."""
    global _registry
    _registry = None
