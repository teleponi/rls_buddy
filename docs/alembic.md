### Step 1: Install Alembic

First, install Alembic along with SQLAlchemy if you haven't already:

```bash
pip install alembic sqlalchemy
```

### Step 2: Configure Alembic

1. **Initialize Alembic**: In the root directory of your FastAPI project, run the following command to initialize Alembic:

    ```bash
    alembic init alembic
    ```

    This will create an `alembic` directory with configuration files.

2. **Edit `alembic.ini`**: Update the `alembic.ini` file to point to your database. Modify the `sqlalchemy.url` section to use your database URL:

    ```ini
    sqlalchemy.url = postgresql://user:password@localhost/dbname
    ```

3. **Edit `env.py`**: Modify `alembic/env.py` to include your models. Import your SQLAlchemy models and configure the `target_metadata`:

    ```python
    from myapp.models import Base  # Adjust the import to your project's structure
    from myapp.database import engine  # Adjust the import to your project's structure

    target_metadata = Base.metadata

    def run_migrations_offline():
        ...
        context.configure(
            url=config.get_main_option("sqlalchemy.url"),
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
        )
        ...

    def run_migrations_online():
        ...
        connectable = engine

        with connectable.connect() as connection:
            context.configure(
                connection=connection, target_metadata=target_metadata
            )
        ...
    ```

### Step 3: Create a Migration Script

1. **Generate a Migration Script**: When you make changes to your models, generate a new migration script with:

    ```bash
    alembic revision --autogenerate -m "Create users table"
    ```

    The `--autogenerate` flag tells Alembic to compare the current state of the database with the models and generate the necessary changes.

2. **Review the Script**: Review the generated migration script in the `alembic/versions` directory to ensure it correctly reflects your changes.

### Step 4: Apply Migrations

1. **Apply Migrations**: To apply the migrations to your database, run:

    ```bash
    alembic upgrade head
    ```

    This command will apply all pending migrations to bring the database schema up to date.

### Example Directory Structure

Your project structure should look something like this:

```
rls-buddy/
├── api-gateway/
│   ├── main.py
│   ├── Dockerfile
├── user-service/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── Dockerfile
├── tracking-service/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── Dockerfile
├── alembic/
│   ├── versions/
│   ├── env.py
├── alembic.ini
├── docker-compose.yml
└── .env
```

### Example of Models and Database Configuration

**user-service/models.py**

```python
from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
```

**user-service/database.py**

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    Base.metadata.create_all(bind=engine)
```


By following these steps, you can effectively manage database migrations in your FastAPI project using Alembic, ensuring that your database schema is kept up to date with your models. This setup provides a robust and flexible way to handle schema changes as your application evolves.


When dealing with not-nullable fields in SQLAlchemy models and handling database migrations with Alembic in a FastAPI project, it’s important to ensure that your model definitions, database schema, and data migrations are consistent and robust. Here’s how you can manage not-nullable fields effectively:

### Step 1: Define Not-Nullable Fields in SQLAlchemy Models

In SQLAlchemy, you can define not-nullable fields by setting `nullable=False` on your columns. For example:

**user-service/models.py**

```python
from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
```

### Step 2: Update Database Schema with Alembic

When you add or modify a not-nullable field in your models, you need to create and apply a migration script with Alembic.

1. **Generate a Migration Script**: Run the following command to generate a new migration script:

    ```bash
    alembic revision --autogenerate -m "Add not-nullable constraints to User fields"
    ```

2. **Review and Edit the Migration Script**: Alembic will generate a migration script in the `alembic/versions` directory. Review the script to ensure it correctly reflects the changes.

**Example Migration Script**

```python
"""Add not-nullable constraints to User fields

Revision ID: abcdef123456
Revises: 123456abcdef
Create Date: 2023-08-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = 'abcdef123456'
down_revision = '123456abcdef'
branch_labels = None
depends_on = None

def upgrade():
    op.alter_column('users', 'name', existing_type=sa.String(), nullable=False)
    op.alter_column('users', 'email', existing_type=sa.String(), nullable=False)
    op.alter_column('users', 'hashed_password', existing_type=sa.String(), nullable=False)

def downgrade():
    op.alter_column('users', 'name', existing_type=sa.String(), nullable=True)
    op.alter_column('users', 'email', existing_type=sa.String(), nullable=True)
    op.alter_column('users', 'hashed_password', existing_type=sa.String(), nullable=True)
```

3. **Apply the Migration**: Apply the migration to your database:

    ```bash
    alembic upgrade head
    ```

### Handling Existing Data

If the table already contains data, adding a not-nullable constraint can cause issues if there are existing rows with `NULL` values. Here are a few strategies to handle this:

1. **Set Default Values**: Update existing rows to set a default value before applying the not-nullable constraint.

    ```python
    def upgrade():
        # Set default values for existing rows
        op.execute("UPDATE users SET name = 'default_name' WHERE name IS NULL")
        op.execute("UPDATE users SET email = 'default@example.com' WHERE email IS NULL")
        op.execute("UPDATE users SET hashed_password = 'default_password' WHERE hashed_password IS NULL")

        # Apply the not-nullable constraint
        op.alter_column('users', 'name', existing_type=sa.String(), nullable=False)
        op.alter_column('users', 'email', existing_type=sa.String(), nullable=False)
        op.alter_column('users', 'hashed_password', existing_type=sa.String(), nullable=False)
    ```

2. **Add Temporary Nullable Columns**: Add temporary nullable columns, migrate the data, then drop the old columns and rename the new ones.

    ```python
    def upgrade():
        # Add temporary columns
        op.add_column('users', sa.Column('new_name', sa.String(), nullable=False, server_default='default_name'))
        op.add_column('users', sa.Column('new_email', sa.String(), nullable=False, server_default='default@example.com'))
        op.add_column('users', sa.Column('new_hashed_password', sa.String(), nullable=False, server_default='default_password'))

        # Migrate data to new columns
        op.execute("UPDATE users SET new_name = name")
        op.execute("UPDATE users SET new_email = email")
        op.execute("UPDATE users SET new_hashed_password = hashed_password")

        # Drop old columns
        op.drop_column('users', 'name')
        op.drop_column('users', 'email')
        op.drop_column('users', 'hashed_password')

        # Rename new columns to old names
        op.alter_column('users', 'new_name', new_column_name='name')
        op.alter_column('users', 'new_email', new_column_name='email')
        op.alter_column('users', 'new_hashed_password', new_column_name='hashed_password')
    ```

### Step 3: Update Pydantic Models

Ensure that your Pydantic models reflect the not-nullable fields.

**user-service/main.py**

```python
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
```

### Conclusion

By following these steps, you can effectively manage not-nullable fields in your FastAPI project using SQLAlchemy, Pydantic, and Alembic. This ensures your database schema stays consistent with your application logic while maintaining data integrity.

### References

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/en/latest/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
