# RLS-BUDDY

Welcome to the RLS-BUDDY project! This project focuses on the prototypical development of the backend for an app that helps users track symptoms of Restless Legs Syndrome (RLS). Utilizing FastAPI, this early-stage prototype aims to provide an efficient and scalable solution for symptom tracking and management. Note that this is an early prototype of the backend, and the frontend is currently missing.

## Table of Contents

- [Introduction](#introduction)
- [Architecture](#architecture)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Introduction

RLS-BUDDY is designed to help users track and manage symptoms of Restless Legs Syndrome. This early prototype leverages FastAPI to create a robust backend infrastructure, providing RESTful APIs for various functionalities. Note that this project is in its early stages, and the frontend development is yet to be implemented.

This project is at a very early stage of development and is intended to serve as a proof of concept for the backend infrastructure. The primary goal is to demonstrate the feasibility of using FastAPI and a microservices architecture to build a scalable and efficient solution for symptom tracking and management.

This project is Open-Source. Feel free to contribute to the project by following the guidelines in the [Contributing](#contributing) section.

## Architecture

RLS-BUDDY utilizes a microservices architecture to divide the application into smaller, manageable services. Each service handles a specific part of the application's functionality and communicates with other services via RESTful APIs.

### Key Components

- **User Service**: Manages user registration, authentication, and profiles.
- **Symptom Tracking Service**: Handles the logging and retrieval of symptom data.
- **API Gateway**: Serves as the entry point for all client requests, routing them to the appropriate microservice.

## Features

- **Symptom Tracking**: Users can log their RLS symptoms, including severity, frequency, and triggers.
- **User Management**: Secure user registration, authentication, and profile management.
- **Secure and Scalable**: Built with security and scalability in mind using modern microservices architecture.

## Installation

To get started with RLS-BUDDY, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/rls-buddy.git
   cd rls-buddy
   ```

2. **Set up a virtual environment:**
   ```bash
   python3 -m venv env
   source env/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory and add the necessary environment variables.
   ```plaintext
   DATABASE_URL=your_database_url
   JWT_SECRET=your_jwt_secret
   ```

5. **Run the application on localhost 8000:**
   ```bash
    docker-compose -f docker-compose.test.yml up --build -d
   ```

5. **Run the application for systemtests on localhost 8080:**
   ```bash
    docker-compose -f docker-compose.test.yml -p test up --build -d
   ```



## Usage

Once the application is running, you can interact with the services through the Frontend-Prototype at `http://localhost:8000/frontend`.

## API Documentation User-Service

To access the API documentation, navigate to `http://localhost:8000/user-docs` in your browser. This page provides detailed information about the available endpoints, request parameters, and response formats.


## API Documentation Tracking-Service

To access the API documentation, navigate to `http://localhost:8000/tracking-docs` in your browser. This page provides detailed information about the available endpoints, request parameters, and response formats.

## Contributing

We welcome contributions from the community! To contribute to RLS-BUDDY, follow these steps:

1. **Fork the repository:**
   Click the "Fork" button at the top of this repository to create a copy of it in your GitHub account.

2. **Clone your fork:**
   ```bash
   git clone https://github.com/teleponi/rls-buddy.git
   cd rls-buddy
   ```

3. **Create a branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make your changes and commit them:**
   ```bash
   git commit -m "Add your commit message here"
   ```

5. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request:**
   Go to the original repository on GitHub and click "New Pull Request" to submit your changes for review.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions, feedback, or support, please open an issue on GitHub or contact us at support@rls-buddy.com.


## Integration Tests

### Overview

Integration testing is a crucial part of the development process for ensuring that different components of a microservices architecture work together seamlessly. In this project, we have implemented integration tests that verify the correct functioning of the API Gateway, User Service, and Tracking Service. These tests simulate real-world interactions between the services, such as user authentication, tracking data creation, and service-to-service communication, all within a controlled environment.

### Testing Environment

To isolate the testing environment from the development and production environments, we have created a dedicated Docker Compose setup (`docker-compose.test.yml`). This setup includes separate instances of the services and databases used exclusively for testing purposes. This ensures that test data does not interfere with the main databases and that tests can be run in a clean environment.

### Systemtests

1. **Start the Test Environment:**

   Before running the tests, ensure that the test environment is up and running. This can be done using the following command:

   ```bash
   docker-compose -f docker-compose.test.yml -p test up --build -d
   ```

   This command will start all the necessary services, including the API Gateway, User Service, Tracking Service, RabbitMQ, and the test databases.

2. **Run the Tests:**

   Once the test environment is ready, you can run the integration tests using `pytest`. The tests are located in the `tests/` directory and are structured to cover various aspects of the microservices' interactions.

   To run the tests, execute:

   ```bash
   pytest tests/
   ```

   This command will run all the test files that follow the `test_*.py` naming convention. The tests will make HTTP requests to the API Gateway, which will forward the requests to the appropriate microservices. The tests will then validate the responses to ensure the services are functioning correctly.


3. **Shutdown docker test:**
   ```bash
   docker-compose -f docker-compose.test.yml -p test down -v
   ```


### User-Service Test && Coverage

The integration tests cover several critical aspects of the system, including:

- **Health Checks:** Verifying that all services are up and running.
- **User Authentication:** Testing the creation of users, token generation, and token validation.

   ```bash
   cd user_service
   pytest tests -vv --cov=./ --cov-config=.converage.rc --no-header
   ```

   to generate a html report, run:

   ```bash
    pytest tests/ -vv --cov=./  --cov-report=html --no-header
    ```


### Tracking-Service Test && Coverage

The integration tests cover several critical aspects of the system, including:

- **Health Checks:** Verifying that all services are up and running.
- **Tracking Data Management:** Ensuring that sleep and day tracking data can be created, retrieved, and managed correctly through the API Gateway.

to generate a coverage report, run:

   ```bash
   cd tracking_service
   pytest tests -vv --cov=./  --no-header
```

to generate a html report, run:
   ```bash
    pytest tests/ -vv --cov=./  --cov-report=html --no-header
```

### Migrations

Migrations are done with Alembic. To init alembic in a new service, run:

change in docker file:

```bash
RUN chown -R nonrootuser:nonrootuser /app
RUN chmod +x /app/wait-for-it.sh
```

mount directory in docker-compose file:

```bash
volumes:
  - ./tracking_service:/app
```

```bash
docker-compose exec user-service alembic init alembic
```

change the `alembic.ini` file to point to the database url.

```bash
script_location = alembic
sqlalchemy.url = postgresql://user:password@user_db/users
```

change the `env.py` file to import the Base model

```python
from models import Base
target_metadata = Base.metadata
```

To create first migration, run:

```bash
docker-compose exec user-service alembic revision "Initial migration"
```

if you already defined models, use autogenerate to create migration files:

```bash
docker-compose exec user-service alembic revision --autogenerate -m "Add user table"
```

Change revision file accordingly.

To apply migration, run:
```bash
docker-compose exec user-service alembic upgrade head
```

to login to the database and view the tables, run:
```bash
docker exec -it rls_buddy-user_db-1 psql -U user -d users
```

to view the history of migrations, run:
```bash
docker-compose exec user-service alembic history
```

to view the current version of the database, run:
```bash
docker-compose exec user-service alembic current
```

to downgrade a migration, run:
```bash
docker-compose exec user-service alembic downgrade -1
```

to upgrade to a specific version, run:
```bash
docker-compose exec user-service alembic upgrade +1
```
