# BNDES Balance Sheet - Production AWS Architecture

[![01 - Code Quality & Lint](https://github.com/thentsation/bndes-data-pipeline/actions/workflows/01-lint-check.yml/badge.svg)](https://github.com/thentsation/bndes-data-pipeline/actions/workflows/01-lint-check.yml)
[![02 - Unit Tests](https://github.com/thentsation/bndes-data-pipeline/actions/workflows/02-unit-tests.yml/badge.svg)](https://github.com/thentsation/bndes-data-pipeline/actions/workflows/02-unit-tests.yml)

An in-depth write-up of the productization of this project — a fetch failure that was silently swallowed and reported as "no data" instead of an error — is available in [ARTIGO.md](ARTIGO.md) (pt-br) / [ARTIGO.en-us.md](ARTIGO.en-us.md) (en-us).

This project implements a production-ready system for fetching, processing, and storing BNDES balance sheet data on AWS using serverless technologies. The system automatically retrieves data from the BNDES Open Data API, processes it for consistency, and stores the processed data in S3 as Parquet files with date partitioning.

## Local development

```bash
make install        # creates .venv, installs requirements.txt + requirements-dev.txt
make test           # pytest, 90% coverage gate
make lint            # ruff check
make typecheck        # mypy
make docker-run        # builds the Lambda image and runs it locally against LOCAL_OUTPUT_DIR
```

CI (`01`-`04`) runs ruff + mypy + pip-audit, pytest across Python 3.11/3.12, a Trivy scan of the Lambda image, and a real build+run smoke test (POSTs a test payload to the Lambda Runtime Interface Emulator). Dependabot covers pip, the Lambda's Docker base image, Terraform providers/modules, and GitHub Actions. `terraform plan`/`apply`/`destroy` stay manual, human-triggered actions against real AWS infrastructure - nothing in CI touches them.

## Overview

This project provides automated access to the BNDES Balance Sheet data, which contains the bank's financial statements presented in three standards:
- **BRGAAP** (Brazilian Generally Accepted Accounting Principles)
- **IFRS** (International Financial Reporting Standards)
- **Prudential Conglomerate**

The system provides:

- **Automated Data Ingestion**: Automated fetching of BNDES balance sheet data by year
- **Data Processing**: Data cleaning and consolidation from multiple resources
- **Monitoring**: Complete observability with CloudWatch logs, metrics, alarms, and dashboards
- **Alerting**: SNS notifications for failures and critical errors
- **Infrastructure as Code**: Complete Terraform configuration for reproducible deployments

## Features

- **Automated Data Pipeline**: Daily execution via CloudWatch Events at 03:00 UTC
- **Serverless Architecture**: Lambda with Docker containers in ECR for easy deployment and scaling
- **Data Persistence**: Processed data stored in S3 as Parquet files with KMS encryption
- **Comprehensive Monitoring**: CloudWatch logs, custom metrics, alarms, and dashboards
- **Alert System**: SNS notifications for failures, errors, and metric thresholds
- **Error Handling**: Dead Letter Queue (SQS) for failed Lambda executions
- **CI/CD Pipeline**: Automated testing, security scanning, building, and deployment via GitHub Actions
- **Security**: KMS encryption, least-privilege IAM policies, versioned state, no hardcoded credentials
- **Infrastructure as Code**: Complete Terraform configuration with modular architecture

## Architecture

### System Architecture

```
┌─────────────┐
│  CloudWatch │
│   Events    │ (Daily trigger at 03:00 UTC)
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────┐     ┌─────────┐
│   Lambda    │────▶│    S3    │     │   ECR   │
│  Function   │     │  Bucket  │     │   Repo  │
│  (Docker)   │     │(Parquet) │     │         │
│             │     │Partition │     │         │
│  Fetch API  │     │ by Date  │     │ Docker  │
│  Process    │     │KMS Enc   │     │ Images  │
│  Upload     │     │          │     │         │
└──────┬──────┘     └──────────┘     └─────────┘
       │
       ▼ (failures)
┌─────────────┐
│  SQS DLQ    │
│ (Failed     │
│  Messages)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│ CloudWatch │────▶│    SNS      │
│  + Alarms  │     │ (Email)     │
│            │     │             │
│  Errors    │     │  Alert Sub  │
│  Duration  │     │  scriptions│
│  Throttles │     │             │
└─────────────┘     └─────────────┘
```

### Data Flow

1. **Trigger**: CloudWatch Events triggers the Lambda function daily at 03:00 UTC
2. **Fetch Data**: Lambda fetches data from the BNDES Open Data API
3. **Process Data**: The data is cleaned and consolidated from multiple resources
4. **Store Data**: Processed data is converted to Parquet format and uploaded to S3
5. **Partitioning**: Files are stored with date-based partitioning (e.g., `s3://bucket/2026/01/01/data.parquet`)
6. **Monitoring**: All operations are logged to CloudWatch Logs
7. **Alerting**: Errors trigger CloudWatch Alarms, which send SNS notifications

### Component Details

#### Lambda Function
- **Runtime**: Python 3.11 in Docker container
- **Timeout**: 900 seconds (15 minutes)
- **Memory**: 1024 MB
- **Triggers**: CloudWatch Events (cron expression)
- **Error Handling**: Failed events sent to SQS DLQ for investigation

#### ECR Repository
- Stores Docker images for the Lambda function
- Image scanning enabled for security
- Lifecycle policies for image management

#### S3 Bucket
- Stores processed data as Parquet files
- KMS encryption at rest
- Date-based partitioning (year/month/day/)
- Versioning enabled for data recovery
- Blocks all public access

#### CloudWatch
- **Logs Group**: Stores Lambda execution logs with 30-day retention
- **Metrics**: Custom metrics for errors, duration, throttles
- **Alarms**: Alarms for error rates, duration thresholds
- **Dashboard**: Visual overview of system health and performance

#### SNS Topic
- Email notifications for:
  - Lambda execution failures
  - Error rate threshold breaches
  - Duration threshold breaches
  - DLQ message accumulation

#### SQS DLQ
- Receives failed Lambda invocations
- Enables investigation of failures
- Supports manual reprocessing of failed events

## Project Structure

```
bndes-data-pipeline/
├── src/                        # Source code
│   ├── __init__.py
│   ├── app.py                  # Lambda entrypoint with S3 upload logic
│   ├── fetch_data.py           # BNDES API data fetching module
│   └── process_data.py         # Data processing and transformation module
├── Dockerfile                  # Docker image for Lambda (Python 3.11)
├── requirements.txt            # Python dependencies
├── data/                       # Local data directory (gitignored)
│   └── bndes-data/
│       └── 2026/
│           └── 01/
│               └── 01/
├── notebooks/                  # Jupyter notebooks for analysis
│   └── bndes_analysis.ipynb    # Data analysis and visualization
├── terraform/                  # Infrastructure as Code
│   ├── main.tf                 # Main Terraform configuration
│   ├── providers.tf            # Provider and backend configuration
│   ├── variables.tf            # Input variables
│   ├── outputs.tf              # Output values
│   ├── terraform.tfvars        # Variable values
│   ├── .gitignore              # Terraform state files
│   └── modules/                # Reusable Terraform modules
│       ├── ecr/                # ECR repository module
│       │   ├── main.tf
│       │   ├── variables.tf
│       │   └── outputs.tf
│       ├── lambda/             # Lambda function module
│       │   ├── main.tf
│       │   ├── variables.tf
│       │   └── outputs.tf
│       ├── s3/                 # S3 bucket module
│       │   ├── main.tf
│       │   ├── variables.tf
│       │   └── outputs.tf
│       ├── monitoring/         # CloudWatch + SNS module
│       │   ├── main.tf
│       │   ├── variables.tf
│       │   └── outputs.tf
│       └── schedule/           # CloudWatch Events module
│           ├── main.tf
│           ├── variables.tf
│           └── outputs.tf
├── tests/                      # Unit tests
│   ├── __init__.py
│   ├── test_app.py
│   ├── test_fetch_data.py
│   └── test_process_data.py
├── scripts/                    # Utility scripts
│   └── setup-terraform-backend.sh
├── .github/
│   └── workflows/              # GitHub Actions CI/CD pipelines
│       ├── 01-lint-check.yml          # Code quality checks
│       ├── 02-unit-tests.yml          # Unit tests with coverage
│       ├── 03-security-scan.yml       # Security scanning
│       ├── 04-docker-build-test.yml   # Docker build and test
│       ├── 05-terraform-plan.yml      # Terraform plan (PRs)
│       └── 06-deploy.yml              # Deployment to production
├── docker-compose.yml         # Docker Compose for local development
├── Dockerfile                  # Lambda Docker image
├── README.md                   # This file
└── .gitignore                  # Git ignore patterns
```

## Data Processing

### Data Source

The system fetches data from the BNDES Open Data API's "balanco-patrimonial" dataset, which contains the BNDES Balance Sheet presented in three accounting standards:
- **BRGAAP** (Brazilian Generally Accepted Accounting Principles)
- **IFRS** (International Financial Reporting Standards)
- **Prudential Conglomerate**

The data includes financial information such as:
- Account descriptions and classifications
- Financial values and balances
- Period information
- Standard-specific metrics

### Data Transformation

The `process_data.py` module performs data cleaning and preparation:

1. **Data Cleaning**: Removes empty rows and cleans text fields (e.g., strips whitespace from descriptions)
2. **Data Consolidation**: Combines multiple resources (e.g., different accounting standards) into a single consolidated dataset
3. **Metadata Addition**: Adds source resource name and ID for traceability
4. **Validation**: Ensures data integrity before storage

### Output Format

Processed data is stored in Parquet format with the following benefits:
- Columnar storage for efficient querying
- Compression for reduced storage costs
- Schema evolution support
- Partitioned by date for optimized queries

## Quick Start

### Prerequisites

Before you begin, ensure you have the following:

- **AWS Account** with appropriate permissions (Lambda, S3, CloudWatch, ECR, SQS, SNS, KMS, IAM)
- **AWS CLI** installed and configured with credentials
- **Docker** installed (for building Lambda images)
- **Terraform** >= 1.5.0 installed
- **Python 3.11** installed
- **GitHub account** (for CI/CD)
- **jq** (optional, for parsing Terraform outputs)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/bndes-data-pipeline.git
cd bndes-data-pipeline
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Terraform Backend

The Terraform state is stored in S3 for persistence and collaboration. Run the setup script to create the necessary AWS resources:

```bash
chmod +x scripts/setup-terraform-backend.sh
./scripts/setup-terraform-backend.sh
```

This script will:
- Create an S3 bucket for Terraform state
- Create a DynamoDB table for state locking
- Enable versioning and encryption

### 4. Configure Variables

Edit `terraform/terraform.tfvars` with your desired values:

```hcl
aws_region          = "us-east-1"
project_name        = "bndes-data-pipeline"
lambda_timeout      = 900
lambda_memory_size  = 1024
alarm_email         = "your-email@example.com"
log_retention_days  = 30
```

### 5. Deploy Infrastructure

Deploy the AWS infrastructure using Terraform:

```bash
cd terraform
terraform init
terraform plan  # Review the changes
terraform apply # Deploy the infrastructure
```

### 6. Build and Push Docker Image

Build the Docker image and push it to ECR:

```bash
# Get the ECR repository URI
ECR_URI=$(terraform output ecr_repository_url)
REGION=$(terraform output aws_region)

# Login to ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_URI

# Build the image
docker build -t bndes-data-pipeline:latest .

# Tag the image
docker tag bndes-data-pipeline:latest $ECR_URI:latest

# Push the image
docker push $ECR_URI:latest
```

### 7. Update Lambda Function

Update the Lambda function to use the new Docker image:

```bash
# Navigate to terraform directory
cd terraform

# Update the Lambda function
terraform apply -var="docker_image_tag=latest"
```

### 8. Verify Deployment

Check that the deployment was successful:

```bash
# View Terraform outputs
terraform output

# Expected outputs:
# - ecr_repository_url
# - lambda_function_name
# - lambda_function_arn
# - s3_bucket_name
# - log_group_name
# - dashboard_url
```

### 9. Test the Pipeline

Manually trigger the Lambda function to test the data pipeline:

```bash
# Get the Lambda function name
FUNCTION_NAME=$(terraform output lambda_function_name)

# Invoke the Lambda function
aws lambda invoke \
  --function-name $FUNCTION_NAME \
  --payload '{}' \
  --cli-binary-format raw-in-base64-out \
  response.json

# View the response
cat response.json

# Check logs
LOG_GROUP=$(terraform output log_group_name)
aws logs tail $LOG_GROUP --follow
```

## Configuration

### Terraform Variables

Key configuration variables in `terraform/main.tf`:

| Variable | Type | Default | Description |
|-----------|------|---------|-------------|
| `aws_region` | string | `us-east-1` | AWS region for deployment |
| `project_name` | string | `bndes-data-pipeline` | Prefix for all AWS resources |
| `lambda_timeout` | number | `900` | Lambda function timeout in seconds (max 900) |
| `lambda_memory_size` | number | `1024` | Lambda function memory in MB (128-10288) |
| `alarm_email` | string | `""` | Email address for SNS notifications |
| `log_retention_days` | number | `30` | CloudWatch logs retention period in days |

### Environment Variables

The Lambda function uses these environment variables:

| Variable | Description | Required |
|-----------|-------------|----------|
| `S3_BUCKET_NAME` | S3 bucket name for data storage | Yes |
| `LOCAL_OUTPUT_DIR` | Local directory for data processing | Yes |
| `BNDES_API_URL` | BNDES API endpoint | Yes |

## Monitoring

### CloudWatch Dashboard

Access the monitoring dashboard:

```bash
# Get the dashboard URL
terraform output dashboard_url
```

Or navigate manually in AWS Console:
1. Open CloudWatch Console
2. Go to Dashboards
3. Select `bndes-data-pipeline-dashboard`

The dashboard displays:
- Lambda invocation metrics (invocations, errors, duration, throttles)
- S3 storage metrics
- CloudWatch log insights
- Recent alarm status

### View Logs

Monitor Lambda execution logs in real-time:

```bash
# Get the log group name
LOG_GROUP=$(terraform output log_group_name)

# Tail the logs
aws logs tail $LOG_GROUP --follow
```

### Check Alarms

List all alarms associated with the project:

```bash
aws cloudwatch describe-alarms --alarm-name-prefix bndes-data-pipeline
```

### Custom Metrics

The system tracks these custom metrics:
- **Errors**: Lambda execution errors
- **Duration**: Lambda execution duration
- **Throttles**: Lambda throttling events
- **Invocations**: Total Lambda invocations
- **Successes**: Successful Lambda executions

## CI/CD Pipeline

The project includes a complete CI/CD pipeline using GitHub Actions, split into modular workflows:

### 1. Lint Check Workflow (`01-lint-check.yml`)
- **Trigger**: Push and pull requests
- **Purpose**: Ensures code quality and consistency
- **Tools**: 
  - Black (code formatting)
  - Flake8 (linting)
  - MyPy (type checking)

### 2. Unit Tests Workflow (`02-unit-tests.yml`)
- **Trigger**: Push and pull requests
- **Purpose**: Validates code functionality
- **Tools**: Pytest with coverage reporting
- **Output**: Codecov integration

### 3. Security Scan Workflow (`03-security-scan.yml`)
- **Trigger**: Push and pull requests
- **Purpose**: Identifies security vulnerabilities
- **Tool**: Trivy vulnerability scanner
- **Scope**: Docker images, dependencies

### 4. Docker Build Workflow (`04-docker-build-test.yml`)
- **Trigger**: Push and pull requests
- **Purpose**: Validates Docker image build
- **Tests**: Container health checks

### 5. Terraform Plan Workflow (`05-terraform-plan.yml`)
- **Trigger**: Pull requests targeting main/develop
- **Purpose**: Generates infrastructure plan for review
- **Backend**: Uses local backend (no S3 access needed)
- **Output**: PR comment with plan details

### 6. Deploy Workflow (`06-deploy.yml`)
- **Trigger**: Push to main branch
- **Purpose**: Deploys infrastructure changes to production
- **Backend**: Uses S3 backend with state locking
- **Process**: 
  1. Builds and pushes Docker image to ECR
  2. Initializes Terraform with S3 backend
  3. Applies Terraform changes

### Required GitHub Secrets

Configure these secrets in your GitHub repository settings:

1. **AWS_ACCESS_KEY_ID**: AWS access key with appropriate permissions
2. **AWS_SECRET_ACCESS_KEY**: AWS secret access key
3. **TF_STATE_BUCKET**: S3 bucket name for Terraform state (optional)

### GitHub Actions Permissions

The workflows require the following GitHub repository permissions:
- `contents: read` (for checkout)
- `pull-requests: write` (for PR comments)
- `issues: write` (for PR comments)

## Local Development

### Running Tests

Run the unit tests locally:

```bash
# Set PYTHONPATH to include src directory
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_fetch_data.py -v
```

### Building Docker Image

Build the Docker image locally for testing:

```bash
# Build the image
docker build -t bndes-data-pipeline:latest .

# Run the container
docker run -p 9010:8080 \
  -e S3_BUCKET_NAME="test-bucket" \
  -e LOCAL_OUTPUT_DIR="/tmp/local_data" \
  bndes-data-pipeline:latest
```

### Running Locally (Simulation)

Simulate the Lambda execution locally:

```bash
# Set environment variables
export S3_BUCKET_NAME="test-bucket"
export LOCAL_OUTPUT_DIR="./data"

# Run the main function
python src/app.py
```

### Using Jupyter Notebooks

Open the analysis notebook for data exploration:

```bash
# Install Jupyter
pip install jupyter notebook

# Start Jupyter
jupyter notebook

# Open notebooks/bndes_analysis.ipynb
```

### Terraform Local Development

Test Terraform changes locally without affecting production:

```bash
cd terraform

# Initialize with local backend (no S3)
terraform init -backend=false

# Validate configuration
terraform validate

# Generate plan
terraform plan

# Format code
terraform fmt -recursive
```

## Cost Estimate

Monthly costs (us-east-1) based on typical usage:

| Service | Estimated Cost | Notes |
|---------|----------------|-------|
| Lambda | ~$0.20 | 1 invocation/day, 900s duration, 1024MB |
| ECR | ~$0.10 | Storage for Docker images |
| S3 | ~$0.05 | 1GB/month for Parquet files |
| CloudWatch Logs | ~$0.10 | 1GB/month log ingestion |
| SQS DLQ | ~$0.00 | Pay per use (minimal) |
| SNS | ~$0.00 | 1000 free emails/month |
| KMS | ~$0.03 | KMS key usage |
| CloudWatch Metrics | ~$0.00 | Custom metrics under free tier |
| **Total** | **~$0.48/month** |  |

**Note**: Costs may vary based on actual usage, data volume, and AWS pricing changes.

## Security Features

The project implements multiple security best practices:

### Data Security
- **KMS Encryption**: All S3 data encrypted at rest using AWS KMS
- **Encryption in Transit**: All data transfers use HTTPS/TLS
- **No Hardcoded Credentials**: No secrets in code or configuration files

### IAM Security
- **Least Privilege**: Lambda execution role has minimum required permissions
- **Resource-Based Policies**: S3 bucket policies restrict access to specific roles
- **Role Separation**: Different roles for different functions (if applicable)

### Infrastructure Security
- **S3 Block Public Access**: Bucket blocks all public access
- **ECR Image Scanning**: Automatic vulnerability scanning on image push
- **VPC Isolation**: Lambda can be configured in VPC (future enhancement)

### Terraform State Security
- **State Encryption**: Terraform state encrypted in S3
- **State Versioning**: S3 versioning enabled for state recovery
- **State Locking**: DynamoDB table prevents concurrent modifications

### Operational Security
- **Audit Logging**: CloudWatch logs all Lambda executions
- **Error Alerts**: SNS notifications for security-relevant errors
- **Secrets Management**: Secrets stored in GitHub Secrets and AWS Secrets Manager

## Troubleshooting

### Lambda Timeout

**Symptoms**: Lambda function times out before completion.

**Solutions**:
1. Increase `lambda_timeout` in Terraform variables (max 900s)
2. Increase `lambda_memory_size` (more CPU power)
3. Optimize data processing code
4. Check BNDES API response time
5. Add pagination for large datasets

```bash
cd terraform
terraform apply -var="lambda_timeout=900" -var="lambda_memory_size=2048"
```

### S3 Permission Errors

**Symptoms**: Lambda fails to upload files to S3.

**Solutions**:
1. Verify IAM policies include S3 permissions
2. Check Lambda execution role has `s3:PutObject` permission
3. Ensure S3 bucket policy allows the Lambda role
4. Verify KMS key permissions if using SSE-KMS

```bash
# Check Lambda role
aws iam get-role-policy --role-name <lambda-role-name> --policy-name <policy-name>

# Check S3 bucket policy
aws s3api get-bucket-policy --bucket <bucket-name>
```

### Out of Memory Errors

**Symptoms**: Lambda fails with "Memory limit exceeded" error.

**Solutions**:
1. Increase `lambda_memory_size` in Terraform
2. Optimize memory usage in code
3. Process data in batches instead of loading all at once

```bash
cd terraform
terraform apply -var="lambda_memory_size=2048"
```

### Terraform State Lock

**Symptoms**: `terraform apply` fails with state lock error.

**Solution**: Unlock the state (only if safe to do so):

```bash
cd terraform
terraform force-unlock <LOCK_ID>

# To get the LOCK_ID:
terraform plan  # The error message will show the Lock ID
```

### BNDES API Errors

**Symptoms**: Lambda fails to fetch data from BNDES API.

**Solutions**:
1. Check API endpoint URL in environment variables
2. Verify BNDES API is accessible
3. Check for API rate limits or changes
4. Review API response in CloudWatch logs

### DLQ Messages Accumulating

**Symptoms**: Messages accumulating in SQS DLQ.

**Solutions**:
1. Check CloudWatch logs for Lambda errors
2. Investigate failed Lambda invocations
3. Manually reprocess DLQ messages after fixing issues
4. Adjust Lambda timeout/memory if needed

```bash
# View DLQ messages
aws sqs receive-message --queue-url <dlq-url>

# Reprocess message (after fixing issues)
# Copy message body and invoke Lambda manually
```

## Documentation

### External Resources

- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Documentation](https://docs.docker.com/)

### Internal Documentation

- `terraform/PIPELINE_SETUP.md`: Terraform pipeline configuration details
- `docs/medium-article-terraform-pipeline.md`: Article about Terraform backend strategy

## Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the Repository**
   ```bash
   git clone https://github.com/your-username/bndes-data-pipeline.git
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make Changes**
   - Write clean, readable code
   - Add tests for new functionality
   - Update documentation as needed

4. **Run Tests Locally**
   ```bash
   pytest tests/ -v
   ```

5. **Commit Changes**
   ```bash
   git commit -m 'Add amazing feature: description'
   ```

6. **Push to Branch**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Open a Pull Request**
   - Describe your changes clearly
   - Reference related issues
   - Ensure all CI checks pass

### Code Style

- Follow PEP 8 guidelines for Python code
- Use Black for code formatting
- Write descriptive variable and function names
- Add docstrings for complex functions
- Keep functions focused and small

### Testing

- Write unit tests for new functionality
- Aim for >80% code coverage
- Test both success and error cases
- Mock external dependencies in tests

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For issues, questions, or contributions:

1. **Open an Issue**: Report bugs or request features on GitHub Issues
2. **Check CloudWatch Logs**: Review Lambda execution logs for errors
3. **Review Terraform State**: Use `terraform show` to inspect current state
4. **Consult Documentation**: Check this README and other documentation files

### Useful Commands

```bash
# View Terraform state
terraform show

# View specific resource
terraform show aws_lambda_function.main

# Check Terraform version
terraform version

# Validate Terraform configuration
terraform validate

# Format Terraform code
terraform fmt -recursive

# Get CloudWatch logs
aws logs tail /aws/lambda/bndes-data-pipeline --follow

# Describe Lambda function
aws lambda get-function --function-name bndes-data-pipeline

# List S3 objects
aws s3 ls s3://bndes-data-pipeline-data --recursive
```

## Acknowledgments

- BNDES (Brazilian Development Bank) for providing the Open Data API
- AWS for the serverless platform and tools
- Terraform community for infrastructure as code best practices

---

**Built with AWS Serverless Technologies**

For more information, visit the [project repository](https://github.com/your-username/bndes-data-pipeline).