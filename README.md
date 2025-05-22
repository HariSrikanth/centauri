# alpha.me

An invite-only "dating platform for founders & investors" that aggregates activity from various sources, generates AI-written newsletters, and proposes mission-aligned matches.

## Core Features

- **Activity Aggregation**: Real-time integration with Gmail, Google Calendar, Twitter/X, GitHub (including private repos), and open-web mentions
- **AI-Generated Newsletters**: Weekly narratives threading member activities into readable stories
- **Intelligent Matchmaking**: Mission-aligned matching with auto-scheduled meetings and feedback loops
- **Privacy-First**: Public by default, private on demand, with frictionless integrations

## Tech Stack

- **Mobile UI**: SwiftUI
- **Web UI** (optional): Next.js + Tailwind + Clerk
- **API Gateway**: FastAPI (uvicorn)
- **Background Jobs**: Celery (Redis)
- **Database**: Postgres 15 + pgvector
- **Cache/SSE**: Redis (Cloud Memorystore)
- **AI Models**: OpenAI GPT-4 for summaries, BGE-base for embeddings
- **Cloud**: Google Cloud (Cloud Run, Pub/Sub, Cloud SQL, Cloud Storage, KMS, Secret Manager)
- **IaC**: Terraform
- **CI/CD**: GitHub Actions → Cloud Build

## Repository Structure

```
alpha-me/
├─ apps/
│  ├─ api/               # FastAPI entry (GraphQL + REST)
│  ├─ mobile/            # SwiftUI app (Xcode project)
│  ├─ web/               # Next.js (optional)
│  └─ workers/           # Celery tasks
├─ libs/
│  ├─ connectors/        # Integration connectors
│  ├─ ai/                # AI pipeline components
│  └─ schemas/           # Pydantic models
├─ infra/                # Terraform configurations
├─ docker/               # Dockerfiles & compose-dev.yml
└─ README.md
```

## Development Setup

### Prerequisites

- Python 3.11+
- Poetry for Python dependency management
- Docker and Docker Compose
- Xcode 15+ (for iOS development)
- Google Cloud SDK
- Terraform CLI

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/alpha-me.git
   cd alpha-me
   ```

2. Install Python dependencies:
   ```bash
   poetry install
   ```

3. Start development services:
   ```bash
   docker-compose -f docker/compose-dev.yml up -d
   ```

4. Run the FastAPI development server:
   ```bash
   poetry run uvicorn apps.api.main:app --reload
   ```

5. Start Celery workers:
   ```bash
   poetry run celery -A apps.workers.celery_app worker --loglevel=info
   ```

### Environment Variables

Create a `.env` file in the root directory with:

```env
# API Configuration
API_VERSION=v1
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/alpha_me

# Redis
REDIS_URL=redis://localhost:6379/0

# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# OpenAI
OPENAI_API_KEY=your-api-key

# Clerk
CLERK_SECRET_KEY=your-secret-key

