# Neutralize

<div align="center">
    <img src="./assets/img/neutralize.png" alt="Neutralize Icon" width="100" height="100">
    <h1>Neutralize</h1>
</div>

**This is the backend repository for Neutralize.** This project was developed during the [HackIreland](https://devpost.com/software/neutraliser) hackathon. And it was awarded the **Runner-up** prize. 🎉

> This repository is no longer maintained after the completion of hackathon. For more information, see the [Note](#note) section.

In today's digital age, encountering biased information is almost inevitable. To address this challenge, we developed Neutralize, a Chrome extension designed to help users identify and understand biases in the articles they read. By offering both quick insights and in-depth analyses, Neutralize empowers users to approach information critically and make informed decisions.

<h3> Features </h3>

- **Instant Bias Detection**: As you browse, Neutralize analyzes the content of each webpage, providing an immediate assessment of its bias—left, center, or right.
- **Alternative Perspectives**: For every article, Neutralize suggests alternative sources covering the same topic, allowing users to explore diverse viewpoints.
- **Reinforcement Learning**: By labeling articles, users contribute to the continuous improvement of our Natural Language Processing (NLP) model, enhancing its accuracy over time.
- **Premium GPT Analysis**: For users seeking a deeper understanding, Neutralize offers a premium feature that utilizes OpenAI's GPT model to provide comprehensive bias analyses.

## Note <!-- omit in toc -->
This repository is no longer maintained after the completion of hackathon. 

The new repository **Neutralise-backend** can be found [here](https://github.com/Eric-xin/neutralise-backend.git)
New features include:
- [x] MongoDB integration
- [x] Encrypted user api
- [x] Signup with access control and rate limit
- [x] Modularized endpoints
- [x] Improved readability and maintainability
- [x] Cache functionality
- [x] Credit check for users
- [x] Multicontext analysis
- [x] Cache-integrated api
Other features like local language model, video analysis, and more are coming soon.

## Table of Contents <!-- omit in toc -->

- [Neutralize](#neutralize)
  - [Features](#features)
  - [Technologies](#technologies)
  - [Installation](#installation)
  - [Usage](#usage)
  - [API Endpoints](#api-endpoints)
    - [Authentication](#authentication)
    - [User Management](#user-management)
    - [Neutralise](#neutralise)
  - [Technologies](#technologies-1)
  - [Project Structure](#project-structure)
  - [License](#license)

## Features

- **User Authentication**: Register, login, and manage user accounts.
- **Bias Detection**: Analyze text for political bias using NLP model.
- **Bias Explanation**: Generate explanations for detected bias using OpenAI's GPT.
- **Database Integration**: Store and manage user data using SQLite.
- **API Endpoints**: Expose functionalities through RESTful API endpoints.
- **Multimodal Analysis**: Analyze text and image for bias with multiple contexts.

## Technologies
<!-- badges -->
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-333?style=for-the-badge&logo=pydantic&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-333?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![BERT](https://img.shields.io/badge/BERT-333?style=for-the-badge&logo=bert&logoColor=white)
![CLIP](https://img.shields.io/badge/CLIP-333?style=for-the-badge&logo=clip&logoColor=white)
![GPT-2](https://img.shields.io/badge/GPT-2-333?style=for-the-badge&logo=gpt&logoColor=white)
![OAuth2](https://img.shields.io/badge/OAuth2-333?style=for-the-badge&logo=oauth&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-333?style=for-the-badge&logo=openai&logoColor=white)
![Transformer](https://img.shields.io/badge/Transformer-333?style=for-the-badge&logo=transformer&logoColor=white)

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