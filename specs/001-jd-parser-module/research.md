# Research: JD Parser Module

**Feature**: 001-jd-parser-module
**Date**: 2025-10-05

## Research Questions

This document captures technology decisions and research findings for the JD Parser module.

---

## 1. LLM Provider Choice

**Question**: Which LLM provider to use? (OpenAI GPT-4, Anthropic Claude, or both?)

**Decision**: Support both OpenAI and Anthropic with abstraction layer

**Rationale**:
- **Constitution Requirement**: Principle I (AI-First Development) mandates "AI components MUST be modular and replaceable (support for different LLM providers)"
- **Provider Strengths**:
  - OpenAI GPT-4: Excellent function calling, JSON mode for structured outputs
  - Anthropic Claude: Superior long-context handling (up to 200k tokens), better at following complex instructions
- **Flexibility**: Abstraction layer (`llm_client.py`) allows:
  - A/B testing between providers
  - Fallback logic if one provider fails or hits rate limits
  - Future integration of additional providers (e.g., local models)
- **Risk Mitigation**: No vendor lock-in, can switch providers without rewriting parser logic

**Alternatives Considered**:
- **Single provider (OpenAI only)**: Simpler implementation, but violates constitution's modularity requirement
- **Open-source models (Llama, Mistral)**: Cost-effective, but lower quality extraction (especially for confidence scoring and edge cases)

**Implementation Approach**:
```python
# Abstract LLM client interface
class LLMClient(ABC):
    @abstractmethod
    def extract_jd(self, text: str) -> dict:
        pass

# Concrete implementations
class OpenAIClient(LLMClient): ...
class AnthropicClient(LLMClient): ...

# Factory pattern for selection
def get_llm_client(provider: str) -> LLMClient: ...
```

---

## 2. Prompting Technique

**Question**: What prompting technique for structured extraction? (Few-shot, function calling, JSON mode?)

**Decision**: Use structured output/JSON mode with few-shot examples

**Rationale**:
- **OpenAI JSON Mode**: Guarantees valid JSON output (uses `response_format={"type": "json_object"}`)
- **Anthropic Structured Output**: Achieves similar results via careful prompt engineering with JSON schema in prompt
- **Few-Shot Examples**: Improves extraction accuracy by 20-30% (based on OpenAI documentation)
  - Include examples for:
    - Minimal input ("react developer")
    - Formal JD (multi-paragraph)
    - Abbreviated format ("Sr. SWE, 5yoe, Python/Go")
- **Confidence Scoring**: Requires explicit instruction in prompt to explain reasoning for each field

**Alternatives Considered**:
- **Function Calling** (OpenAI-specific):
  - Pros: Structured, type-safe
  - Cons: Not portable to Anthropic, less flexible for confidence metadata
- **Pure Prompt Engineering**:
  - Pros: Provider-agnostic
  - Cons: Less reliable JSON formatting, requires extensive post-processing

**Prompt Structure**:
```
You are a job description parser. Extract structured candidate requirements from the following JD.

Output must be valid JSON matching this schema:
{schema here}

Examples:
Input: "senior python developer..."
Output: {...}

Now extract from this JD:
{user_input}
```

---

## 3. Skill Normalization

**Question**: How to handle skill normalization? (Static dictionary vs dynamic LLM-based?)

**Decision**: Static dictionary with LLM fallback for unknowns

**Rationale**:
- **Static Mappings** (`src/config/skill_mappings.json`):
  - Fast (O(1) lookup)
  - Deterministic (same input → same output)
  - Explainable (constitution requirement for transparency)
  - Covers ~200 common skills (JS, React, Python, etc.)
- **LLM Fallback**:
  - Handles new/emerging technologies (htmx, bun, deno, etc.)
  - Infers canonical form for typos/variations
  - Only invoked when static lookup misses
- **Hybrid Benefits**:
  - Speed: 90%+ hits on static dictionary (no LLM call)
  - Coverage: LLM handles long tail
  - Transparency: Log which normalization method was used

