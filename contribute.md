# Contributing to RLS Buddy

Thank you for considering contributing to RLS Buddy! This project aims to provide a user-friendly, open-source solution for tracking Restless Legs Syndrome (RLS) symptoms, with a backend based on microservices and a RESTful API. We are excited to have you join us and help improve the project.

## How to Contribute

### 1. Getting Started

1. **Fork the repository**: Start by forking the RLS Buddy repository to your GitHub account.

2. **Clone the forked repository**: Clone the repository to your local machine.

   ```bash
   git clone https://github.com/your-username/rls-buddy.git
   ```

3. **Install dependencies**: The project uses Docker for managing services, so you will need Docker and Docker Compose installed on your machine. If you don't have them, follow the [official Docker installation guide](https://docs.docker.com/get-docker/).

4. **Set up the development environment**: To set up the project, use Docker Compose to build and start all services.

   ```bash
   docker-compose up --build
   ```

5. **Create a branch**: When you're ready to start working on an issue or feature, create a new branch with a descriptive name.

   ```bash
   git checkout -b feature/new-feature-name
   ```

### 2. Code Guidelines

- **Code Style**: Follow Python's [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines for clean and readable code.
- **Docstrings**: Write clear docstrings for all functions and classes, especially for complex logic. Refer to the [Google Python Style Guide](http://google.github.io/styleguide/pyguide.html) for consistent docstring formatting.
- **Testing**: Ensure that all new features and bug fixes include appropriate test coverage. We use `pytest` for unit and integration tests.

  Run the tests locally before submitting your pull request:

  ```bash
  pytest
  ```

- **Commits**: Write clear and meaningful commit messages. Follow this format:

  - `fix`: For bug fixes
  - `feat`: For new features
  - `docs`: For changes related to documentation
  - `style`: For formatting, missing semi-colons, etc.
  - `refactor`: For refactoring code (no functional changes)
  - `test`: For adding or fixing tests

### 3. Submitting a Pull Request

1. **Push your branch to GitHub**:

   ```bash
   git push origin feature/new-feature-name
   ```

2. **Create a Pull Request**: Go to the original repository and submit a pull request. Make sure to provide a clear description of what the pull request does and reference any related issues.

3. **Code Review**: One of the maintainers will review your pull request. Please be patient, as the process may take a few days. If any changes are requested, make sure to address them promptly.

4. **Merge**: Once your pull request is approved, it will be merged into the main branch!

### 4. Contributing Guidelines

- **Reporting Bugs**: If you find a bug, please open an issue on GitHub with a clear description of the problem. Include steps to reproduce the issue, any relevant error messages, and screenshots if applicable.

- **Proposing Features**: If you have a feature idea, feel free to open a feature request issue to discuss it with the community. We encourage thoughtful discussions and collaboration before implementation.

- **Open Discussions**: We value open communication. Use the Discussions feature to propose ideas, ask questions, or start discussions about the future direction of the project.

### 5. Code of Conduct

By contributing, you agree to abide by the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/). We aim to create a welcoming and inclusive community for everyone, and we ask that you follow these guidelines to maintain a positive and constructive atmosphere.

### 6. Licensing

By contributing to RLS Buddy, you agree that your contributions will be licensed under the MIT License. Make sure to read the [LICENSE](LICENSE) file for more information.

---
