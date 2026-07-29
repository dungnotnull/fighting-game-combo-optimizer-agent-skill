"""
Quality Gates Module — Automated quality gate enforcement with auto-fix
Implements universal and domain-specific quality gates with retry logic and graceful degradation.
"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
import logging
import re

from config.skill_registry import SkillRegistry, get_registry

logger = logging.getLogger("fighting-game-combo-optimizer")


class GateStatus(str, Enum):
    """Status of a quality gate check."""
    PASSED = "passed"
    FAILED = "failed"
    AUTO_FIXED = "auto_fixed"
    LIMITATION_FLAGGED = "limitation_flagged"
    SKIPPED = "skipped"


@dataclass
class QualityGate:
    """
    A quality gate that checks output against criteria.
    """
    name: str
    description: str
    check_func: Callable[[str, Any], tuple[bool, List[str]]]
    auto_fix_func: Optional[Callable[[str, Any], Any]] = None
    max_retries: int = 2
    priority: int = 0  # Higher priority gates execute first
    universal: bool = False  # True for universal gates (U1-U6)
    domain_gate: bool = False  # True for domain gates (G1-G4)


@dataclass
class QualityGateResult:
    """
    Result of a quality gate check.
    """
    gate_name: str
    status: GateStatus
    passed: bool
    errors: List[str] = field(default_factory=list)
    auto_fixes_applied: List[str] = field(default_factory=list)
    duration_ms: float = 0.0
    retries: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "gate_name": self.gate_name,
            "status": self.status.value,
            "passed": self.passed,
            "errors": self.errors,
            "auto_fixes_applied": self.auto_fixes_applied,
            "duration_ms": self.duration_ms,
            "retries": self.retries,
            "metadata": self.metadata
        }


# Universal Gates (U1-U6)

def check_u1_sources(skill_name: str, output: Any) -> tuple[bool, List[str]]:
    """U1: Check ≥3 sources cited, ≥1 academic/authoritative."""
    errors = []

    # Extract sources from output
    sources = extract_sources(output)

    if len(sources) < 3:
        errors.append(f"U1: Need at least 3 sources, found {len(sources)}")

    academic_sources = [s for s in sources if is_academic_or_authoritative(s)]
    if len(academic_sources) < 1:
        errors.append("U1: Need at least 1 academic/authoritative source")

    return (len(errors) == 0, errors)


def check_u2_disclosure(skill_name: str, output: Any) -> tuple[bool, List[str]]:
    """U2: Check disclosure/limitations before recommendation."""
    errors = []

    if isinstance(output, dict):
        output_str = str(output.get("disclosure", "") + str(output.get("content", "")))
    else:
        output_str = str(output)

    # Check if disclosure exists
    if "disclosure" not in output_str.lower() and "limitation" not in output_str.lower():
        errors.append("U2: Disclosure/limitations section missing")

    # Check if disclosure appears before verdict/conclusion
    disclosure_pos = output_str.lower().find("disclosure")
    verdict_pos = output_str.lower().find("verdict")
    conclusion_pos = output_str.lower().find("conclusion")

    if verdict_pos > 0 or conclusion_pos > 0:
        first_verdict = min([p for p in [verdict_pos, conclusion_pos] if p > 0])
        if disclosure_pos < 0 or disclosure_pos > first_verdict:
            errors.append("U2: Disclosure must appear before verdict/conclusion")

    return (len(errors) == 0, errors)


def check_u3_evidence_hierarchy(skill_name: str, output: Any) -> tuple[bool, List[str]]:
    """U3: Check evidence hierarchy stated per source."""
    errors = []

    sources = extract_sources(output)

    for source in sources:
        if "tier" not in str(source).lower():
            errors.append(f"U3: Source missing tier label: {source}")

    return (len(errors) == 0, errors)


def check_u4_language_match(skill_name: str, output: Any) -> tuple[bool, List[str]]:
    """U4: Check language matches user preference."""
    # This would need context about user's language preference
    # For now, assume English (most common)
    errors = []

    # Basic check - if output contains Vietnamese characters, flag it
    vietnamese_chars = set('àáảãạăâèéêìíòóôơùúưý')
    output_str = str(output)

    has_vietnamese = any(char in vietnamese_chars for char in output_str.lower())

    # If mixed language detected, flag it
    if has_vietnamese and any(ord(c) < 128 for c in output_str):
        errors.append("U4: Mixed language detected - ensure consistent language")

    return (len(errors) == 0, errors)


def check_u5_output_format(skill_name: str, output: Any) -> tuple[bool, List[str]]:
    """U5: Check output uses declared template with all sections."""
    errors = []

    required_sections = [
        "## Analysis",
        "## Verdict",
        "## Sources",
        "## Disclosure"
    ]

    output_str = str(output)

    for section in required_sections:
        if section not in output_str:
            errors.append(f"U5: Missing required section: {section}")

    return (len(errors) == 0, errors)


def check_u6_claims_traced(skill_name: str, output: Any) -> tuple[bool, List[str]]:
    """U6: Check every claim traceable to source or flagged as judgment."""
    errors = []

    # This is a complex check - for now, do a basic check
    # Look for claims without sources or [analyst judgment] flags

    output_str = str(output)

    # Count assertion-like statements
    # Simple heuristic: sentences with "is", "are", "shows" that aren't sourced
    lines = output_str.split('\n')
    unsourced_claims = 0

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('>'):
            continue

        # Check if line makes a claim without source
        if any(word in line.lower() for word in ['is ', 'are ', 'shows ', 'indicates ']):
            if not any(marker in line for marker in ['[', 'source:', 'according to']):
                if '[analyst judgment]' not in line.lower():
                    unsourced_claims += 1

    if unsourced_claims > 5:
        errors.append(f"U6: {unsourced_claims} potentially unsourced claims found")

    return (len(errors) == 0, errors)


# Domain Gates (G1-G4)

def check_g1_frame_advantage(skill_name: str, output: Any) -> tuple[bool, List[str]]:
    """G1: Check frame advantage computed."""
    errors = []

    output_str = str(output)

    # Look for frame advantage calculations
    if "frame advantage" not in output_str.lower() and "on block" not in output_str.lower():
        errors.append("G1: Frame advantage not computed")

    # Check for numeric frame values
    if not re.search(r'[-+]?\d+\s*frames?', output_str, re.IGNORECASE):
        errors.append("G1: No frame data values found")

    return (len(errors) == 0, errors)


def check_g2_combo_optimized(skill_name: str, output: Any) -> tuple[bool, List[str]]:
    """G2: Check combo routes optimized for damage/meter."""
    errors = []

    output_str = str(output)

    # Look for combo routes and optimization
    if "combo" not in output_str.lower():
        errors.append("G2: No combo routes found")

    # Check for damage/meter metrics
    if not any(word in output_str.lower() for word in ['damage', 'meter', 'efficiency']):
        errors.append("G2: No damage/meter optimization metrics found")

    return (len(errors) == 0, errors)


def check_g3_punish_routes(skill_name: str, output: Any) -> tuple[bool, List[str]]:
    """G3: Check punish routes from frame data."""
    errors = []

    output_str = str(output)

    # Look for punish options
    if "punish" not in output_str.lower():
        errors.append("G3: No punish routes found")

    return (len(errors) == 0, errors)


def check_g4_execution_tradeoff(skill_name: str, output: Any) -> tuple[bool, List[str]]:
    """G4: Check execution difficulty vs consistency tradeoff noted."""
    errors = []

    output_str = str(output)

    # Look for execution discussion
    execution_terms = ['difficulty', 'consistency', 'execution', 'timing']
    if not any(term in output_str.lower() for term in execution_terms):
        errors.append("G4: Execution difficulty/consistency not discussed")

    return (len(errors) == 0, errors)


# Helper functions

def extract_sources(output: Any) -> List[str]:
    """Extract source citations from output."""
    sources = []
    output_str = str(output)

    # Look for common source patterns
    # URLs
    sources.extend(re.findall(r'https?://[^\s\)]+', output_str))
    # DOIs
    sources.extend(re.findall(r'doi:\s*10\.\S+', output_str, re.IGNORECASE))
    # Bracket citations
    sources.extend(re.findall(r'\[\d+\]', output_str))

    return list(set(sources))


def is_academic_or_authoritative(source: str) -> bool:
    """Check if source is academic or authoritative."""
    authoritative_patterns = [
        r'\.edu',
        r'arxiv\.org',
        r'scholar\.google',
        r'doi:',
        r'ieee\.org',
        r'acm\.org',
        r'springer\.com',
        r'elsevier\.com',
        r'pubmed\.ncbi\.nlm\.nih\.gov'
    ]

    for pattern in authoritative_patterns:
        if re.search(pattern, source, re.IGNORECASE):
            return True

    return False


# Gate definitions

UNIVERSAL_GATES = [
    QualityGate("U1", "≥3 sources cited, ≥1 academic/authoritative", check_u1_sources, universal=True),
    QualityGate("U2", "Disclosure/limitations before recommendation", check_u2_disclosure, universal=True),
    QualityGate("U3", "Evidence hierarchy stated per source", check_u3_evidence_hierarchy, universal=True),
    QualityGate("U4", "Language matches user preference", check_u4_language_match, universal=True),
    QualityGate("U5", "Output uses declared template", check_u5_output_format, universal=True),
    QualityGate("U6", "Every claim traceable to source or flagged", check_u6_claims_traced, universal=True),
]

DOMAIN_GATES = [
    QualityGate("G1", "Frame advantage computed", check_g1_frame_advantage, domain_gate=True),
    QualityGate("G2", "Combo routes optimized for damage/meter", check_g2_combo_optimized, domain_gate=True),
    QualityGate("G3", "Punish routes from frame data", check_g3_punish_routes, domain_gate=True),
    QualityGate("G4", "Execution difficulty vs consistency tradeoff noted", check_g4_execution_tradeoff, domain_gate=True),
]

ALL_GATES = UNIVERSAL_GATES + DOMAIN_GATES


def apply_quality_gates(
    skill_name: str,
    output: Any,
    strict: bool = True,
    gates: Optional[List[QualityGate]] = None
) -> List[QualityGateResult]:
    """
    Apply quality gates to skill output.

    Args:
        skill_name: Name of the skill
        output: Output to check
        strict: Whether to enforce all gates (default: True)
        gates: Custom list of gates (if None, uses all gates)

    Returns:
        list: Results for each gate
    """
    if gates is None:
        gates = ALL_GATES

    # Sort by priority (higher priority first)
    gates = sorted(gates, key=lambda g: g.priority, reverse=True)

    results = []

    for gate in gates:
        start_time = time.perf_counter()

        result = QualityGateResult(
            gate_name=gate.name,
            status=GateStatus.PASSED,
            passed=True,
            retries=0
        )

        # Check gate with retries
        for attempt in range(gate.max_retries + 1):
            try:
                passed, errors = gate.check_func(skill_name, output)

                if passed:
                    result.status = GateStatus.PASSED
                    result.passed = True
                    result.retries = attempt
                    break
                else:
                    # Try to auto-fix
                    if gate.auto_fix_func and attempt < gate.max_retries:
                        output = gate.auto_fix_func(skill_name, output)
                        result.auto_fixes_applied.append(f"Auto-fix attempt {attempt + 1}")
                        result.retries = attempt + 1
                    else:
                        result.status = GateStatus.FAILED
                        result.passed = False
                        result.errors = errors
                        result.retries = attempt

                        if not strict:
                            result.status = GateStatus.LIMITATION_FLAGGED
                        break

            except Exception as e:
                result.errors.append(f"Gate check error: {e}")
                result.status = GateStatus.FAILED
                result.passed = False
                break

        result.duration_ms = (time.perf_counter() - start_time) * 1000
        results.append(result)

    return results


def get_gate_statistics(results: List[QualityGateResult]) -> Dict[str, Any]:
    """
    Get statistics from gate results.

    Args:
        results: Gate results to analyze

    Returns:
        dict: Statistics summary
    """
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)
    auto_fixed = sum(1 for r in results if r.status == GateStatus.AUTO_FIXED)

    return {
        "total_gates": len(results),
        "passed": passed,
        "failed": failed,
        "auto_fixed": auto_fixed,
        "pass_rate": passed / len(results) if results else 0.0,
        "total_retries": sum(r.retries for r in results),
        "total_duration_ms": sum(r.duration_ms for r in results)
    }
