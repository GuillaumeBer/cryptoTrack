# Trading Pair Finder

This application provides a simple interface to search for cryptocurrency trading pairs.

## Backend

The backend is a Python application built with FastAPI. It exposes an API to fetch a list of tradable USDC pairs from Binance.

### Setup

1.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

2.  Run the backend server:
    ```bash
    uvicorn src.main:app --host 0.0.0.0 --port 8000
    ```

## Frontend

The frontend is a React application that allows users to search for trading pairs.

### Setup

1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```

2.  Install the required Node.js packages:
    ```bash
    npm install
    ```
    or
    ```bash
    yarn install
    ```

3.  Run the frontend development server:
    ```bash
    npm start
    ```
    or
    ```bash
    yarn start
    ```