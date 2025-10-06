# Data Model: JD Parser Module

**Feature**: 001-jd-parser-module
**Date**: 2025-10-05

This document defines the data entities for the JD Parser module.

---

## Entity Diagram

```
FreeTextInput
    |
    | (parsed by JDParser)
    ↓
JobRequirement
    |
    | (contains)
    ↓
ConfidenceScore (per field)
```

---

## Entities

### 1. FreeTextInput (Input)

**Purpose**: Represents the raw user-provided job description text.

**Fields**:
| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `text` | `str` | Yes | `minLength: 1`, unlimited max | The JD text in English |
| `language` | `str` | No | `enum: ["en"]`, default: `"en"` | Input language (English-only for POC) |
| `submitted_at` | `datetime` | Auto | ISO 8601 format | Timestamp of submission |

**Validation Rules**:
- `text` must not be empty
- `language` must be "en" (enforced in POC)
- `submitted_at` auto-generated on creation

**Pydantic Model**:
```python
from pydantic import BaseModel, Field
from datetime import datetime

class FreeTextInput(BaseModel):
    text: str = Field(..., min_length=1, description="Free-text job description in English")
    language: str = Field(default="en", pattern="^en$")
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### 2. JobRequirement (Output)

**Purpose**: Represents the structured candidate requirements extracted from the JD.

**Fields**:
| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `role` | `str \| null` | Yes | Can be null | Job title (e.g., "Senior Backend Engineer") |
| `required_skills` | `list[str]` | Yes | `minItems: 0` | Must-have technical skills (normalized) |
| `preferred_skills` | `list[str]` | Yes | `minItems: 0` | Nice-to-have skills (normalized) |
| `years_of_experience` | `YearsOfExperience` | Yes | Nested object | Experience range or minimum |
| `seniority_level` | `str \| null` | Yes | Enum or null | Junior, Mid-level, Senior, Staff, Principal |
| `location_preferences` | `list[str]` | Yes | `minItems: 0` | Cities, countries, or "remote" |
| `domain` | `str \| null` | Yes | Can be null | Industry context (e.g., "fintech") |
| `confidence_scores` | `dict[str, ConfidenceScore]` | Yes | Keys match field names | Per-field confidence metadata |
| `original_input` | `str` | Yes | Non-empty | Raw JD text for reference |
| `schema_version` | `str` | Yes | Semver pattern `^\d+\.\d+\.\d+$` | Output schema version |

**Validation Rules** (FR-011):
1. If `role` is null AND `required_skills` is empty → **validation error**
2. If `seniority_level` provided, must be from enum: `["Junior", "Mid-level", "Senior", "Staff", "Principal"]`
3. If `years_of_experience.min` and `years_of_experience.max` both provided: `min <= max`
4. `confidence_scores` keys must exist in extracted fields
5. `schema_version` must follow semver (e.g., "1.0.0")

**Pydantic Model**:
```python
from typing import Optional
from pydantic import BaseModel, Field, model_validator

class JobRequirement(BaseModel):
    role: Optional[str] = None
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    years_of_experience: "YearsOfExperience"
    seniority_level: Optional[str] = Field(None, pattern="^(Junior|Mid-level|Senior|Staff|Principal)$")
    location_preferences: list[str] = Field(default_factory=list)
    domain: Optional[str] = None
    confidence_scores: dict[str, "ConfidenceScore"]
    original_input: str
    schema_version: str = Field(default="1.0.0", pattern=r"^\d+\.\d+\.\d+$")

    @model_validator(mode='after')
    def validate_minimum_fields(self):
        if not self.role and len(self.required_skills) == 0:
            raise ValueError("At least one of 'role' or 'required_skills' must be present")
        return self
```

---

### 3. YearsOfExperience (Nested)

**Purpose**: Represents experience range or minimum years.

**Fields**:
| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `min` | `int \| null` | No | `>= 0` if provided | Minimum years |
| `max` | `int \| null` | No | `>= 0` if provided | Maximum years |
| `range_text` | `str \| null` | No | Free text | Original text (e.g., "5+ years") |

**Validation Rules**:
- If both `min` and `max` provided: `min <= max`
- At least one of `min`, `max`, or `range_text` should be present (can all be null if not mentioned in JD)

**Pydantic Model**:
```python
class YearsOfExperience(BaseModel):
    min: Optional[int] = Field(None, ge=0)
    max: Optional[int] = Field(None, ge=0)
    range_text: Optional[str] = None

    @model_validator(mode='after')
    def validate_range(self):
        if self.min is not None and self.max is not None:
            if self.min > self.max:
                raise ValueError(f"min ({self.min}) cannot be greater than max ({self.max})")
        return self
