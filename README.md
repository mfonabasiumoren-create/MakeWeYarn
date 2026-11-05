# \# MakeWeYarn

# 

# \## Mobile Telecom Service Operations Platform

# 

# \*\*MakeWeYarn\*\* is a simulated telecommunications service operations platform designed to demonstrate how a fictional Nigerian mobile network operator could manage subscriber services and automate essential operational processes.

# 

# The project combines application development, database management, containerization, orchestration, CI automation, and infrastructure security to demonstrate practical Cloud Engineering and DevOps skills.

# 

# > \*\*Project Disclaimer:\*\* MakeWeYarn is an educational and portfolio project. It uses simulated telecommunications operations and does not connect to a real mobile network, process real subscriber information, or provide actual telecom services.

# 

# \---

# 

# \## 1. Project Objectives

# 

# The project aims to demonstrate the design, development, deployment, and operation of a containerized telecommunications service platform.

# 

# Key objectives include:

# 

# \- Manage simulated mobile subscribers.

# \- Maintain mobile data plans and subscriptions.

# \- Automate subscription expiry processing.

# \- Track simulated cellular network sites.

# \- Record and manage network incidents.

# \- Expose application health information.

# \- Implement persistent relational database storage.

# \- Containerize application services using Docker.

# \- Orchestrate application workloads using Kubernetes.

# \- Automate validation and build processes using GitHub Actions.

# \- Apply container and Kubernetes security best practices.

# \- Introduce monitoring and observability using Prometheus and Grafana.

# 

# \---

# 

# \## 2. Technology Stack

# 

# | Technology | Purpose |

# |---|---|

# | Python | Application development |

# | Flask | REST API framework |

# | PostgreSQL 17 | Relational database |

# | Docker | Application containerization |

# | Docker Compose | Container orchestration for local development |

# | Kubernetes | Container orchestration and workload management |

# | Kustomize | Kubernetes manifest management |

# | GitHub Actions | Continuous Integration |

# | NGINX Ingress | Planned external application routing |

# | Prometheus | Planned metrics collection |

# | Grafana | Planned monitoring dashboards |

# 

# \---

# 

# \## 3. Current Project Architecture

# 

# The current implementation follows a containerized application architecture.

# 

# ```text

# &#x20;                 Developer

# &#x20;                     |

# &#x20;                     v

# &#x20;                GitHub Repo

# &#x20;                     |

# &#x20;                     v

# &#x20;             GitHub Actions CI

# &#x20;                     |

# &#x20;             Build and Test

# &#x20;                     |

# &#x20;                     v

# &#x20;              Docker Image

# &#x20;                     |

# &#x20;                     v

# &#x20;            Kubernetes Cluster

# &#x20;               (Docker Desktop)

# &#x20;                     |

# &#x20;            +--------+--------+

# &#x20;            |                 |

# &#x20;            v                 v

# &#x20;       API Service       Subscription

# &#x20;            |             Expiry CronJob

# &#x20;            |                 |

# &#x20;            v                 |

# &#x20;       Flask API <------------+

# &#x20;            |

# &#x20;            v

# &#x20;         Gunicorn

# &#x20;            |

# &#x20;            v

# &#x20;        PostgreSQL

# ```

# 

# \### Architecture Components

# 

# \*\*Application Layer\*\*

# \- Flask provides the API functionality.

# \- Gunicorn serves the application using multiple workers.

# \- PostgreSQL provides persistent data storage.

# 

# \*\*Container Layer\*\*

# \- Docker packages the application and its dependencies.

# \- The API image is built using a dedicated Dockerfile.

# \- Container execution incorporates security restrictions.

# 

# \*\*Orchestration Layer\*\*

# \- Kubernetes manages application deployment and service discovery.

# \- The API Deployment maintains two replicas.

# \- Kubernetes probes monitor application health.

# \- The CronJob automates subscription expiry processing.

# 

# \*\*Automation Layer\*\*

# \- GitHub Actions executes application compilation, automated tests, Kubernetes YAML validation, and Docker image builds.

# 

# \---

# 

# \## 4. Implemented Features

# 

# \### 4.1 Flask API

# 

# \- Flask-based application.

# \- Gunicorn application serving.

