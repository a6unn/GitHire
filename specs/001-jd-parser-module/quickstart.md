# Quickstart: JD Parser Module

**Feature**: 001-jd-parser-module
**Date**: 2025-10-05

This document contains manual test scenarios for validating the JD Parser module.

---

## Test Scenarios

These scenarios are derived from the acceptance criteria in the feature spec.

### Scenario 1: Full JD Parsing

**Input**:
```
senior python developer with 5+ years in fintech using fastapi and postgresql
```

**Expected Output**:
```json
{
  "role": "Senior Python Developer",
  "required_skills": ["Python", "FastAPI", "PostgreSQL"],
  "preferred_skills": [],
  "years_of_experience": {
    "min": 5,
    "max": null,
    "range_text": "5+ years"
  },
  "seniority_level": "Senior",
  "location_preferences": [],
  "domain": "fintech",
  "confidence_scores": {
    "role": {"score": 95, "reasoning": "Explicitly stated with seniority", ...},
    "required_skills": {"score": 95, "reasoning": "Technologies explicitly mentioned", ...},
    "years_of_experience": {"score": 90, "reasoning": "Clear numeric requirement", ...},
    "domain": {"score": 90, "reasoning": "Industry explicitly stated", ...}
  },
  "original_input": "senior python developer with 5+ years in fintech using fastapi and postgresql",
  "schema_version": "1.0.0"
}
```

**Validation**:
- ✅ Role extracted correctly
- ✅ Skills normalized (fastapi → FastAPI, postgresql → PostgreSQL)
- ✅ Experience parsed as minimum
- ✅ Seniority identified
- ✅ Domain extracted

---

### Scenario 2: Minimal Input

**Input**:
```
react developer
```

**Expected Output**:
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
    "role": {"score": 80, "reasoning": "Inferred from 'developer' keyword", ...},
    "required_skills": {"score": 95, "reasoning": "Explicit technology mention", ...}
  },
  "original_input": "react developer",
  "schema_version": "1.0.0"
}
```

**Validation**:
- ✅ Minimum viable input (role + skill) satisfied
- ✅ Missing fields are null/empty arrays
- ✅ Lower confidence for inferred role

---

### Scenario 3: Missing Required Fields (Validation Error)

**Input**:
```
backend experience needed
```

**Expected Output**:
```
ValidationError: At least one of 'role' or 'required_skills' must be present
```

**Validation**:
- ✅ Parser rejects input lacking both role and specific skills
- ✅ Error message guides user to provide more details

---

### Scenario 4: Ambiguous Input with Low Confidence

**Input**:
```
developer with some backend experience
```

**Expected Output** (if role="Developer" can be inferred):
```json
{
  "role": "Developer",
  "required_skills": [],
  "preferred_skills": [],
  "years_of_experience": {
    "min": null,
    "max": null,
    "range_text": "some experience"
  },
  "seniority_level": null,
  "location_preferences": [],
  "domain": null,
  "confidence_scores": {
    "role": {"score": 60, "reasoning": "Generic term, lacks specificity", ...},
    "years_of_experience": {"score": 40, "reasoning": "Vague quantifier 'some'", ...}
  },
  "original_input": "developer with some backend experience",
  "schema_version": "1.0.0"
}
```

**Validation**:
- ✅ Low confidence scores reflect ambiguity
- ✅ Parsing succeeds but flags vague terms
- ⚠️ May fail validation if "Developer" alone doesn't count as a specific role

---

### Scenario 5: Formal Multi-Paragraph JD

**Input**:
```
About the Role:
We are seeking a Senior Full Stack Engineer to join our team.

Requirements:
- 8-15 years of experience in software development
- Strong knowledge of C#, .NET Core, and Angular
- Experience with microservices architecture
- Located in Tamil Nadu or willing to relocate

Nice to Have:
- Experience with Kubernetes
- Knowledge of Azure cloud services
```

**Expected Output**:
```json
{
  "role": "Senior Full Stack Engineer",
  "required_skills": ["C#", ".NET Core", "Angular", "Microservices"],
  "preferred_skills": ["Kubernetes", "Azure"],
  "years_of_experience": {
    "min": 8,
    "max": 15,
    "range_text": "8-15 years"
  },
  "seniority_level": "Senior",
  "location_preferences": ["Tamil Nadu"],
  "domain": null,
  "confidence_scores": {
    "role": {"score": 95, "reasoning": "Explicitly stated in 'About the Role' section", ...},
    "required_skills": {"score": 95, "reasoning": "Listed under 'Requirements'", ...},
    "preferred_skills": {"score": 90, "reasoning": "Listed under 'Nice to Have'", ...},
    ...
  },
  "original_input": "About the Role:\n...",
  "schema_version": "1.0.0"
}
```

**Validation**:
- ✅ Distinguishes required vs nice-to-have skills
- ✅ Extracts from structured sections ("Requirements", "Nice to Have")
- ✅ Ignores company info ("About the Role") per FR-009

---

### Scenario 6: Iterative Refinement

**Step 1 - Initial Input**:
```
python developer
```

**Output 1**:
```json
{
  "role": "Python Developer",
  "required_skills": ["Python"],
  ...
}
```

**Step 2 - User Edits Input**:
```
senior python developer with fastapi
```

**Output 2**:
```json
{
  "role": "Senior Python Developer",
  "required_skills": ["Python", "FastAPI"],
  "seniority_level": "Senior",
  ...
}
```

**Validation**:
- ✅ Parser re-processes updated input
- ✅ New fields extracted (seniority, additional skill)
- ✅ Previous context not lost (Python still in skills)

---

## Edge Case Validations

### Contradictory Information
**Input**: `junior developer with 10 years experience`
**Expected**: Low confidence score + warning in `reasoning`: "Contradiction detected: junior level but 10+ years experience"

### Typos and Abbreviations
**Input**: `sr dev, JS/TS, 5 yoe`
**Expected**:
- `sr dev` → `Senior Developer`
- `JS/TS` → `["JavaScript", "TypeScript"]`
- `5 yoe` → `years_of_experience: {min: 5, ...}`

### Non-English Input
**Input**: `développeur python senior` (French)
**Expected**: `ValidationError: Currently only English job descriptions are supported`

### Extremely Long Input (20,000+ characters)
**Input**: [Full JD with 20,000 characters]
**Expected**: Parser handles without truncation, completes within <5 seconds

---

## Running Tests Manually

1. **Setup**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

2. **Run Parser**:
   ```bash
   python -m jd_parser.cli "senior python developer with 5+ years in fintech"
   ```

3. **Validate Output**:
   - Check JSON structure matches schema
   - Verify all required fields present
   - Confirm confidence scores are reasonable (>70 for clear inputs)

4. **Test Edge Cases**:
   - Try each scenario above
   - Compare actual output with expected
   - File issues for discrepancies

---

## Success Criteria

- ✅ All 6 primary scenarios pass
- ✅ Edge cases handled gracefully
- ✅ Output validates against JSON schema
- ✅ Performance targets met (<2s typical, <5s large)
- ✅ Confidence scores reflect extraction quality
