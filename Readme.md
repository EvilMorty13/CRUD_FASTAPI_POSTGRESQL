# Alembic Migration Setup

- Initialize Alembic
   ```
   alembic init -t async alembic
   ```

- Add changes in the model

- Modify **env.py** file
  ```
  from database import Base # Import Base
  target_metadata = Base.metadata  # Replace with your metadata
  ```

- Update **alembic.ini** file
  ```
  sqlalchemy.url = postgresql+asyncpg://username:password@localhost/dbname
  ```

- Create Migration file
  ```
  alembic revision --autogenerate -m "file_name"
  ```

- Go to the **versions/<migration_id>_file_name.py** file and update the upgrade & downgrade functions

- Apply the migration
  ```
  alembic upgrade head
  ```

- See migration history
  ```
  alembic history
  ```

- Downgrade to the Previous Revision 
  ```
  alembic downgrade -1
  ```

- Downgrade to the Specific Revision 
  ```
  alembic downgrade <revision_id>
  ```

