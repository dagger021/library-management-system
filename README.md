# Library Management System
This project demostrates the backend design and implementation of a library management system, which involves managing books, members, and books borrowed.

## RESTful API Endpoints
1. Auth

  - **POST** `/login`

  - **POST** `/register`


2. Books

  - **GET** `/books`
    - Description: Get books from categories, authors, and publishers, with categories, authors, and publishers.

  - **POST** `/books`
    - Description: Create book from categories, authors, and publishers.

  - **GET** `/books/{isbn}`
    - Description: Get a book by *isbn*.


3. Authors

  - **GET** `/authors`
    - Description: Get all authors.

  - **POST** `/authors`
    - Description: Create an author record.

  - **DELETE** `/authors`
    - Description: Delete authors with the provided *author_ids*.

  - **DELETE** `/authors/{author_id}`
    - Description: Delete authors with the provided *author_id*.


4. Categories (Book Categories)

  - **GET** `/categories`
    - Description: Get all categories.

  - **POST** `/categories`
    - Description: Create an category record.

  - **DELETE** `/categories`
    - Description: Delete categories with the provided *category_ids*.

  - **DELETE** `/categories/{category_id}`
    - Description: Delete categories with the provided *category_id*.


5. Publisher

  - **GET** `/publishers`
    - Description: Get all publishers.

  - **POST** `/publishers`
    - Description: Create an publisher record.

  - **DELETE** `/publishers`
    - Description: Delete publishers with the provided *publisher_ids*.

  - **DELETE** `/publishers/{publisher_id}`
    - Description: Delete publishers with the provided *publisher_id*.


## Database Migrations
`Alembic` tool is used for database migrations.

Follow steps to migrate database to a newer state:

1. import new database schemas, if created to `alembic/env.py` files, otherwise go to step 2.

2. Ask alembic revise changes:
  ```sh
  alembic revision --autogenerate -m "<message>"
  ```

3. Make the migration:
  ```sh
  alembic upgrade head
  ```

## Testing
The project follows *test-driven development*, covering test cases for different parts of code. All testing code resides in `/tests` folder.

This project uses `pytest` for extensive testing.

1. To run tests:
  ```sh
  pytest tests
  ```