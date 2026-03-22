# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python CLI tool (`kb`) for managing and organizing knowledge bases. Knowledge bases are reusable units that encapsulate domain-specific background knowledge with metadata, source code, and dependency relationships. The system supports version management, dependency management, and packaging for distribution.

## Common Commands

### Development and Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# Run tests with coverage report
pytest tests/ -v --cov=kb --cov-report=html

# Run specific test file
pytest tests/cli/test_init.py -v

# Run specific test function
pytest tests/cli/test_init.py::test_init_creates_directory -v

# Run tests in a specific module
pytest tests/core/ -v
```

### CLI Commands

The `kb` CLI is the main entry point. Key commands:

```bash
# Initialize a knowledge base project and download dependencies
kb init

# Package knowledge base for distribution
kb package

# Check for dependency updates
kb check-updates

# Update dependencies
kb update [dependency_name]

# Cache management
kb cache info
kb cache list
kb cache clean [target]

# Show help
kb --help
kb <command> --help
```

## Architecture

### High-Level Structure

The project follows a modular architecture with clear separation of concerns:

- **CLI Layer** (`kb/cli/`): Click-based command-line interface with subcommands for different operations (init, package, cache, update). All commands are registered in `cli/main.py`.

- **Core Layer** (`kb/core/`): Core functionality including:
  - `models.py`: Pydantic models for data validation (KnowledgeMetadata, Dependency, ExcludedDependency)
  - `parser.py`: Parses Knowledge.md markdown files into structured metadata
  - `validator.py`: Validates knowledge base structure and metadata

- **Dependency Management** (`kb/dependency/`): Handles dependency resolution and downloading:
  - `downloader.py`: Downloads knowledge base packages from Git repositories
  - `extractor.py`: Extracts tar.gz packages to deps/ directory
  - `resolver.py`: Resolves dependency versions and handles conflicts
  - `conflict.py`: Manages dependency conflict detection and resolution

- **Update System** (`kb/update/`): Checks for and applies version updates:
  - `checker.py`: Queries GitHub/GitLab APIs for latest versions
  - `updater.py`: Downloads and applies updates
  - `models.py`: Models for version updates

- **Cache Layer** (`kb/cache/`): Manages local cache at `~/.kb-cache/`:
  - `manager.py`: Cache operations (info, list, clean)

- **Exceptions** (`kb/exceptions.py`): Custom exception types (KnowledgeParseError, VersionFormatError, DependencyConflictError, etc.)

### Key Design Patterns

1. **Semantic Versioning**: The system uses semantic version (MAJOR.MINOR.PATCH) and supports version ranges (`^1.0.0` for compatible versions, `~2.1.0` for patch versions).

2. **Markdown-based Metadata**: Knowledge.md files contain structured metadata in markdown format with tables for dependencies and excluded dependencies. The parser extracts this into Pydantic models for type-safe operations.

3. **Dependency Resolution**: Dependencies are declared in Knowledge.md tables and resolved through a transitive resolution process. The system detects version conflicts and supports explicit exclusion via the "排除依赖" table.

4. **Caching Strategy**: Downloaded packages are cached in `~/.kb-cache/` to avoid repeated downloads. The cache is keyed by library name and version.

5. **Pydantic for Validation**: All data models use Pydantic for runtime type checking and validation (e.g., semantic version format validation in Dependency model).

### Knowledge Base Structure

A knowledge base project follows this structure:

```
knowledge-base/
├── src/                    # Source code (required)
│   └── Knowledge.md         # Metadata file (required)
├── deps/                   # Dependencies (created by kb init)
├── tests/                  # Tests (recommended)
├── publish/                # Package output (created by kb package)
└── README.md               # Documentation (recommended)
```

### Knowledge.md Format

The metadata file is markdown with specific sections:

- Basic info: Name, Version, Type, Description
- Dependencies table: | 知识库名称 | 版本号 | Git地址 |
- Excluded dependencies table: | 知识库名称 | 版本号 | 原因 |

### Version Update Workflow

1. `kb check-updates` queries remote repositories for latest versions
2. Compares with current versions in deps/
3. `kb update` downloads new versions and updates deps/
4. System handles version conflicts and transitive dependencies

### Testing Strategy

Tests are organized by module (`tests/cli/`, `tests/core/`, `tests/cache/`, `tests/update/`). All command-line tests interact with Click's CliRunner. Run tests before committing changes to any CLI command or core functionality.