# Other OAuth Providers
GITHUB_CLIENT_ID=your-client-id
GITHUB_CLIENT_SECRET=your-client-secret
TWITTER_API_KEY=your-api-key
TWITTER_API_SECRET=your-api-secret
```

## API Documentation

Once the development server is running, visit:
- REST API docs: http://localhost:8000/docs
- GraphQL playground: http://localhost:8000/graphql

## Testing

Run the test suite:

```bash
poetry run pytest
```

## Deployment

### Prerequisites

1. Install required tools:
   ```bash
   # Install Google Cloud SDK
   brew install google-cloud-sdk  # macOS
   # or visit https://cloud.google.com/sdk/docs/install for other platforms

   # Install Terraform
   brew install terraform  # macOS
   # or visit https://developer.hashicorp.com/terraform/downloads for other platforms
   ```

2. Create a Google Cloud account and set up billing
   - Visit https://console.cloud.google.com
   - Create a new project or select an existing one
   - Enable billing for the project

### Initial Setup

1. Clone the repository and navigate to it:
   ```bash
   git clone https://github.com/your-org/alpha-me.git
   cd alpha-me
   ```

2. Create a `.env` file with your configuration:
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

3. Create a `terraform.tfvars` file in the `infra` directory:
   ```bash
   cd infra
   cat > terraform.tfvars << EOL
   project_id  = "alpha-me-<your-project-id>"
   region      = "us-central1"
   db_password = "$(openssl rand -base64 32)"  # Generates a secure random password
   environment = "prod"
   EOL
   ```

4. Initialize Google Cloud:
   ```bash
   # Login to Google Cloud
   gcloud auth login
   gcloud auth application-default login

   # Set your project
   gcloud config set project alpha-me-<your-project-id>

   # Enable required APIs
   gcloud services enable \
     cloudresourcemanager.googleapis.com \
     compute.googleapis.com \
     sqladmin.googleapis.com \
     redis.googleapis.com \
     secretmanager.googleapis.com \
     run.googleapis.com \
     storage.googleapis.com \
     iam.googleapis.com

   # Create a GCS bucket for Terraform state
   gsutil mb -l us-central1 gs://alpha-me-terraform-state
   ```

### Deploy Infrastructure

1. Initialize and apply Terraform:
   ```bash
   cd infra
   terraform init
   terraform plan
   terraform apply
   ```

2. After successful deployment, Terraform will output:
   - API URL
   - Database private IP
   - Redis host
   - Storage bucket name

3. Store secrets in Google Secret Manager:
   ```bash
   # For each secret in your .env file
   echo -n "your-secret-value" | gcloud secrets versions add alpha-me-clerk-secret-key --data-file=-
   echo -n "your-secret-value" | gcloud secrets versions add alpha-me-openai-api-key --data-file=-
   # ... repeat for other secrets
   ```

### Deploy Application

1. Build and push Docker images:
   ```bash
   # Build images
   docker build -t gcr.io/alpha-me-<your-project-id>/alpha-me-api:latest -f docker/Dockerfile.prod .
   docker build -t gcr.io/alpha-me-<your-project-id>/alpha-me-worker:latest -f docker/Dockerfile.worker.prod .

   # Push to Google Container Registry
   docker push gcr.io/alpha-me-<your-project-id>/alpha-me-api:latest
   docker push gcr.io/alpha-me-<your-project-id>/alpha-me-worker:latest
   ```

2. The application will automatically deploy to Cloud Run via GitHub Actions when you push to main.

### Verify Deployment

1. Check Cloud Run services:
   ```bash
   gcloud run services list
   ```

2. Test the API:
   ```bash
   curl https://alpha-me-api-xxxxx-uc.a.run.app/health
   ```

3. Monitor the application:
   ```bash
   # View logs
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=alpha-me-api"

   # View metrics
   open https://console.cloud.google.com/monitoring/dashboards
   ```

### Common Operations

1. Update infrastructure:
   ```bash
   cd infra
   terraform plan
   terraform apply
   ```

2. Update application:
   ```bash
   # Make your changes
   git add .
   git commit -m "Your changes"
   git push origin main
   # GitHub Actions will handle the deployment
   ```

3. Access the database:
   ```bash
   # Get the connection name
   gcloud sql instances describe alpha-me-postgres --format='get(connectionName)'

   # Connect using Cloud SQL Auth proxy
   cloud-sql-proxy <connection-name>
   ```

4. View costs:
   ```bash
   open https://console.cloud.google.com/billing
   ```

### Troubleshooting

1. If Cloud Run services fail to start:
   - Check logs: `gcloud logging read "resource.type=cloud_run_revision"`
   - Verify secrets are set: `gcloud secrets list`
   - Check IAM permissions: `gcloud projects get-iam-policy alpha-me-<your-project-id>`

2. If database connection fails:
   - Verify VPC connectivity
   - Check database logs: `gcloud sql logs tail alpha-me-postgres`
   - Ensure Cloud SQL Auth proxy is running

3. If Redis connection fails:
   - Check Memorystore status
   - Verify VPC connectivity
   - Check Redis logs

### Cleanup

To destroy all resources (be careful, this is irreversible):
```bash
cd infra
terraform destroy
```

## Contributing

1. Create a feature branch from `main`
2. Make your changes
3. Run tests and linting
4. Submit a pull request

### License

Proprietary - All rights reserved

## Implementation Status

### Core Features

| Feature | Status | Notes |
|---------|--------|-------|
| Activity Aggregation | 🟡 In Progress | Tasks defined, ingestion logic pending |
| AI-Generated Newsletters | 🟡 In Progress | Tasks defined, AI generation pending |
| Intelligent Matchmaking | 🟡 In Progress | Tasks defined, algorithm pending |
| Privacy-First | 🟡 In Progress | Infrastructure ready, controls pending |

### Tech Stack

| Component | Status | Notes |
|-----------|--------|-------|
| Mobile UI (SwiftUI) | 🔴 Not Started | Planned for future |
| Web UI (Next.js) | 🔴 Not Started | Optional, planned for future |
| API Gateway (FastAPI) | ✅ Complete | REST + GraphQL endpoints ready |
| Background Jobs (Celery) | ✅ Complete | Task framework implemented |
| Database (Postgres) | ✅ Complete | Schema and migrations ready |
| Cache/SSE (Redis) | ✅ Complete | Configured and integrated |
| AI Models | 🟡 In Progress | Tasks defined, implementation pending |
| Cloud (GCP) | ✅ Complete | Infrastructure as code ready |
| IaC (Terraform) | ✅ Complete | All resources defined |
| CI/CD (GitHub Actions) | ✅ Complete | Automated deployment pipeline |

### Next Steps

1. **Activity Aggregation**
   - Implement Gmail OAuth and email ingestion
   - Implement Calendar event processing
   - Implement Twitter API integration
   - Implement GitHub API integration
   - Implement web mention crawling

2. **AI Pipeline**
   - Implement narrative generation using GPT-4
   - Implement embedding generation using BGE
   - Implement newsletter formatting and delivery
   - Implement matchmaking algorithm
   - Implement feedback processing

3. **Privacy & Security**
   - Implement data access controls
   - Implement privacy settings API
   - Implement data retention policies
   - Implement audit logging

4. **User Interface**
   - Start SwiftUI mobile app development
   - (Optional) Implement Next.js web interface
   - Implement real-time updates
   - Implement push notifications

### Contributing

We welcome contributions! Please check the [Contributing Guide](CONTRIBUTING.md) for details.

1. Create a feature branch from `main`
2. Make your changes
3. Run tests and linting
4. Submit a pull request

### License

Proprietary - All rights reserved