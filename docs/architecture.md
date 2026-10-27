# MakeWeYarn — System Architecture

## 1. Overview

MakeWeYarn is a telecommunications-modeled service operations platform that simulates the core digital operations of a fictional Nigerian mobile network operator.

The system will be developed incrementally, starting with a REST API and PostgreSQL database before introducing container orchestration, continuous integration, and observability.

## 2. Application Components

### Client
An API client sends HTTP requests to the platform and receives JSON responses.

### REST API
Python and Flask provide endpoints for:
- Subscriber management
- Mobile data plans
- Subscriber subscriptions
- Simulated cellular network sites
- Network incident management
- Application health checks
- Application metrics

### Database
PostgreSQL stores subscriber records, data plans, subscriptions, network sites, and incidents.

### Containerization
Docker packages the application and its dependencies. Docker Compose will support local development alongside PostgreSQL.

### Orchestration
Kubernetes will manage application deployment, service discovery, health probes, scaling, and persistent database storage.

### Traffic Routing
NGINX Ingress will route HTTP requests to the application when the Kubernetes environment is configured.

### Continuous Integration
GitHub Actions will automate application tests, configuration validation, and Docker image builds.

### Observability
Prometheus will collect supported application and infrastructure metrics. Grafana will visualize those metrics in dashboards.

## 3. Request Flow

1. A client sends an HTTP request.
2. NGINX Ingress routes the request when ingress is configured.
3. The Flask API validates and processes the request.
4. The API reads or writes data in PostgreSQL when required.
5. The API returns a JSON response.
6. Monitoring tools collect available metrics independently of normal request processing.

## 4. Security Principles

- Use fictional subscriber data.
- Keep database credentials out of source control.
- Use environment variables or appropriate secret-management mechanisms for configuration.
- Run application containers as a non-root user where practical.
- Apply container resource limits and health probes.
- Validate request data and handle errors safely.
- Avoid exposing database services publicly.

## 5. Deployment Strategy

Development will proceed in stages:

1. Build and test the REST API.
2. Integrate PostgreSQL persistence.
3. Containerize the application.
4. Validate the local Docker Compose environment.
5. Deploy the application to local Kubernetes.
6. Configure ingress and scaling.
7. Implement automated CI checks.
8. Add metrics, dashboards, and resilience tests.

## 6. Scope and Limitations

MakeWeYarn is a learning and portfolio project. It will simulate telecom operations and will not connect to a real mobile network, carrier billing system, or subscriber-management platform.

The architecture describes the intended design. Components will be marked as implemented only after they have been built and verified.
