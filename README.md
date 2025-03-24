# Django Modular Project 🔥

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![codecov](https://codecov.io/github/animemoeus/special-pancake/graph/badge.svg?token=nYlXdNE9pW)](https://codecov.io/github/animemoeus/special-pancake)

## About

A modular Django project template designed for scalability and maintainability, with production-ready features out of the box.

## Features

- Modern Django configuration with modular app structure
- Docker setup for development, local testing, and production
- DevContainer configuration for VS Code users
- Comprehensive testing framework
- Documentation with ReadTheDocs integration
- Multiple environment support (local, production)
- Pre-commit hooks for code quality

## Quick Start

### Using Docker

```bash
# Local development setup
docker-compose -f docker-compose.local.yml up

# For documentation development
docker-compose -f docker-compose.docs.yml up
```

### Manual Setup

1. Set up a virtual environment:

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements/local.txt
   ```

3. Create a .env file:

   ```bash
   python merge_production_dotenvs_in_dotenv.py
   ```

4. Run migrations:

   ```bash
   python manage.py migrate
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Development

This project uses [just](https://github.com/casey/just) as a command runner. See the `justfile` for available commands.

## Testing

```bash
python manage.py test
```

## Documentation

Documentation is available at [ReadTheDocs](https://django-modular.readthedocs.io/).

To build documentation locally:

```bash
cd docs
make html
```

## Contributing

See [CONTRIBUTORS.txt](CONTRIBUTORS.txt) for the list of contributors.

Contributions are welcome! Please set up pre-commit hooks before contributing:

```bash
pre-commit install
```

## License

This project is licensed under the terms of the LICENSE file included in this repository.

---

## Todo:

- Update form to Django Form Class
- Adding Test to Inventory app
- Add Product UoM
- Add Product Category
