# Event Management System

## Description
This Django-based Event Management System allows users to create, view, update, and delete events. It also handles user registrations for these events, providing a robust platform for managing event logistics.

## Technology Stack
- **Backend**: Django 3.x
- **Database**: PostgreSQL
- **Containerization**: Docker, Docker Compose

## Setup Instructions

### Prerequisites
- Docker
- Docker Compose

### Getting Started

1. **Clone the Repository**
```
git clone https://github.com/degvor/event_manager.git
cd event_manager
```

2. **Build and Run the Docker Containers**
- This command will build the Docker images and start the services defined in `docker-compose.yml`:
```
docker-compose up -d
```

3. **Accessing the Application**
- Once the containers are running, the Django application will be accessible at `http://localhost:8000`.

4. **Making Changes and Rebuilding**
- If you make changes to the Dockerfile or the docker-compose configurations, rebuild the services:
```
docker-compose up -d --build
```

5. **Stopping the Application**
- To stop the running containers:
```
docker-compose down
```

### Using the Application

- **Admin Interface**
- You can access the Django admin interface by navigating to `http://localhost:8000/admin`.
- To use the admin interface, you will first need to create a superuser:
 ```
 docker-compose run app python manage.py createsuperuser
 ```

- **API Endpoints**
- The application exposes several API endpoints for managing events and registrations. Details of these endpoints can be found in the provided API documentation (link or location to API docs).

### Testing

- **Running Tests**
- To run tests, use the following command:
 ```
 docker-compose run app python manage.py test
 ```

## Deployment

- **Deployment instructions** on a production server or a cloud platform should include steps for setting environment variables securely and possibly using a more robust server than the Django development server.