# \- Health endpoint for application and database connectivity checks.

# \- Subscription expiry processing endpoint.

# \- PostgreSQL database integration.

# 

# \### 4.2 PostgreSQL Database

# 

# \- PostgreSQL 17 running in a Docker container.

# \- Persistent relational database storage.

# \- Database credentials supplied through environment configuration.

# \- Kubernetes Secret integration for sensitive database credentials.

# 

# \### 4.3 Docker Containerization

# 

# The application is packaged into a Docker image:

# 

# `makeweyarn-api:v1`

# 

# Container security measures include:

# 

# \- Non-root application execution.

# \- Read-only root filesystem.

# \- Dropped Linux capabilities.

# \- Disabled privilege escalation.

# \- Process limits.

# \- Memory and CPU restrictions.

# \- Temporary writable storage through temporary filesystems.

# 

# \### 4.4 Kubernetes Deployment

# 

# The application is deployed to a local Kubernetes cluster using Docker Desktop.

# 

# Implemented Kubernetes resources:

# 

# | Resource | Purpose |

# |---|---|

# | Namespace | Isolates MakeWeYarn resources |

# | Deployment | Manages two API replicas |

# | Service | Exposes the API internally |

# | CronJob | Automates subscription expiry processing |

# | Secret | Stores database credentials |

# | ConfigMap | Supports configuration management |

# | Kustomization | Organizes Kubernetes manifests |

# 

# The API Deployment includes:

# 

# \- Two replicas.

# \- Readiness, liveness, and startup probes.

# \- Resource requests and limits.

# \- Non-root security context.

# \- RuntimeDefault seccomp profile.

# \- Read-only container filesystem.

# 

# \### 4.5 Subscription Expiry Automation

# 

# A Kubernetes CronJob automatically triggers subscription expiry processing.

# 

# | Configuration | Value |

# |---|---|

# | CronJob name | `makeweyarn-subscription-expiry` |

# | Schedule | `0 0 \* \* \*` |

# | Timezone | `Africa/Lagos` |

# | Execution frequency | Daily at midnight |

# | Concurrency policy | Forbid |

# | Retry limit | 2 |

# | Active deadline | 120 seconds |

# 

# The CronJob sends an HTTP POST request to:

# 

# `http://makeweyarn-api:8001/subscriptions/expire`

# 

# The shell execution uses `set -e` and curl failure handling to ensure unsuccessful requests result in a failed job rather than a false success.

# 

# A manual execution has been tested successfully.

# 

# \---

# 

# \## 5. Continuous Integration

# 

# MakeWeYarn uses GitHub Actions to automate application validation whenever changes are pushed to the `main` branch or a pull request targets that branch.

# 

# The workflow is defined in:

# 

# `.github/workflows/ci.yml`

# 

# \### CI Pipeline Stages

# 

# 1\. Check out the source repository.

# 2\. Set up Python 3.14.

# 3\. Install application dependencies.

# 4\. Compile the Python application.

# 5\. Execute automated unit tests.

# 6\. Validate Kubernetes YAML manifests.

# 7\. Build the Docker image.

# 

# \### Latest Verified CI Result

# 

# | Item | Result |

# |---|---|

# | Workflow | MakeWeYarn CI |

# | Latest verified run | #3 |

# | Commit | `65f4a77` |

# | Build and Test | Passed |

# | Total execution time | 29 seconds |

# 

# The successful workflow confirms that the configured automated checks completed successfully.

# 

# \---

# 

# \## 6. Repository Structure

# 

# ```text

# MakeWeYarn/

# │

# ├── app/

# │   └── app.py

# │

# ├── docker/

# │   └── Dockerfile

# │

# ├── k8s/

# │   ├── namespace.yaml

# │   ├── api-deployment.yaml

# │   ├── api-service.yaml

# │   ├── subscription-expiry-cronjob.yaml

# │   └── kustomization.yaml

# │

# ├── tests/

# │

# ├── .github/

# │   └── workflows/

# │       └── ci.yml

# │

# ├── requirements.txt

# ├── .dockerignore

# ├── .env

# └── README.md

# ```

# 

# \---

# 

# \## 7. Running the Project

# 

# \### Prerequisites

# 

