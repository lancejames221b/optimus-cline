#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Error handling
set -e
trap 'echo -e "${RED}Error occurred. Exiting...${NC}" >&2' ERR

echo -e "${BLUE}Initializing templates...${NC}"

# Create task template
echo -e "${GREEN}Creating task template...${NC}"
cat > ~/.ewitness/templates/task.md << 'EOF'
# Task: {TITLE}
Date: $(date +%Y-%m-%d_%H-%M-%S)

## Context
- Previous Tasks: [Link to relevant cline tasks]
- Related Docs: [Confluence/Git doc links]
- Tickets: [JIRA ticket links]

## Environment
- Staging: auth-server-staging (157.245.210.244)
- Collectors: collectors.staging.vpc.local (10.108.0.35)
- Database: mysql.staging.vpc.local (10.108.0.33)
- Elasticsearch: elastic.staging.k8s.vpc.local

## Access Requirements
- SSH Config: ~/.ewitness/access/ssh/config
- DO Resources: [Relevant droplets]
- API Keys: ~/.ewitness/access/keys/current/keys.txt

## Pre-Execution Checklist
- [ ] Verified staging environment
- [ ] Checked service health
- [ ] Backed up relevant data
- [ ] Reviewed previous related tasks

## Steps
1. [Step details]
   ```bash
   # Command to execute
   ```

## Verification
1. [Verification steps]
   ```bash
   # Verification commands
   ```

## Rollback
1. [Rollback steps if needed]
   ```bash
   # Rollback commands
   ```

## Results
- [ ] Task completed successfully
- [ ] Documentation updated
- [ ] Changes verified
- [ ] Rollback tested if applicable

## Notes
- Historical context: [Reference to previous similar tasks]
- Known issues: [Document any issues encountered]
- Future improvements: [Suggestions for future work]
EOF

# Create SSH config template
echo -e "${GREEN}Creating SSH config template...${NC}"
cat > ~/.ewitness/access/ssh/config << 'EOF'
# Staging Environment Access
Host auth-server-staging
    HostName 157.245.210.244
    User root
    IdentityFile ~/.ewitness/access/ssh/keys/staging_key
    StrictHostKeyChecking no

# Internal Services (via Jump Host)
Host *.staging.vpc.local
    User root
    ProxyJump auth-server-staging
    StrictHostKeyChecking no

Host collectors.staging.vpc.local
    HostName 10.108.0.35

Host mysql.staging.vpc.local
    HostName 10.108.0.33

Host elastic.staging.k8s.vpc.local
    HostName 10.108.0.36

# Keep connection alive
Host *
    ServerAliveInterval 60
    ServerAliveCountMax 10
EOF

chmod 600 ~/.ewitness/access/ssh/config

echo -e "${GREEN}Templates initialized successfully${NC}"
echo -e "${BLUE}Task template: ~/.ewitness/templates/task.md${NC}"
echo -e "${BLUE}SSH config: ~/.ewitness/access/ssh/config${NC}"
