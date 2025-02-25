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
    - [Neutralise](#neutralise)
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
    - Open your browser and navigate to `http://localhost:8000/api/docs`.

3. **Run in development**
    - Run the server with the following command:
    ```sh
    fastapi dev server.py
    ```

## API Endpoints

### Authentication

- **Register a new user**:
    - `POST /api/register`
    - Request body: User schema

- **Login**:
    - `POST /api/login`
    - Request body: OAuth2PasswordRequestForm

### User Management

- **Retrieve all users**:
    - `GET /api/users`
    - Response: List of UserResponse schema

- **Retrieve a single user**:
    - `GET /api/user/{id}`
    - Response: UserResponse schema

- **Update user data**:
    - `PATCH /api/user/{id}`
    - Request body: User schema

- **Delete a user**:
    - `DELETE /api/user/{id}`
    - Response: List of UserResponse schema

### Neutralise

- **Analyze text for bias**:
    - `POST /api/analyze/`
    - Request body: TextRequest schema
    - Response: Bias analysis result

- **Analyze text for bias and get explanation**:
    - `POST /api/analyze_mult/`
    - Request body: TextRequest schema
    - Response: Bias analysis result and explanation

- **Reduce bias in text**:
    - `POST /api/reduce_bias_txt`
    - Request body: TextRequest schema
    - Response: Original text, bias analysis result, and neutralized text

- **Reduce bias in text and image**:
    - `POST /api/reduce_bias`
    - Request body: Form data with text and optional image file
    - Response: Original text, bias analysis result, neutralized text, and additional context

- **Analyze text and image for bias with multicontext**:
    - `POST /api/multicon_bias_ana`
    - Request body: Form data with text and optional image file
    - Response: Original text, bias analysis result, and explanation

- **Caching integration for websites visited**:
    - `POST /api/cache`
    - Request body: CacheRequest schema
    - Response: URL, Title, and Text are added into table Cache

## Technologies
- **FastAPI**: Web framework for building APIs with Python.
- **Pydantic**: Data validation and parsing using Python type hints.
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM) for Python.
- **SQLite**: Serverless, self-contained SQL database engine.
- **BERT**: Pre-trained NLP model developed by Google.
- **CLIP**: Vision-language multimodal model developed by OpenAI.
- **GPT-2**: Generative Pre-trained Transformer developed by OpenAI.
- **OAuth2**: Authentication framework for securing APIs.

## Project Structure
```plaintext
.
├── CRUD
│   └── authen.py
├── LICENSE
├── assets
│   └── img
├── database.py
├── db
│   ├── SQLite.db
│   ├── SQLite.db-journal
│   ├── __init__.py
│   ├── credit_check.py
│   ├── db_gen.py
│   └── url_cache.py
├── models.py
├── neutralize
│   ├── NLP
│   │   ├── GPT_ana.py
│   │   ├── __init__.py
│   │   └── multimo.py
│   ├── neutralize.py
│   ├── neutralize_not_enc.py
│   └── reinforced
│       ├── __init__.py
│       └── nlp_model.py
├── readme.md
├── requirements.txt
├── schemas.py
├── server.py
├── service
│   ├── hashing.py
│   ├── jwttoken.py
│   └── oauth.py
└── uploaded_images
```

## License
[LICENSE](./LICENSE)