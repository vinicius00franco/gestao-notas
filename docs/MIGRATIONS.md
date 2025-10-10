# SQL-First Migration Strategy

This document outlines the official strategy for creating and managing database migrations in this project. To ensure consistency, safety, and predictability, all schema changes must adhere to a SQL-first approach.

## Core Principles

1.  **All Migrations Must Be Raw SQL:** All schema changes (e.g., `CREATE TABLE`, `ALTER TABLE`, `ADD COLUMN`) must be written in raw SQL. Django's automatic migration generation (`makemigrations`) should not be used for schema changes.
2.  **Idempotency is Mandatory:** Every SQL script must be idempotent, meaning it can be run multiple times without causing errors or unintended side effects. Use defensive statements like `CREATE TABLE IF NOT EXISTS`, `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`, and check for the existence of constraints before adding them.
3.  **Separation of Concerns:** Each migration consists of two parts:
    *   A `.sql` file containing the raw, idempotent SQL code.
    *   A Python migration file (`.py`) that uses `django.db.migrations.RunSQL` to execute the corresponding `.sql` file.

## The Migration Workflow

1.  **Create the SQL File:**
    -   Create a new `.sql` file in the relevant app's `migrations` directory (e.g., `apps/app_name/migrations/000X_description.sql`).
    -   Write the idempotent SQL for your schema change. For example:
        ```sql
        -- Add a new column 'new_field' to the 'my_table' table
        ALTER TABLE my_table ADD COLUMN IF NOT EXISTS new_field VARCHAR(100);

        -- Initialize the new column to avoid issues with NOT NULL constraints if applied later
        UPDATE my_table SET new_field = '' WHERE new_field IS NULL;
        ```

2.  **Create the Python Migration File:**
    -   Run `python manage.py makemigrations app_name --empty -n description` to generate an empty migration file.
    -   In the generated Python file, add a `migrations.RunSQL` operation to read and execute your `.sql` file. Use the pattern below to locate and run the SQL script:

        ```python
        import os
        from django.db import migrations

        # Function to read the SQL file
        def read_sql_file(file_name):
            file_path = os.path.join(os.path.dirname(__file__), file_name)
            with open(file_path, 'r') as f:
                return f.read()

        class Migration(migrations.Migration):

            dependencies = [
                ('app_name', '000X-1_previous_migration'),
            ]

            operations = [
                migrations.RunSQL(
                    sql=read_sql_file('000X_description.sql'),
                    reverse_sql="-- Add reverse SQL here if applicable, e.g., DROP TABLE, ALTER TABLE ... DROP COLUMN",
                ),
            ]
        ```

3.  **Verification:**
    -   After creating a migration, always run `python manage.py makemigrations --check` to ensure your changes are synchronized with the Django models and that no further automatic migrations are needed.
    -   This confirms that your manual SQL migration correctly reflects the state of your models.

By following this standardized process, we ensure that our database schema evolves in a controlled, robust, and maintainable way.