# Cost Analysis: Product Launch Agent

## Summary

The Product Launch Agent uses Amazon Bedrock AgentCore services with consumption-based pricing. Estimated monthly cost for typical usage: **$7-630** depending on activity levels.

### Key Cost Drivers
- **Runtime**: Agent execution and tool orchestration
- **Gateway**: API calls to tools and MCP operations
- **Memory**: Short-term conversation and long-term insights
- **Cognito**: User authentication (AWS Free Tier eligible)
- **Supporting Services**: Lambda, DynamoDB, S3, CloudWatch

## Detailed Cost Breakdown

### 1. AgentCore Runtime
**Pricing**: $0.0895 per vCPU-hour | $0.00945 per GB-hour

**Usage Pattern**: Product launch agent with market research, competitor analysis, and tool orchestration
- Average session: 45 seconds
- I/O wait: 60% (waiting for LLM, APIs, database)
- Active CPU: 1 vCPU during processing
- Memory: Peak 2GB

**Monthly Estimate** (1,000 sessions):
- CPU cost: 18s active × 1 vCPU × ($0.0895/3600) × 1,000 = $0.45
- Memory cost: 45s × 2GB × ($0.00945/3600) × 1,000 = $0.24
- **Total: $0.69/month**

**Scaling**:
- 10K sessions/month: $6.90
- 100K sessions/month: $69.00

### 2. AgentCore Gateway
**Pricing**: $0.005 per 1K API invocations | $0.025 per 1K search queries | $0.02 per 100 tools/month

**Usage Pattern**: 
- Tools indexed: 10 (market research, product details, competitor analysis, poster creation, etc.)
- Average invocations per session: 5 (ListTools, InvokeTool calls)
- Search queries: 2 per session

**Monthly Estimate** (1,000 sessions):
- Tool indexing: 10 tools × $0.02/100 = $0.002
- API invocations: 5,000 × $0.005/1,000 = $0.025
- Search queries: 2,000 × $0.025/1,000 = $0.05
- **Total: $0.08/month**

**Scaling**:
- 10K sessions/month: $0.80
- 100K sessions/month: $8.00

### 3. AgentCore Memory
**Pricing**: $0.25 per 1K events | $0.75 per 1K long-term records | $0.50 per 1K retrievals

**Usage Pattern**:
- Short-term events: 10 per session (conversation turns)
- Long-term records: 2 per session (insights, preferences)
- Memory retrievals: 3 per session

**Monthly Estimate** (1,000 sessions):
- Short-term: 10,000 events × $0.25/1,000 = $2.50
- Long-term storage: 2,000 records × $0.75/1,000 = $1.50
- Retrievals: 3,000 × $0.50/1,000 = $1.50
- **Total: $5.50/month**

**Scaling**:
- 10K sessions/month: $55.00
- 100K sessions/month: $550.00

### 4. AgentCore Identity
**Pricing**: $0.010 per 1K token requests

**Usage Pattern**: OAuth tokens for third-party tool access (Tavily search, external APIs)
- Token requests: 3 per session

**Monthly Estimate** (1,000 sessions):
- 3,000 requests × $0.010/1,000 = $0.03
- **Total: $0.03/month**

**Note**: No additional charge when using through Runtime or Gateway

### 5. Amazon Cognito
**Pricing**: Free Tier: 50,000 MAUs | $0.0055 per MAU beyond Free Tier

**Usage Pattern**: User authentication for web interface
- Monthly Active Users (MAU): 10-50

**Monthly Estimate**:
- **Total: $0.00** (within Free Tier)

### 6. Supporting AWS Services

#### AWS Lambda (PostSignup function)
**Pricing**: Free Tier: 1M requests/month, 400K GB-seconds
- Invocations: ~100/month (new user signups)
- **Total: $0.00** (within Free Tier)

#### Amazon DynamoDB (Memory storage)
**Pricing**: Free Tier: 25GB storage, 25 WCU, 25 RCU
- Storage: <1GB
- Read/Write: Minimal
- **Total: $0.00** (within Free Tier)

#### Amazon S3 (Code artifacts, generated materials)
**Pricing**: $0.023 per GB/month
- Storage: ~500MB
- **Total: $0.01/month**

#### Amazon CloudWatch (Logs, Metrics)
**Pricing**: $0.50 per GB ingested
- Log data: ~1GB/month
- **Total: $0.50/month**

#### Amazon ECR (Container images)
**Pricing**: $0.10 per GB/month
- Storage: 2GB (Runtime container)
- **Total: $0.20/month**

## Total Monthly Cost Estimates

### Light Usage (1,000 sessions/month)
| Service | Cost |
|---------|------|
| AgentCore Runtime | $0.69 |
| AgentCore Gateway | $0.08 |
| AgentCore Memory | $5.50 |
| AgentCore Identity | $0.03 |
| Cognito | $0.00 |
| Lambda | $0.00 |
| DynamoDB | $0.00 |
| S3 | $0.01 |
| CloudWatch | $0.50 |
| ECR | $0.20 |
| **Total** | **$7.01** |

### Medium Usage (10,000 sessions/month)
| Service | Cost |
|---------|------|
| AgentCore Runtime | $6.90 |
| AgentCore Gateway | $0.80 |
| AgentCore Memory | $55.00 |
| AgentCore Identity | $0.30 |
| Cognito | $0.00 |
| Supporting Services | $0.71 |
| **Total** | **$63.71** |

### High Usage (100,000 sessions/month)
| Service | Cost |
|---------|------|
| AgentCore Runtime | $69.00 |
| AgentCore Gateway | $8.00 |
| AgentCore Memory | $550.00 |
| AgentCore Identity | $3.00 |
| Cognito | $0.28 |
| Supporting Services | $5.00 |
| **Total** | **$635.28** |

## Cost Optimization Tips

1. **Memory Management**: Use built-in with override strategies ($0.25 vs $0.75 per 1K records) for long-term memory
2. **Session Duration**: Optimize agent logic to reduce session time and I/O wait
3. **Tool Indexing**: Only index tools actively used by the agent
4. **CloudWatch Logs**: Set retention policies (7-30 days) to reduce storage costs
5. **ECR Images**: Use image lifecycle policies to remove old container versions
6. **Free Tier**: New AWS customers receive up to $200 in AgentCore credits

## Additional Costs (Not Included)

- **Amazon Bedrock Model Inference**: Varies by model (Claude, Llama, etc.)
  - Example: Claude 3.5 Sonnet ~$3 per 1M input tokens, $15 per 1M output tokens
  - Estimated: $10-50/month for typical usage
- **Third-party APIs**: Tavily search, external data providers
- **Data Transfer**: Outbound data transfer beyond 100GB/month
- **Observability**: If using AgentCore Observability (CloudWatch pricing applies)

## Pricing Calculator

Use the [AWS Pricing Calculator](https://calculator.aws) for customized estimates based on your specific usage patterns.

## Free Tier Benefits

New AWS customers receive:
- Up to **$200 in AgentCore credits**
- 12 months of AWS Free Tier for supporting services
- No upfront commitments or minimum fees

Start building at: [AWS Free Tier](https://aws.amazon.com/free)
