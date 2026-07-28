# Source Registry Validation Report

## Overview
- **Registry Version:** v1.1
- **Status:** COMPLETE
- **Frozen:** TRUE
- **Generated At:** 2026-07-28T09:18:06Z

## Statistics
- **Total Entries:** 117
- **Total URLs Validated:** 291
- **Total Categories:** 11

## Category Breakdown
- **chunking**: 11 entries
- **deployment**: 35 entries
- **embedding**: 5 entries
- **evaluation**: 8 entries
- **fine_tuning**: 8 entries
- **framework**: 4 entries
- **llm**: 7 entries
- **prompting**: 12 entries
- **rerankers**: 9 entries
- **retrieval**: 12 entries
- **vectordb**: 6 entries

## Validation Checks Performed
- [x] JSON syntax validation
- [x] Required fields & ordering check
- [x] Unique ID validation
- [x] Category & naming consistency
- [x] HTTPS-only links enforcement
- [x] Empty string vs empty array constraints
- [x] ISO-8601 timestamp formatting
- [x] License & organization consistency

## Known Limitations & Intentional States
- **Intentionally Empty Metadata:** Entries lacking an official framework maintainer (e.g., theoretical prompting techniques like Zero-Shot) utilize Independent Research and leave framework-specific fields (e.g., github_repository, license) strictly empty as empty arrays ([]) or strings ("").
- **WAF Protections:** Specific active documentation sites (e.g., Arize AI, vLLM, K3s, KServe) successfully exist but actively block scraping via 403 Forbidden or 429 Too Many Requests errors. They are structurally correct and have been securely retained rather than downgraded to READMEs.

## Final Validation Status
All checks passed successfully. The registry is perfectly consistent and locked.
