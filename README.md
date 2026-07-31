## Multi_Tenant_Booking_System

A multi-tenant restaurant booking system built with Django and
Django REST Framework.

Users can browse restaurants using various filters, check available
reservation time slots, make bookings, and leave reviews with ratings.
Restaurant owners and staff can manage reservations, members, menus,
opening hours, and customer bans through dedicated endpoints.

The booking process is designed to be safe in concurrent environments
by preventing race conditions during table reservations. The system
also uses Celery to send booking confirmation and reminder emails,
as well as to automatically update booking statuses.

The project includes nearly **500 automated tests** written with
**pytest**, covering business logic, API endpoints, permissions,
and edge cases.

## Tech Stack

- Python
- Django
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- Docker
- GitHub Actions
- Docker Compose
- Pytest
- JWT Authentication (SimpleJWT)
- Django Filter
- Swagger / OpenAPI (drf-spectacular)
- Pillow
- Ruff
- pre-commit


## Features

- **Restaurant search** — filter restaurants by city, reservation duration minutes and cuisine type,
  with sorting by average review rating
- **Restaurant management** — owners configure opening hours, tables,
  menus, and staff roles (manager / staff) for their restaurants
- **Menus** — owners and managers create and manage restaurant dishes
  with prices
- **Booking system** — availability checks based on opening hours,
  breaks, and special exceptions, with race-condition-safe table
  reservations and a complete booking lifecycle
  (pending → confirmed → completed / cancelled / no_show)
- **Booking management** — users can check available reservation
  time slots, while restaurant staff can view daily booking schedules
  for their restaurants
- **Email notifications** — booking confirmation and reminder emails sent
  asynchronously using Celery, with automatic cancellation of unconfirmed
  bookings
- **Reviews and ratings** — users can rate and review restaurants they
  have visited
- **User bans** — restaurant staff can manually ban users, with automatic
  bans after exceeding the no-show threshold
- **Account management** — email-verified registration (verification code sent via
  email), JWT-based authentication with token blacklisting on logout, password change,
  and password reset via emailed verification code
- **Rate limiting** — configurable API throttling with stricter limits
  on authentication endpoints to prevent brute-force attacks
- **Caching** — Redis-backed caching for frequently accessed endpoints
- **Pagination** — list endpoints return paginated results with configurable page size
- **API documentation** — complete OpenAPI documentation with detailed
  request and response schemas available through Swagger UI

## Continuous Integration

The project uses GitHub Actions to automatically run the test suite
on every push and pull request.

The CI pipeline includes:

- Installing project dependencies
- Running database migrations
- Executing the pytest test suite
- Checking code quality with Ruff

## Project Structure

The project is divided into multiple Django applications, each responsible
for a specific domain:

```
Multi_Tenant_Booking_System/
│
├── accounts/              # User authentication and custom user model
├── restaurants/           # Restaurant management and restaurant endpoints
├── memberships/           # Restaurant roles and staff management
├── available_rules/       # Opening hours, breaks, and special exceptions
├── booking_system/        # Reservations, booking lifecycle, and email tasks
├── menus/                 # Restaurant menus and dishes
├── user_reviews/          # Reviews and ratings
│
├── config/                # Django project configuration
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── manage.py
```

## Installation
### 1. Clone the repository
```bash
git clone https://github.com/Guciowsky333/multi-tenant-booking-system

cd Multi_Tenant_Booking_System
```
### 2. Create environment variables
Create a `.env` file in the project root directory and configure
the required environment variables.
Example:
```env
DJANGO_DEBUG=True

DJANGO_SECRET_KEY=your_secret_key

POSTGRES_DB=booking_system
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432

REDIS_URL=redis://redis:6379/0
```
### 3. Run the application using Docker Compose
```bash
docker compose up --build
```
### 4. Apply database migrations
```bash
docker compose exec web python manage.py migrate
```
### 5. Create a superuser (optional)
```bash
docker compose exec web python manage.py createsuperuser
```

## Running tests
The project contains nearly **500 automated tests** written with
**pytest**.

```bash
# Run all tests 
docker-compose exec web pytest
# Run a single test
docker-compose exec web pytest -k "test_name"
```

## API Documentation
After running the project, API documentation is available at:
### Swagger UI
http://localhost:8000/api/docs/
### OpenAPI Schema
http://localhost:8000/api/schema/

## Author

**Kacper Kubiak**
- GitHub : [Multi_Tenant_Booking_System](https://github.com/Guciowsky333/multi-tenant-booking-system)


