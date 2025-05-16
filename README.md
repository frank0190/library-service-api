# Library Service API

## Project Description
A web-based application for managing books, users, borrowings, 
and sending notifications. The system allows users to borrow books, 
track active borrowings, and receive Telegram notifications on borrowing creation.

## Features
- JWT authentication for secure API access.
- Manage books, users, and borrowing records.
- Permissions system:
  -  Admins can create, update, and delete books.
  -  All users (even unauthenticated) can list books.
  -  Borrowings are restricted to authenticated users.
- Borrowing system with inventory validation.
- Telegram notifications for new borrowings.
- API documentation available at `/api/doc/swagger/` (Swagger UI), `/api/doc/redoc/` (Redoc)

## Technologies Used
- **Backend:** Django Framework, Django REST Framework
- **Authentication:** JWT (via djangorestframework-simplejwt)
- **Database:** PostgreSQL
- **Notifications:** Telegram API
- **Containerization:** Docker, Docker Compose

## Installation
### Python 3 must be installed
1. **Clone the repository:**
   ```bash
   git clone https://github.com/frank0190/library-service-api.git
   cd library_service_api
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Linux/Mac
   venv\Scripts\activate  # For Windows
3. **Install dependencies:**
    ```bash
   pip install -r requirements.txt
4. **Create a .env file:**
   ```bash
   cp env.sample .env
   ```
   - Open .env and fill in the required environment variables 
   (e.g., SECRET_KEY, POSTGRES_USER, POSTGRES_PASSWORD, etc.).
   - **Important:** Since the database runs in a Docker container, set
   POSTGRES_HOST to the service name defined in your docker-compose.yml (for example, db).
5. **Start the database container:**
   ```bash
   docker-compose up -d db
   ```
6. **Apply database migrations:**
    ```bash
   python manage.py migrate
7. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
8. **Start the development server:**
    ```bash
   python manage.py runserver
9. **Create and Configure a Telegram Bot:**

- Open Telegram and search for `@BotFather`.
- Start a chat with BotFather and send the command `/newbot`.
- Follow the instructions to choose a name and a username for your bot.
- After creation, BotFather will provide you with a bot token.
- Store this token in your `.env` file as BOT_TOKEN.
- To obtain the chat ID (where notifications will be sent):
  - Add your bot to a Telegram group or create a chat.
  - Open a browser and navigate to `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates`
  - The response will contain a `chat.id` - copy this value and add this to `.env` as CHAT_ID
   
## Containerized Deployment (For Full Environment)

1. **Create and configure the .env file:**
   ```bash
   cp env.sample .env
2. **Build and run the containers:**
   ```bash
   docker-compose up --build
   ```
   This command will build the Docker images and start the
   containers for the web application and PostgreSQL database.

## API Endpoints


- `/api/books/` - List all books or create (admin only)
- `/api/books/{id}/` - Retrieve/update/delete book (admin only)


- `/api/borrowings/` - List borrowings (filtered by user, active status for admin) or create (requires authentication)
- `/api/borrowings/{id}/` - Retrieve borrowing detail info
- `/api/borrowings/{id}/return/` - Return a borrowed book


- `/api/user/register/` - Register new user
- `/api/user/token/` - Get token for user
- `/api/user/me/` - Manage user data
