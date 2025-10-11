# TDD Status - Contract Tests (Phase 3.2)

**Date**: 2025-10-09
**Status**: ✅ Tests Written, ❌ Expecting Failures (as designed)

## Overview

Following strict TDD methodology, we have written contract tests **BEFORE** implementing the enhanced models. These tests define the expected behavior and will guide our implementation.

## Test Files Created

### 1. test_input_schema.py (JobRequirement Contract Tests)
- **Location**: `tests/github_sourcer/contract/test_input_schema.py`
- **Purpose**: Validates that JobRequirement model accepts all enhanced configuration fields
- **Test Count**: 13 tests
- **Expected Status**: Most tests WILL FAIL until we update `src/jd_parser/models.py`

**Tests:**
- ✅ `test_minimal_valid_job_requirement` - PASSES (backward compatibility)
- ❌ `test_enhanced_sourcing_source_config` - FAILS (field doesn't exist)
- ❌ `test_skill_confidence_min_threshold` - FAILS (field doesn't exist)
- ❌ `test_skill_confidence_min_invalid_range` - FAILS (validation doesn't exist)
- ❌ `test_location_hierarchy_enabled_flag` - FAILS (field doesn't exist)
- ❌ `test_location_fuzzy_match_enabled_flag` - FAILS (field doesn't exist)
- ❌ `test_bigquery_discovery_config` - FAILS (field doesn't exist)
- ❌ `test_graphql_batching_config` - FAILS (field doesn't exist)
- ❌ `test_dependency_graph_detection_config` - FAILS (field doesn't exist)
- ❌ `test_max_candidates_config` - FAILS (field doesn't exist)
- ❌ `test_complete_enhanced_job_requirement` - FAILS (multiple fields don't exist)
- ❌ `test_default_values_for_optional_fields` - FAILS (fields don't exist)
- ❌ `test_skill_normalization_hint` - FAILS (normalization not implemented)

### 2. test_output_schema.py (Candidate Output Contract Tests)
- **Location**: `tests/github_sourcer/contract/test_output_schema.py`
- **Purpose**: Validates that Candidate model returns enhanced metadata fields
- **Test Count**: 13 tests
- **Expected Status**: Most tests WILL FAIL until we update `src/github_sourcer/models/candidate.py`

**Tests:**
- ✅ `test_minimal_valid_candidate` - PASSES (backward compatibility with existing model)
- ❌ `test_skill_confidence_scores_field` - FAILS (field doesn't exist)
- ❌ `test_skill_confidence_scores_range_validation` - FAILS (validation doesn't exist)
- ❌ `test_location_parsed_hierarchy_field` - FAILS (field doesn't exist)
- ❌ `test_sourcing_metadata_field` - FAILS (field doesn't exist)
- ❌ `test_detection_method_field` - FAILS (field doesn't exist)
- ❌ `test_fallback_detection_method` - FAILS (ensemble fallback not implemented)
- ❌ `test_location_fuzzy_match_metadata` - FAILS (fuzzy matching not implemented)
- ❌ `test_hierarchical_state_match_metadata` - FAILS (hierarchical matching not implemented)
- ❌ `test_complete_enhanced_candidate` - FAILS (multiple fields don't exist)
- ❌ `test_optional_fields_can_be_none` - Expected behavior needs verification

### 3. test_candidate_validation.py (Business Rule Validation Tests)
- **Location**: `tests/github_sourcer/contract/test_candidate_validation.py`
- **Purpose**: Validates business rules and constraints for Candidate model
- **Test Count**: 15 tests
- **Expected Status**: ALL tests WILL FAIL until we implement validation logic

**Tests (all expected to fail):**
- ❌ `test_skill_confidence_keys_must_match_skills_list` (BR-001)
- ❌ `test_skill_confidence_with_extra_skill_fails` (BR-001)
- ❌ `test_match_score_must_not_exceed_max_confidence` (BR-002)
- ❌ `test_location_parsed_confidence_matches_method` (BR-003)
- ❌ `test_location_fuzzy_match_has_lower_confidence` (BR-003)
- ❌ `test_state_match_has_medium_confidence` (BR-003)
- ❌ `test_country_match_has_low_confidence` (BR-003)
- ❌ `test_all_confidence_scores_in_valid_range` (BR-004)
- ❌ `test_skill_confidence_negative_fails` (BR-004)
- ❌ `test_matched_skills_must_be_subset_of_skills` (BR-005)
- ❌ `test_detection_method_must_be_valid_enum` (BR-006)
- ❌ `test_invalid_detection_method_fails` (BR-006)
- ❌ `test_github_url_must_be_valid_format` (BR-007)
- ❌ `test_valid_github_url_formats` (BR-007)
- ❌ `test_email_validation_if_provided` (BR-008)
- ❌ `test_public_repos_and_followers_must_be_non_negative` (BR-009)

## Current Model Status

### JobRequirement (src/jd_parser/models.py)
**Current Fields:**
- role, required_skills, preferred_skills, years_of_experience
- seniority_level, location_preferences, domain
- confidence_scores, original_input, schema_version

**Missing Enhanced Fields (FR-025 to FR-032):**
- sourcing_source_config
- skill_confidence_min
- location_hierarchy_enabled, location_fuzzy_match_enabled, location_fuzzy_threshold
- bigquery_discovery_enabled, bigquery_time_range_days
- graphql_batching_enabled, graphql_batch_size
- dependency_graph_enabled, dependency_graph_fallback_to_ensemble
- max_candidates

### Candidate (src/github_sourcer/models/candidate.py)
**Current Fields:**
- github_username, name, bio, location, public_email
- top_repos, languages, contribution_count, account_age_days, followers
- profile_url, avatar_url, fetched_at

**Missing Enhanced Fields (FR-003 to FR-009):**
- skill_confidence_scores (dict[str, float])
- location_parsed (dict with city, state, country, confidence, matched_via)
- detection_method (enum: dependency_graph, ensemble_fallback, manual)
- sourcing_metadata (dict with discovery details, pipeline timing)
- match_score (float 0.0-1.0)
- matched_skills (list[str])

## Next Steps (TDD Red-Green-Refactor)

### RED Phase (Current) ✅ COMPLETE
We've written failing tests that define expected behavior.

### GREEN Phase (Next - T012-T014B)
Implement minimal code to make tests pass:

1. **T012**: Update JobRequirement model with enhanced fields
   - Add all sourcing configuration fields
   - Add default values per spec.md
   - Add validation for ranges (0.0-1.0 for confidence scores)

2. **T013**: Update Candidate model with output fields
   - Add skill_confidence_scores, location_parsed, detection_method
   - Add sourcing_metadata, match_score, matched_skills
   - Align field names (github_url vs profile_url)

3. **T014**: Implement Candidate validation logic
   - Validators for BR-001 through BR-009
   - Confidence score range checks
   - Match score consistency checks
   - URL format validation

### REFACTOR Phase (T015+)
After tests pass, refactor for:
- Consistent field naming across models
- Better error messages
- Code organization
- Documentation

## Running Tests

```bash
# Run all contract tests (expect failures)
python3.11 -m pytest tests/github_sourcer/contract/ -v

# Run specific test file
python3.11 -m pytest tests/github_sourcer/contract/test_input_schema.py -v

# Run specific test
python3.11 -m pytest tests/github_sourcer/contract/test_input_schema.py::TestJobRequirementInputSchema::test_minimal_valid_job_requirement -v
```

## Test Dependencies

All tests depend on:
- pydantic>=2.0.0
- pytest>=8.0.0
- Existing models in `src/jd_parser/models.py` and `src/github_sourcer/models/candidate.py`

## Notes

- Backward compatibility maintained: Minimal tests pass with existing model
- Enhanced tests intentionally fail until we implement new fields
- This is the **correct TDD approach**: write tests first, then implement
- All test failures are **expected and documented**