# Install the following:

# 

# \- Python 3.14

# \- Docker Desktop

# \- Kubernetes enabled in Docker Desktop

# \- kubectl

# \- Git

# 

# \### Step 1: Clone the repository

# 

# ```bash

# git clone https://github.com/mfonabasiumoren-create/MakeWeYarn.git

# cd MakeWeYarn

# ```

# 

# \### Step 2: Configure environment variables

# 

# Create a local `.env` file containing the required database configuration.

# 

# Do not commit `.env` or expose database credentials in source control.

# 

# \### Step 3: Install Python dependencies

# 

# ```bash

# python -m pip install -r requirements.txt

# ```

# 

# \### Step 4: Run automated tests

# 

# ```bash

# python -m unittest discover -s tests -v

# ```

# 

# \### Step 5: Build the Docker image

# 

# ```bash

# docker build -f docker/Dockerfile -t makeweyarn-api:v1 .

# ```

# 

# \### Step 6: Deploy Kubernetes resources

# 

# Ensure your Kubernetes context points to Docker Desktop.

# 

# ```bash

# kubectl apply -k ./k8s

# ```

# 

# \### Step 7: Verify Kubernetes resources

# 

# ```bash

# kubectl get all -n makeweyarn

# ```

# 

# Check the CronJob:

# 

# ```bash

# kubectl get cronjobs -n makeweyarn

# ```

# 

# Check API deployment status:

# 

# ```bash

# kubectl get deployments -n makeweyarn

# ```

# 

# \---

# 

# \## 8. Security Considerations

# 

# Security has been incorporated into both the container and Kubernetes configurations.

# 

# Implemented controls include:

# 

# \- Non-root container execution.

# \- Read-only root filesystem.

# \- Linux capability restrictions.

# \- Disabled privilege escalation.

# \- Resource limits.

# \- Kubernetes Secret-based database credential management.

# \- RuntimeDefault seccomp profile.

# \- Application health probes.

# 

# These controls demonstrate practical container security and workload hardening.

# 

# \---

# 

# \## 9. Testing and Validation

# 

# The project has undergone several validation stages:

# 

# \- Automated Python unit testing.

# \- Python application compilation.

# \- Docker image build validation.

# \- Kubernetes YAML syntax validation.

# \- Kustomize build validation.

# \- Kubernetes server-side dry-run validation.

# \- API health checks.

# \- Database connectivity checks.

# \- Manual subscription expiry job execution.

# \- GitHub Actions CI execution.

# 

# \---

# 

# \## 10. Planned Enhancements

# 

# The following areas represent future development opportunities:

# 

# \- NGINX Ingress configuration and external API access.

# \- Prometheus metrics collection.

# \- Grafana monitoring dashboards.

# \- Enhanced subscriber lifecycle management.

# \- Mobile data plan management.

# \- Cellular network site management.

# \- Network incident recording and management.

# \- Horizontal Pod Autoscaling.

# \- Advanced application logging and alerting.

# \- Expanded integration and end-to-end testing.

# 

# \---

# 

# \## 11. Learning Outcomes

# 

# This project demonstrates practical experience in:

# 

# \- Python application development.

# \- REST API implementation.

# \- PostgreSQL database integration.

# \- Docker image creation and container security.

# \- Kubernetes workload deployment.

# \- Kubernetes networking and service discovery.

# \- Scheduled workload automation using CronJobs.

# \- Infrastructure configuration using YAML and Kustomize.

# \- Continuous Integration using GitHub Actions.

# \- Automated software testing.

# \- Cloud-native application architecture.

# 

# \---

# 

# \## 12. Project Information

# 

# \*\*Project:\*\* MakeWeYarn  

# \*\*Category:\*\* Cloud Engineering / DevOps Portfolio  

# \*\*Application:\*\* Simulated Telecommunications Operations Platform  

# \*\*Repository:\*\* https://github.com/mfonabasiumoren-create/MakeWeYarn  

# \*\*Branch:\*\* main  

# \*\*Status:\*\* Active development

# 

# \---

# 

# \## Author

# 

# Developed as a practical Cloud Engineering and DevOps portfolio project to demonstrate the design, automation, deployment, and operational management of containerized applications.

# 



