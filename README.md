# Flask App CI/CD Pipeline with GitHub Actions

## Objective

Implement a complete CI/CD workflow using GitHub Actions for a Python Flask application with automated deployment to staging and production environments.

**GitHub Repository:** [https://github.com/jatinggg/flask_Practice.git](https://github.com/jatinggg/flask_Practice.git)

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [GitHub Actions Workflow](#github-actions-workflow)
- [EC2 Configuration](#ec2-configuration)
- [MongoDB Setup](#mongodb-setup)
- [Deployment Process](#deployment-process)
- [Verification](#verification)

---

## Prerequisites

- GitHub account
- AWS account with EC2 access
- MongoDB Atlas account
- Local development environment with Git installed
- Basic knowledge of Python, Flask, and CI/CD concepts

---

## Setup Instructions

### Step 1: Fork the Repository

Fork the provided repository to your GitHub account:
```
https://github.com/jatinggg/flask_Practice.git
```

### Step 2: Create Staging Branch

In your forked repository, create a new branch called `staging`:
```bash
git checkout -b staging
git push origin staging
```

### Step 3: Clone Repository Locally

```bash
git clone https://github.com/<your-username>/flask_Practice.git
cd flask_Practice
```

### Step 4: Create GitHub Actions Workflow

Create the workflow directory structure and add the workflow file:

```bash
mkdir -p .github/workflows
```

Create `main.yml` file in `.github/workflows/` with the CI/CD pipeline configuration for both `main` and `staging` branches.

**Note:** Ensure the workflow file is committed to both branches.

---

## GitHub Actions Workflow

The workflow automates:
- Code checkout
- Dependency installation
- Running tests
- Building artifacts
- Deploying to EC2 instances
- Service restart

---

## EC2 Configuration

### Step 5: Launch EC2 Instances

Launch **2 EC2 instances** (Ubuntu recommended):
- **Staging Server**
- **Production Server**

**Security Group Configuration:**
- Allow inbound traffic on **port 8000** from anywhere (IPv4)
- Allow SSH access (port 22) from your IP

### Step 6: Configure Systemd Service

SSH into each EC2 instance and create the Flask app service:

```bash
sudo nano /etc/systemd/system/flaskapp.service
```

Add the following configuration:

```ini
[Unit]
Description=Gunicorn instance to serve Flask App
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/app
Environment="PATH=/home/ubuntu/app/venv/bin:/usr/local/bin:/usr/bin"
EnvironmentFile=/home/ubuntu/app/.env

# Point to the venv gunicorn and bind to 0.0.0.0:5000
ExecStart=/home/ubuntu/app/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable flaskapp.service
sudo systemctl start flaskapp.service
```

**Repeat this configuration on both staging and production servers.**

---

## MongoDB Setup

### Step 8: Create MongoDB Cluster

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster
3. Configure network access to allow connections from **all IP addresses** (0.0.0.0/0)
4. Create a database user with appropriate permissions
5. Get your connection string

---

## GitHub Secrets Configuration

### Step 9: Add Repository Secrets

Navigate to: **Settings > Secrets and variables > Actions > New repository secret**

Add the following secrets:

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `EC2_HOST_PROD` | Production EC2 IP address | `54.123.45.67` |
| `EC2_HOST_STAGING` | Staging EC2 IP address | `54.123.45.68` |
| `EC2_SSH_KEY` | Private SSH key for EC2 access | `-----BEGIN RSA PRIVATE KEY-----...` |
| `EC2_USERNAME` | EC2 username | `ubuntu` |
| `MONGO_URI` | MongoDB connection string | `mongodb+srv://user:pass@cluster.mongodb.net/` |
| `SECRET_KEY` | Flask secret key | `123456` (use a secure random string) |

---

## Deployment Process

### Step 10-12: Deploy to Staging

1. Switch to the staging branch:
```bash
git switch staging
```

2. Make your code changes in Visual Studio Code or your preferred editor

3. Configure Personal Access Token (PAT):
   - Go to GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)
   - Generate new token with `repo` and `workflow` permissions
   - Configure in local repository:
   ```bash
   git remote set-url origin https://<your-PAT>@github.com/<your-username>/flask_Practice.git
   ```

4. Commit and push changes:
```bash
git checkout staging
git add .
git commit -m "Staging Initial build"
git push origin staging
```

### Step 13: Verify Staging Deployment

1. Go to your GitHub repository
2. Navigate to **Actions** tab
3. Verify the workflow run completed successfully

### Step 14: Verify Staging Artifacts

SSH into the staging server:
```bash
ssh ubuntu@<staging-ec2-ip>
```

Check for the `app.zip` artifact in the root directory:
```bash
ls -la /home/ubuntu/
```

### Step 15: Test Staging Application

Access the application in your browser:
```
http://<staging-ec2-ip>:8000
```

Verify data in MongoDB Compass using your connection string.

---

## Production Deployment

### Step 16: Deploy to Production

Once staging tests pass, merge to production:

```bash
git fetch origin
git pull origin main
git checkout main
git commit -m "Deploy to prod"
git merge origin/staging
git tag v1.0.1
git push origin v1.0.1
```

The tag push triggers the production deployment workflow.

### Step 17: Verify Production Deployment

Access the production application:
```
http://<production-ec2-ip>:8000
```

Verify the application is running correctly and data is being stored in MongoDB.

---

## Application Architecture

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────┐
│   GitHub    │────────>│  GitHub Actions  │────────>│  EC2 Server │
│ Repository  │         │   CI/CD Pipeline │         │  (Staging)  │
└─────────────┘         └──────────────────┘         └─────────────┘
                                 │                            │
                                 │                            │
                                 v                            v
                        ┌──────────────────┐         ┌─────────────┐
                        │    Production    │────────>│  MongoDB    │
                        │    EC2 Server    │         │   Atlas     │
                        └──────────────────┘         └─────────────┘
```

---