```

---

### 4. ConfidenceScore (Nested)

**Purpose**: Represents confidence metadata for each extracted field.

**Fields**:
| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `score` | `int` | Yes | `0-100` inclusive | Confidence level (higher = more confident) |
| `reasoning` | `str` | Yes | `minLength: 1` | Why this score? (e.g., "Explicitly stated") |
| `highlighted_spans` | `list[TextSpan]` | No | Can be empty | Text spans that contributed to extraction |

**Validation Rules**:
- `score` must be between 0 and 100
- `reasoning` must not be empty
- `highlighted_spans` can be empty if no specific text matched

**Pydantic Model**:
```python
class TextSpan(BaseModel):
    start: int = Field(..., ge=0, description="Start index in original text")
    end: int = Field(..., ge=0, description="End index in original text")
    text: str

class ConfidenceScore(BaseModel):
    score: int = Field(..., ge=0, le=100, description="Confidence 0-100")
    reasoning: str = Field(..., min_length=1)
    highlighted_spans: list[TextSpan] = Field(default_factory=list)
```

---

### 5. SkillNormalizationMapping (Configuration)

**Purpose**: Maps skill variations to canonical names.

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `canonical_name` | `str` | Yes | Official skill name (e.g., "JavaScript") |
| `aliases` | `list[str]` | Yes | Variations (e.g., ["JS", "javascript", "ECMAScript"]) |
| `category` | `str \| null` | No | Type: "language", "framework", "tool", etc. |

**Example JSON** (`src/config/skill_mappings.json`):
```json
{
  "mappings": [
    {
      "canonical_name": "JavaScript",
      "aliases": ["js", "javascript", "ecmascript", "es6", "es2015"],
      "category": "language"
    },
    {
      "canonical_name": "React",
      "aliases": ["react", "reactjs", "react.js"],
      "category": "framework"
    },
    {
      "canonical_name": ".NET Core",
      "aliases": ["dotnet", ".net", "asp.net", "aspnet", "dotnet core"],
      "category": "framework"
    }
  ]
}
```

---

## Relationships

1. **FreeTextInput → JobRequirement** (1:1)
   - One input generates one output
   - `original_input` field preserves raw text

2. **JobRequirement → ConfidenceScore** (1:many)
   - One score per extracted field
   - Stored as dict with field names as keys

3. **SkillNormalizationMapping** (configuration)
   - Loaded once at startup
   - Used to normalize skills in `JobRequirement`

---

## State Transitions

```
[User Input] → [FreeTextInput created]
    ↓
[LLM Processing] → [Raw extraction]
    ↓
[Skill Normalization] → [Skills mapped to canonical forms]
    ↓
[Validation] → [JobRequirement validated]
    ↓
[Output] → [JSON returned to caller]
```

**Error States**:
- Input validation fails → Return 400 error with details
- LLM extraction returns invalid JSON → Retry or return 500 error
- Minimum fields not met (role + skill) → Return 422 error with guidance

---

## JSON Examples

### Minimal Valid Input
```json
{
  "text": "react developer"
}
```

### Full Valid Output
```json
{
  "role": "React Developer",
  "required_skills": ["React"],
  "preferred_skills": [],
  "years_of_experience": {
    "min": null,
    "max": null,
    "range_text": null
  },
  "seniority_level": null,
  "location_preferences": [],
  "domain": null,
  "confidence_scores": {
    "role": {
      "score": 85,
      "reasoning": "Inferred from 'developer' keyword",
      "highlighted_spans": [{"start": 6, "end": 15, "text": "developer"}]
    },
    "required_skills": {
      "score": 95,
      "reasoning": "Explicitly mentioned technology",
      "highlighted_spans": [{"start": 0, "end": 5, "text": "react"}]
    }
  },
  "original_input": "react developer",
  "schema_version": "1.0.0"
}
```
