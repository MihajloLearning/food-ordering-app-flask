# Food Ordering App (Flask & Dockerized)

## Project Overview

This is a Dockerized food ordering web application built with Python Flask for the backend and a pure HTML, CSS, and JavaScript frontend. It supports restaurant and menu item management, collaborative ordering with "open" and "locked" order statuses, and displays order history.

### Key Technologies:
- **Backend:** Python Flask, Flask-SQLAlchemy (ORM)
- **Database:** PostgreSQL
- **Frontend:** HTML, CSS, JavaScript (single-page application)
- **Containerization:** Docker, Docker Compose

### Architecture:
The application consists of two main services orchestrated by Docker Compose:
1.  **`web` service:** The Flask application, serving the frontend and providing RESTful API endpoints.
2.  **`db` service:** A PostgreSQL database instance for data persistence.

### Database Schema:
The application uses the following models (defined in `app/models.py`):
-   `Restaurant`: Manages restaurant information.
-   `MenuItem`: Stores menu items associated with restaurants.
-   `Order`: Represents an order, including `orderer_name`, `created_at`, and a `status` (`open` or `locked`).
-   `OrderItem`: Details individual items within an order, including the `user_name` who added the item.

## Building and Running

The application is designed to be run using Docker Compose.

### Prerequisites:
-   Docker and Docker Compose installed.

### Setup:
1.  **Environment Variables:** Create a `.env` file in the project root (`food-ordering-app-flask/`) with the following variables (replace with your desired values):
    ```
    DATABASE_URL=postgresql://user:password@db:5432/food_ordering_db
    DB_USER=user
    DB_PASSWORD=password
    DB_NAME=food_ordering_db
    FLASK_APP=run.py
    FLASK_RUN_HOST=0.0.0.0
    ```
2.  **Build and Run with Docker Compose:**
    Navigate to the project root directory (`food-ordering-app-flask/`) and run:
    ```bash
    docker-compose up --build -d
    ```
    This command will:
    -   Build the `web` service Docker image (based on `Dockerfile`).
    -   Start the `db` (PostgreSQL) and `web` (Flask) services.
    -   The Flask application will automatically create the database schema on startup using `db.create_all()`.

### Accessing the Application:
Once the containers are running, the application will be accessible in your web browser at `http://localhost:5000`.

## Development Conventions

-   **Flask Application Structure:** The Flask application follows a standard structure with an `app` directory containing `__init__.py` (app initialization), `models.py` (database models), and `routes.py` (API endpoints and view logic).
-   **Database Management:** Database schema creation is handled directly by `db.create_all()` within `app/__init__.py` on application startup. Flask-Migrate is not currently in use.
-   **Frontend:** The frontend is a single HTML file (`app/templates/index.html`) that uses vanilla JavaScript to interact with the backend API and dynamically update the UI.
-   **Styling:** Basic CSS is embedded in `index.html`, utilizing CSS variables for easy theme adjustments. A dark mode feature is implemented with a toggle and preference persistence in `localStorage`.
-   **Debugging:** `console.log` statements are present in the frontend JavaScript (e.g., for restaurant creation) to aid in debugging network requests and responses.