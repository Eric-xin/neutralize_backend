# Neutralize

<div align="center">
    <img src="./assets/img/neutralize.png" alt="Neutralize Icon" width="100" height="100">
    <h1>Neutralize</h1>
</div>

Neutralize is a web application designed to analyze and neutralize political bias in text using machine learning models. It leverages the BERT model for bias detection and OpenAI's GPT for generating explanations of the detected bias.

## Table of Contents

- [Neutralize](#neutralize)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Installation](#installation)
  - [Usage](#usage)
  - [API Endpoints](#api-endpoints)
    - [Authentication](#authentication)
    - [User Management](#user-management)
    - [Bias Analysis](#bias-analysis)
  - [Technologies](#technologies)
  - [Project Structure](#project-structure)
  - [License](#license)

## Features

- **User Authentication**: Register, login, and manage user accounts.
- **Bias Detection**: Analyze text for political bias using NLP model.
- **Bias Explanation**: Generate explanations for detected bias using OpenAI's GPT.
- **Database Integration**: Store and manage user data using SQLite.
- **API Endpoints**: Expose functionalities through RESTful API endpoints.

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/neutralize.git
    cd neutralize
    ```

2. **Create and activate a virtual environment**:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
    - Copy `.env.example` to `.env` and fill in the required values.

5. **Initialize the database**:
    ```sh
    python database/db_gen.py
    ```

## Usage

1. **Run the server**:
    ```sh
    uvicorn server:app --reload --host 0.0.0.0 --port 9999
    ```

2. **Access the API documentation**:
    - Open your browser and navigate to `http://localhost:9999/api/docs`.

## API Endpoints

### Authentication

- **Register a new user**:
    - `POST /api/register`
    - Request body: [User](http://_vscodecontentref_/2) schema

- **Login**:
    - `POST /api/login`
    - Request body: [OAuth2PasswordRequestForm](http://_vscodecontentref_/3)

### User Management

- **Retrieve all users**:
    - `GET /api/users`
    - Response: List of [UserResponse](http://_vscodecontentref_/4) schema

- **Retrieve a single user**:
    - `GET /api/user/{id}`
    - Response: [UserResponse](http://_vscodecontentref_/5) schema

- **Update user data**:
    - `PATCH /api/user/{id}`
    - Request body: [User](http://_vscodecontentref_/6) schema

- **Delete a user**:
    - `DELETE /api/user/{id}`
    - Response: List of [UserResponse](http://_vscodecontentref_/7) schema

### Bias Analysis

- **Analyze text for bias**:
    - `POST /api/analyze/`
    - Request body: [TextRequest](http://_vscodecontentref_/8) schema
    - Response: Bias analysis result

- **Analyze text for bias and get explanation**:
    - `POST /api/analyze_mult/`
    - Request body: [TextRequest](http://_vscodecontentref_/9) schema
    - Response: Bias analysis result and explanation

- **Caching intergration for websites visited**:
    - `POST /api/cache`
    - Request body: [CacheRequest](http://_vscodecontentref_/10) schema
    - Response: URL, Title and Text are added into table Cache

## Technologies
- **FastAPI**: Web framework for building APIs with Python.
- **Pydantic**: Data validation and parsing using Python type hints.
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM) for Python.
- **SQLite**: Serverless, self-contained SQL database engine.
- **BERT**: Pre-trained NLP model developed by Google.

## Project Structure
```plaintext
.
├── CRUD
│   └── authen.py
├── LICENSE
├── database
│   ├── SQLite.db
│   ├── SQLite.db-journal
│   └── db_gen.py
├── database.py
├── models.py
├── neutralize
│   ├── GPT
│   │   ├── __init__.py
│   │   └── work.py
│   ├── NLP
│   │   ├── nlp_app.py
│   │   └── nlp_model.py
│   └── neutralize.py
├── readme.md
├── requirements.txt
├── schemas.py
├── server.py
├── service
│   ├── hashing.py
│   ├── jwttoken.py
│   └── oauth.py
```

## License
[LICENSE](./LICENSE)