**Alternatives Considered**:
- **Pure LLM**: Flexible but slow (extra API call per skill), non-deterministic
- **Manual-only**: Fast but incomplete (can't handle new skills)
- **Edit Distance**: Fast but error-prone ("Java" vs "JavaScript" have low edit distance but are different)

**Implementation**:
```python
class SkillNormalizer:
    def __init__(self, mappings_file: str, llm_client: LLMClient):
        self.static_map = load_mappings(mappings_file)
        self.llm = llm_client

    def normalize(self, skill: str) -> str:
        # 1. Try static lookup
        if skill.lower() in self.static_map:
            return self.static_map[skill.lower()]

        # 2. Fallback to LLM
        return self.llm.normalize_skill(skill)
```

---

## 4. Testing with LLM APIs

**Question**: How to ensure deterministic testing with LLM APIs? (Mocking strategy?)

**Decision**: Mock LLM responses using pytest fixtures + contract tests

**Rationale**:
- **Unit Tests**: Use mock responses (pytest-mock or unittest.mock)
  - Deterministic: Same input → same output
  - Fast: No API calls
  - Free: No API costs
  - Example: Mock `llm_client.extract_jd()` to return predefined JSON
- **Integration Tests**: Use real API with response caching (optional)
  - Verify actual LLM behavior
  - Run less frequently (e.g., nightly builds)
  - Cache responses to avoid repeated costs
- **Contract Tests**: Validate schema compliance
  - Ensure output matches JSON schema regardless of LLM provider
  - Catch breaking changes in LLM responses

**Alternatives Considered**:
- **VCR.py** (cassette-based recording):
  - Pros: Records real responses, replays deterministically
  - Cons: Initial recording still costs money, brittle to prompt changes
- **No mocking** (always call real API):
  - Pros: Tests real behavior
  - Cons: Slow (~1-2s per test), expensive ($$$), non-deterministic

**Test Structure**:
```python
# Unit test with mock
def test_parse_jd_minimal_input(mock_llm_client):
    mock_llm_client.extract_jd.return_value = {
        "role": "React Developer",
        "required_skills": ["React"],
        ...
    }
    parser = JDParser(llm_client=mock_llm_client)
    result = parser.parse("react developer")
    assert result.role == "React Developer"

# Contract test (no mocks)
def test_output_matches_schema():
    parser = JDParser(llm_client=real_client)
    result = parser.parse("python developer")
    validate(instance=result.dict(), schema=output_schema)  # jsonschema validation
```

---

## 5. Pydantic Version

**Question**: What Pydantic version for data validation? (v1 vs v2?)

**Decision**: Pydantic v2 (latest stable)

**Rationale**:
- **Performance**: 5-50x faster than v1 (Rust-based validation)
- **JSON Schema**: Native `model_json_schema()` method (FR-010 requires JSON schema output)
- **Validation Errors**: Improved error messages (better debugging for users)
- **Type Safety**: Stricter validation, catches more bugs at runtime
- **Future-Proof**: v1 is in maintenance mode, v2 is actively developed

**Alternatives Considered**:
- **Pydantic v1**:
  - Pros: More established, wider ecosystem compatibility
  - Cons: Slower, v2 has breaking changes anyway (might as well migrate now)
- **Dataclasses**:
  - Pros: Standard library, no dependencies
  - Cons: No validation, no JSON schema generation

**Migration Notes**:
- Use `BaseModel` from `pydantic` (same in v1/v2)
- Use `model_dump()` instead of `dict()` (v2 naming)
- Use `model_validate()` instead of `parse_obj()` (v2 naming)

---

## Summary

**Core Stack**:
- **Language**: Python 3.11+
- **LLM Providers**: OpenAI + Anthropic (abstracted)
- **Data Validation**: Pydantic v2
- **Testing**: pytest (with mocking for unit tests)
- **Skill Normalization**: Static dictionary + LLM fallback

**Key Dependencies**:
```
openai>=1.0.0
anthropic>=0.18.0
pydantic>=2.0.0
pytest>=7.4.0
pytest-mock>=3.11.0
```

**Performance Targets**:
- Typical JD (500-2000 chars): <2 seconds
- Large JD (10,000+ chars): <5 seconds
- Skill normalization (static): <0.01 seconds
- Skill normalization (LLM fallback): ~0.5 seconds

**Next Steps**:
- Create data models (Pydantic)
- Define JSON schemas (contracts/)
- Write contract tests
- Implement LLM abstraction layer
- Build JDParser class
