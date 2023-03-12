# translate-md

Python client to [spanglish](https://github.com/plaguss/spanglish), *and a bit more*. Translate your markdown files from english 🇬🇧 to spanish 🇪🇸.

<div align="center">

| | |
| --- | --- |
| CI/CD | [![CI - Test](https://github.com/plaguss/translate-md/actions/workflows/test.yml/badge.svg)](https://github.com/plaguss/translate-md/actions/workflows/test.yml)  |
| Docs | [![Docs - Release](https://github.com/plaguss/translate-md/actions/workflows/docs-release.yml/badge.svg)](https://github.com/plaguss/translate-md/actions/workflows/docs-release.yml) |
| Package | [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/translate-md.svg?logo=python&label=Python&logoColor=gold)](https://pypi.org/project/translate-md/) |
| Meta | [![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch) [![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v0.json)](https://github.com/charliermarsh/ruff) [![code style - Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/python/mypy) [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) |

</div>

---

> This project was developed for my personal use: translating markdown files from my blog posts. It may be useful for somebody (I would be honored to listen to that), but please don't expect everything correct to the detail.

Anyway, the API is not expected to change much unless some extra feature is required. Contributions are welcome!

To see the features along some examples, please visit the docs.

## 🔧 Installation

```console
pip install translate-md
```

This client depends on a service which is currently expected tu run locally. You would need to get it to work:

### Additional dependencies

You will need [spanglish](https://github.com/plaguss/spanglish) running in order to start working. The easiest way is to clone the repo and use docker for it. Get the service up you should be ready to go.

### CLI version

It may be convenient for some cases, so the library comes with a CLI with a subset of the functionality:

```console
pip install translate-md[cli]
```

Or maybe better with pipx

```console
pipx install translate-md[cli]
```

Visit the docs for further information.


## 📝 Documentation

The [documentation](https://plaguss.github.io/translate-md/) is made with [Material for MkDocs](https://github.com/squidfunk/mkdocs-material) and is hosted by [GitHub Pages](https://docs.github.com/en/pages).

