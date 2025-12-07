# Changelog

<!-- START -->
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2025-12-07

[:material-github: Github release](https://github.com/illagrenan/django-brotli/releases/tag/v0.4.0)

### Added

- Add support for Python 3.14.
- Add support for Django 6.0.

### Changed

- Updated CI workflows to use pipx for Poetry installation to fix Python 3.13+ compatibility.

### Credits

- Thanks to [@axsapronov](https://github.com/axsapronov) for contributions to this release.


## [0.3.0] - 2024-12-11

[:material-github: Github release](https://github.com/illagrenan/django-brotli/releases/tag/v0.3.0)

### Added

- Add support for Python 3.10, 3.11, 3.12 and 3.13.
- Add support for Django 4.2 LTS, 5.0 and 5.1.

### Changed

- Use Github Actions for CI.
- Use Ruff formatter and Ruff linter.
- Use pytest for tests.


### Removed

- Drop support for unsupported versions of Python (3.6, 3.7, 3.8) and Django (3)
