# Library Management System
This project demostrates the backend design and implementation of a library management system, which involves managing books, members, and books borrowed.

## RESTful API Endpoints
1. Auth
  - **POST** `/login`
  - **POST** `/register`

2. Books
  - **GET** `/books`
    - Description: Get books from categories, authors, and publishers.


## Database Migrations
`Alembic` tool is used for database migrations.

Follow steps to migrate database to a newer state:
1. import new database schemas, if created to `alembic/env.py` files, otherwise go to step 2.

2. Ask alembic revise changes:
  ```powershell
  alembic revision --autogenerate -m "<message>"
  ```

3. Make the migration:
  ```powershell
  alembic upgrade head
  ```