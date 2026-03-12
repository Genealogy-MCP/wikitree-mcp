# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial release with 10 WikiTree API tools
- `get_profile` — retrieve person or free-space profile
- `get_person` — retrieve person profile
- `get_people` — fetch multiple profiles by keys
- `search_person` — search profiles by criteria
- `get_ancestors` — get ancestral tree
- `get_descendants` — get descendant tree
- `get_relatives` — get parents, children, siblings, spouses
- `get_bio` — retrieve biography text
- `get_photos` — get photos linked to a profile
- `get_categories` — retrieve associated categories
- HTTP client with retry, timeout, and exponential backoff
- Docker support (multi-stage build)
- GitHub Actions CI pipeline
