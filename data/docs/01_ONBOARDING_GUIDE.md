# 🧭 Developer Onboarding Guide — Hotel Booking System (HBS)

> Version: 1.0  
> Last Updated: 2025-10-25  
> Maintainer: Engineering PMO  
> Audience: New Developers, QA Engineers, and DevOps Members  
> Tags: onboarding, development, setup, guideline

---

## 1. Introduction

Welcome to the **Hotel Booking System (HBS)** project.  
This guide will help you set up your development environment, understand project structure, and align with the coding standards and workflows we use across the team.

The onboarding process is designed to ensure that **every developer can contribute productively within the first week**.

# 🧭 Developer Onboarding Guide — Hotel Booking System (HBS)

> Version: 2.0  
> Last Updated: 2025-10-25  
> Maintainer: Engineering PMO  
> Audience: New Developers, QA Engineers, and DevOps Members  
> Tags: onboarding, development, setup, guideline

---

## 1. Introduction

Welcome to the **Hotel Booking System (HBS)** project! 🎉  

This guide will help you set up your development environment, understand project structure, and align with the coding standards and workflows we use across the team. Whether you're coming from a startup background or enterprise experience, we'll get you up to speed quickly.

The onboarding process is designed to ensure that **every developer can contribute productively within the first week**, with your first PR merged by Day 3.

### What You'll Learn:
- **Day 1**: Environment setup, repository access, and team introductions
- **Day 2**: Code structure, architecture patterns, and first code exploration
- **Day 3**: First feature implementation and PR submission
- **Day 4-5**: Code review, testing practices, and CI/CD workflows
- **Week 2+**: Advanced topics, deployment, and domain expertise

### Quick Navigation:
- [Environment Setup](#4-setting-up-your-environment)
- [Git Workflow](#5-git-workflow)
- [Running Locally](#7-running-locally)
- [Common Issues](#11-common-issues--solutions)
- [Your First Task](#14-your-first-week-roadmap)

---

## 2. Prerequisites

Before you begin, ensure that you have the following:

### 2.1 Hardware Requirements
| Component | Minimum | Recommended |
|------------|----------|-------------|
| CPU | Intel i5 or AMD Ryzen 5 | Intel i7+ |
| RAM | 8 GB | 16 GB |
| Storage | 50 GB free | SSD 512 GB |
| OS | Windows 11 / macOS 14 / Ubuntu 22.04 | Any OS with Docker support |

### 2.2 Software Requirements
| Tool | Version | Notes |
|------|----------|-------|
| .NET SDK | 8.0+ | Backend development |
| Node.js | 20+ | Frontend or integration testing |
| SQL Server | 2022 | Local DB instance |
| Docker Desktop | Latest | Optional for containerized environment |
| Git | 2.40+ | Git hooks required |
| Visual Studio / Rider | Latest | Preferred IDE |
| Azure CLI | 2.60+ | Deployment to Azure environment |
| Postman | Latest | API testing |

### 2.3 Accounts and Access

You'll need the following accounts (request from your manager on Day 1):

- **GitHub Enterprise Account** (project repo access) - Request: github-access@company.com
- **Azure DevOps Account** (CI/CD pipelines and boards) - Auto-provisioned via AD
- **Azure Subscription Access** (staging environment) - Request: devops@company.com with justification
- **Slack / Teams Access** (internal communication) - Join #hbs-dev, #hbs-alerts, #engineering-general
- **Confluence Access** (documentation repository) - Request: it-support@company.com
- **VPN Access** (required for staging/production access) - IT will send credentials
- **SonarQube Account** (code quality dashboard) - Use SSO with GitHub
- **Azure Application Insights** (monitoring access) - Same as Azure subscription
- **PagerDuty** (on-call rotation) - Added after first month

**Pro Tip:** Create a secure password manager vault (we recommend 1Password or LastPass) and store all credentials securely. Never commit credentials to Git!

### 2.4 Essential Reading (Before You Code)

| Document | Time | Purpose | When to Read |
|----------|------|---------|--------------|
| [02_BUSINESS_OVERVIEW.md](./02_BUSINESS_OVERVIEW.md) | 30 min | Understand domain and business rules | Day 1 |
| [03_SYSTEM_ARCHITECTURE.md](./03_SYSTEM_ARCHITECTURE.md) | 45 min | System design and patterns | Day 1-2 |
| [04_API_REFERENCE.md](./04_API_REFERENCE.md) | 20 min | Available endpoints and contracts | Day 2 |
| [09_SECURITY_COMPLIANCE.md](./09_SECURITY_COMPLIANCE.md) | 15 min | Security requirements | Day 2 |
| Team Charter (Confluence) | 10 min | Team norms and expectations | Day 1 |



---

## 3. System Overview

### 3.1 Key Modules

| Module | Description |
|---------|--------------|
| Search Service | Handles hotel and room searching with filters and availability. |
| Booking Service | Manages reservations, cancellations, and confirmation workflow. |
| Payment Gateway | Integrates multiple payment methods (credit card, e-wallet, bank). |
| Customer Service | Handles reviews, feedback, and loyalty points. |
| Admin Portal | Allows hotel managers to manage inventory, pricing, and promotions. |

### 3.2 Environments

| Environment | Purpose | URL | Notes |
|--------------|----------|-----|------|
| Development | Local environment for individual developers | `http://localhost:5000` | Local SQL & mock services |
| Staging | Internal testing & QA | `https://staging.hbs.azurewebsites.net` | Auto-deployed from `develop` branch |
| Production | Live environment | `https://hotelbooking.com` | Deployed from `main` branch after QA approval |

---

## 4. Setting Up Your Environment

### 4.1 Clone the Repository

```bash
git clone https://github.com/hbs-enterprise/hotel-booking-system.git
cd hotel-booking-system
```

### 4.2 Folder Structure

```
hotel-booking-system/
│
├─ src/
│  ├─ HBS.API/                  → API entry point
│  ├─ HBS.Application/          → CQRS, Services, DTOs
│  ├─ HBS.Domain/               → Entities, Aggregates, Domain Events
│  ├─ HBS.Infrastructure/       → EF Core, Repositories, External Services
│  └─ HBS.Tests/                → xUnit test projects
│
├─ docs/
│  ├─ 01_ONBOARDING_GUIDE.md
│  ├─ 02_BUSINESS_OVERVIEW.md
│  └─ ...
│
└─ docker-compose.yml
```

### 4.3 Environment Variables

Create a `.env` file under the project root:

```env
ASPNETCORE_ENVIRONMENT=Development
ConnectionStrings__Default=Server=localhost;Database=HBS;User Id=sa;Password=Pass@123;
Jwt__Key=YOUR_LOCAL_JWT_KEY
Azure__Storage__ConnectionString=UseDevelopmentStorage=true
```

---

## 5. Git Workflow

We use **GitHub Flow with branch naming conventions** and enforce pull requests via CI checks.

### 5.1 Branch Naming Rules

| Type | Format | Example |
|------|---------|----------|
| Feature | `feature/<ticket-id>-<short-description>` | `feature/HBS-102-add-booking-api` |
| Bugfix | `bugfix/<ticket-id>-<short-description>` | `bugfix/HBS-301-fix-null-payment` |
| Hotfix | `hotfix/<short-description>` | `hotfix/invalid-token-handling` |
| Release | `release/vX.Y.Z` | `release/v1.0.0` |

### 5.2 Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add booking cancellation endpoint
fix: correct total price calculation
refactor: simplify payment handler
docs: update onboarding guide
```

### 5.3 Pull Request Policy

- All PRs must be reviewed by at least **1 senior developer**.
- Must pass:
  - Unit Tests (xUnit)
  - Code Coverage ≥ 80%
  - SonarQube Code Quality check
- PR title format: `[HBS-xxx] Short Description`

---

## 6. Coding Standards

### 6.1 C# Conventions
- Use **PascalCase** for classes, methods, and properties.
- Use **camelCase** for private fields.
- Always add XML doc comments for public methods.
- Avoid magic strings — use constants or enums.
- Follow **Clean Architecture**: `Domain → Application → Infrastructure → API`.

### 6.2 Example Folder Pattern

```
/HBS.Application/
 ├─ Bookings/
 │   ├─ Commands/
 │   │   ├─ CreateBookingCommand.cs
 │   │   ├─ CancelBookingCommand.cs
 │   ├─ Queries/
 │   │   ├─ GetBookingDetailsQuery.cs
 │   │   ├─ GetAllBookingsQuery.cs
```

### 6.3 Coding Style Check

We use `.editorconfig` and `dotnet format` for enforcement.

```bash
dotnet format --verify-no-changes
```

If any formatting issues occur, fix them automatically:
```bash
dotnet format
```

---

## 7. Running Locally

### 7.1 First-Time Setup Walkthrough

**Step 1: Restore Dependencies**

```bash
cd hotel-booking-system
dotnet restore
npm install --prefix ./src/HBS.Web
```

**Step 2: Database Setup**

Option A - Local SQL Server:

```bash
# Update connection string in appsettings.Development.json
dotnet ef database update --project src/HBS.Infrastructure --startup-project src/HBS.API

# Seed test data
dotnet run --project src/HBS.API -- --seed
```

Option B - Docker SQL Server:

```bash
docker run -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=YourStrong@Passw0rd" -p 1433:1433 --name hbs-sql -d mcr.microsoft.com/mssql/server:2022-latest
```

**Step 3: Configure Secrets**

```bash
# Initialize user secrets
dotnet user-secrets init --project src/HBS.API

# Add sensitive values
dotnet user-secrets set "Jwt:Key" "your-256-bit-secret-key-here" --project src/HBS.API
dotnet user-secrets set "Stripe:SecretKey" "sk_test_xxx" --project src/HBS.API
```

**Step 4: Start the Application**

```bash
# Terminal 1 - API
dotnet run --project src/HBS.API

# Terminal 2 - Frontend (if applicable)
cd src/HBS.Web
npm run dev
```

API should be running at `https://localhost:5001`  
Swagger UI: `https://localhost:5001/swagger`

### 7.2 Using Visual Studio / Rider

1. Open `HotelBookingSystem.sln`
2. Set `HBS.API` as startup project
3. Hit F5 to run with debugger
4. Breakpoints will work across all projects

**Pro Tips:**
- Use `launchSettings.json` profiles for different configurations
- Enable "Hot Reload" for rapid development
- Install "REST Client" extension for VS Code to test APIs inline

### 7.3 Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f hbs-api

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

This will spin up:

- **HBS API** (port 5000)
- **SQL Server** (port 1433)
- **Redis Cache** (port 6379)
- **Seq Log Server** (port 5341) - for structured logging
- **LocalStack** (port 4566) - AWS mock for testing S3/SQS

Access points:

- API: `http://localhost:5000`
- Swagger: `http://localhost:5000/swagger`
- Seq Dashboard: `http://localhost:5341`

### 7.4 Troubleshooting Startup Issues

| Issue | Solution |
|-------|----------|
| Port 5000 already in use | Kill process: `netstat -ano \| findstr :5000` then `taskkill /PID <pid> /F` |
| Database connection timeout | Verify SQL Server is running and connection string is correct |
| Swagger not loading | Check `ASPNETCORE_ENVIRONMENT=Development` is set |
| Hot reload not working | Restart with `dotnet watch run --project src/HBS.API` |
| EF migration fails | Delete `Migrations` folder and regenerate with `dotnet ef migrations add Initial` |

### 7.5 Testing Your Setup

Run the health check endpoint:

```bash
curl https://localhost:5001/health
```

Expected response:

```json
{
  "status": "Healthy",
  "checks": {
    "database": "Healthy",
    "redis": "Healthy",
    "storage": "Healthy"
  },
  "timestamp": "2025-10-25T10:30:00Z"
}
```

---

## 8. Quality Assurance

### 8.1 Unit Tests

- Framework: `xUnit`
- Mocking: `Moq` or `NSubstitute`
- Coverage target: **≥ 80%**
- Run tests locally:

```bash
dotnet test --collect:"XPlat Code Coverage"

# Generate HTML report
dotnet tool install --global dotnet-reportgenerator-globaltool
reportgenerator -reports:"**/coverage.cobertura.xml" -targetdir:"coveragereport" -reporttypes:Html
```

**Example Test Structure:**

```csharp
public class BookingServiceTests
{
    private readonly Mock<IBookingRepository> _mockRepo;
    private readonly BookingService _sut; // System Under Test

    public BookingServiceTests()
    {
        _mockRepo = new Mock<IBookingRepository>();
        _sut = new BookingService(_mockRepo.Object);
    }

    [Fact]
    public async Task CreateBooking_ValidInput_ReturnsSuccess()
    {
        // Arrange
        var command = new CreateBookingCommand { RoomId = 1, GuestId = 100 };
        _mockRepo.Setup(r => r.IsRoomAvailable(It.IsAny<int>(), It.IsAny<DateTime>()))
                 .ReturnsAsync(true);

        // Act
        var result = await _sut.CreateBookingAsync(command);

        // Assert
        Assert.True(result.IsSuccess);
        _mockRepo.Verify(r => r.AddAsync(It.IsAny<Booking>()), Times.Once);
    }
}
```

### 8.2 Integration Tests

Located under `/HBS.Tests/Integration/`.  
Uses `WebApplicationFactory` for in-memory API testing.

**Run integration tests:**

```bash
dotnet test --filter "Category=Integration"
```

**Example Integration Test:**

```csharp
public class BookingApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public BookingApiTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task POST_CreateBooking_Returns201()
    {
        // Arrange
        var booking = new { roomId = 1, checkIn = "2025-11-01", checkOut = "2025-11-03" };
        var content = new StringContent(JsonSerializer.Serialize(booking), Encoding.UTF8, "application/json");

        // Act
        var response = await _client.PostAsync("/api/bookings", content);

        // Assert
        Assert.Equal(HttpStatusCode.Created, response.StatusCode);
    }
}
```

### 8.3 End-to-End Tests

- Framework: `Playwright` (for UI testing)
- Located under `/HBS.Tests/E2E/`
- Run only on staging before production deployment

```bash
npm run test:e2e
```

### 8.4 Code Review Checklist

Before submitting your PR, verify:

✅ **Naming follows conventions** (PascalCase, camelCase)  
✅ **No magic values** (use constants or configuration)  
✅ **Proper null handling** (null checks, null-coalescing)  
✅ **Unit test included** (minimum 80% coverage for new code)  
✅ **No direct SQL or external calls in Application layer** (use repositories)  
✅ **Async/await used properly** (no blocking calls)  
✅ **Logging added for important operations** (using ILogger)  
✅ **Error handling implemented** (try-catch with proper exceptions)  
✅ **API documentation updated** (XML comments, Swagger annotations)  
✅ **Database migrations included** (if schema changes)  

### 8.5 Performance Testing

For performance-critical features, add benchmarks:

```bash
dotnet run --project HBS.Benchmarks -c Release
```

Use `BenchmarkDotNet` for micro-benchmarks.

---

## 9. Deployment Process

### 9.1 CI/CD Overview
- **CI Pipeline:** Runs on each PR push.
  - Restore → Build → Test → Lint → Package
- **CD Pipeline:** Deploys automatically to Staging when merged into `develop`.

### 9.2 Deployment Commands (Manual)
```bash
az login
az webapp deploy --resource-group HBS-RG --name hbs-api --src-path ./publish
```

---

## 10. Communication & Support

| Purpose | Channel | Owner |
|----------|----------|--------|
| Daily Standup | Slack #hbs-dev | Scrum Master |
| Tech Discussion | Slack #hbs-engineering | Lead Engineer |
| Incident Report | Teams / PagerDuty | DevOps |
| Knowledge Docs | Confluence | PMO |
| Access Issues | Email IT Support | IT Department |

---

## 11. Common Issues & Solutions

### 11.1 Environment Setup Issues

| Problem | Symptoms | Solution | Prevention |
|----------|----------|----------|------------|
| **SQL Server connection failed** | `A network-related or instance-specific error` | 1. Verify SQL Server service is running<br>2. Check firewall rules<br>3. Test connection with SSMS<br>4. Verify connection string format | Use Docker SQL for consistency |
| **Port conflict (5000/5001)** | `Address already in use` | PowerShell: `Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess \| Stop-Process`<br>Or change port in `launchSettings.json` | Use `dotnet watch` on unique ports |
| **EF Migration fails** | `Unable to create migration` | 1. Check connection to DB<br>2. Ensure `HBS.Infrastructure` is set correctly<br>3. Delete `Migrations/` and regenerate | Always test migrations on fresh DB first |
| **Docker won't start** | `Cannot connect to Docker daemon` | 1. Restart Docker Desktop<br>2. Check WSL2 is enabled (Windows)<br>3. Verify virtualization in BIOS | Keep Docker Desktop updated |
| **.NET SDK version mismatch** | `The current .NET SDK does not support` | 1. Run `dotnet --list-sdks`<br>2. Install .NET 8.0 SDK<br>3. Update `global.json` if needed | Use `global.json` to lock SDK version |

### 11.2 Build & Compilation Issues

| Problem | Cause | Solution |
|----------|-------|----------|
| **Nullable reference warnings** | Missing null checks in C# 10+ | Add null-forgiving operator `!` or proper null checks |
| **Missing package reference** | NuGet restore incomplete | Run `dotnet restore` or delete `bin/obj` folders |
| **Version conflict** | Multiple versions of same package | Check with `dotnet list package --include-transitive` |
| **Circular dependency** | Project references form a cycle | Refactor to extract shared interfaces into separate project |

### 11.3 Runtime Errors

| Error | Likely Cause | Debug Steps |
|-------|--------------|-------------|
| **401 Unauthorized** | Missing or invalid JWT token | 1. Check token in request header<br>2. Verify `Jwt:Key` in user-secrets<br>3. Confirm token hasn't expired |
| **500 Internal Server Error** | Unhandled exception | 1. Check Application Insights logs<br>2. Look at console output<br>3. Add try-catch with logging |
| **404 Not Found** | Route mismatch | 1. Verify controller route attribute<br>2. Check HTTP verb (GET/POST/PUT)<br>3. Review Swagger UI for correct endpoint |
| **DbUpdateConcurrencyException** | Concurrent update conflict | Implement optimistic concurrency with `RowVersion` |
| **Payment Gateway timeout** | External service slow/down | 1. Check network connectivity<br>2. Implement retry logic<br>3. Use circuit breaker pattern |

### 11.4 Testing Issues

| Problem | Solution |
|----------|----------|
| **Tests fail in CI but pass locally** | Environment differences - check connection strings, secrets, and dependencies |
| **Flaky integration tests** | Use `WebApplicationFactory` with isolated database per test |
| **Mock not returning expected value** | Verify `.Setup()` matches actual method call signature exactly |
| **Code coverage below threshold** | Add tests for edge cases, error paths, and validation logic |

### 11.5 Git & CI/CD Issues

| Problem | Solution |
|----------|----------|
| **PR blocked by failing CI** | Check Azure Pipelines logs, fix failing tests or build errors |
| **Merge conflict in migration file** | Never merge migration files - regenerate after pulling latest |
| **Pre-commit hook fails** | Run `dotnet format` and `dotnet test` before committing |
| **Cannot push to protected branch** | Never push directly to `main` or `develop` - use PRs |

### 11.6 Performance Issues

| Symptom | Diagnosis | Fix |
|----------|-----------|-----|
| **Slow API response (>2s)** | N+1 query problem | Use `.Include()` for eager loading or projection |
| **High memory usage** | Memory leak or large collections | Use `IAsyncEnumerable` for streaming, dispose resources |
| **Database deadlock** | Lock contention | Review transaction isolation level, optimize queries |

### 11.7 Getting Help

When you're stuck:

1. **Check documentation first** (this guide, Confluence, README)
2. **Search Slack history** (`#hbs-dev` channel)
3. **Review similar issues in GitHub** (closed issues/PRs)
4. **Ask in Slack with context**:

```text
🔴 I'm facing an issue with [feature]
📌 What I'm trying to do: [goal]
❌ Current behavior: [error/symptom]
✅ Expected behavior: [what should happen]
🔍 What I've tried: [steps taken]
💻 Environment: [local/staging/docker]
```

5. **Pair with mentor** (schedule 30-min session)
6. **Escalate to senior engineer** (if blocking >4 hours)

**Pro Tip:** Before asking, spend 30 minutes researching. Document what you tried - this helps others help you faster!

---

## 12. Next Steps

Once onboarding setup is completed:

1. Read the **[Business Overview](./02_BUSINESS_OVERVIEW.md)**
2. Join the next **Sprint Planning** to get your first assigned task
3. Familiarize yourself with the **API Documentation** and Postman Collection
4. Review **Security & Compliance** policies

---

## 13. Your First Week Roadmap

### Day 1: Setup & Orientation

**Morning (9:00 AM - 12:00 PM)**

- ✅ Team introduction meeting with Engineering Manager
- ✅ Receive laptop, accounts, and access credentials
- ✅ Complete HR onboarding paperwork
- ✅ Set up development environment (Sections 2-4)
- ✅ Join Slack channels: #hbs-dev, #engineering-general, #random
- ✅ Read [02_BUSINESS_OVERVIEW.md](./02_BUSINESS_OVERVIEW.md)

**Afternoon (1:00 PM - 5:00 PM)**

- ✅ Clone repository and successfully run the app locally
- ✅ Explore codebase structure (spend 30-45 min browsing)
- ✅ Watch recorded "Architecture Deep Dive" session (Confluence)
- ✅ Complete security training module (mandatory)
- ✅ Schedule 1:1 with your assigned mentor

**Homework:**

- Read [03_SYSTEM_ARCHITECTURE.md](./03_SYSTEM_ARCHITECTURE.md)
- Explore Postman collection and test API endpoints locally

---

### Day 2: Code Exploration & Learning

**Morning**

- ✅ Daily standup attendance (introduce yourself!)
- ✅ Pair programming session with mentor (60 min)
- ✅ Deep dive into one module (e.g., Booking Service)
  - Read the code
  - Understand dependencies
  - Review existing tests
- ✅ Run all tests successfully (`dotnet test`)

**Afternoon**

- ✅ Pick your **First Task** (should be labeled "good-first-issue")
  - Example: "Add validation for guest email format"
  - Example: "Fix typo in error message"
  - Example: "Add unit test for existing method"
- ✅ Create feature branch following naming convention
- ✅ Review similar PRs for reference

**Homework:**

- Work on your first task (aim to complete 80%)

---

### Day 3: First Contribution

**Morning**

- ✅ Complete your first task
- ✅ Write unit tests (ensure ≥80% coverage for new code)
- ✅ Run `dotnet format` to fix formatting
- ✅ Commit with conventional commit message
- ✅ Push branch and create Pull Request

**PR Description Template:**

```markdown
## Description
Fixes #HBS-123

Added email validation to the guest registration endpoint.

## Changes
- Added `EmailValidator` utility class
- Updated `GuestService.RegisterAsync()` to validate email
- Added unit tests for validation logic

## Testing
- ✅ Unit tests passing (95% coverage)
- ✅ Manual testing completed
- ✅ No breaking changes

## Screenshots (if applicable)
N/A
```

**Afternoon**

- ✅ Address code review feedback (if any)
- ✅ Attend team knowledge sharing session (Fridays at 2 PM)
- ✅ Start reading about CQRS pattern (used in our architecture)

---

### Day 4: Code Review & Collaboration

**Morning**

- ✅ Your first PR gets merged! 🎉
- ✅ Pick second task (slightly more complex)
  - Example: "Implement cancellation fee calculation"
  - Example: "Add pagination to booking history API"
- ✅ Review someone else's PR (learn from others' code)

**Afternoon**

- ✅ Work on second task
- ✅ Ask questions in #hbs-dev (don't hesitate!)
- ✅ Participate in architectural discussion (if any)

**Pro Tip:** At this stage, focus on understanding *why* decisions were made, not just *what* the code does.

---

### Day 5: Testing & Quality

**Morning**

- ✅ Complete second task
- ✅ Write comprehensive tests (unit + integration)
- ✅ Run SonarQube analysis locally
- ✅ Submit second PR

**Afternoon**

- ✅ Week 1 retrospective with mentor
  - What went well?
  - What was challenging?
  - Questions for next week?
- ✅ Celebrate your first week! 🚀

**Week 1 Goals Checklist:**

- [ ] Environment fully set up
- [ ] At least 1 PR merged
- [ ] Understand core domain concepts
- [ ] Know the team and communication channels
- [ ] Comfortable with Git workflow
- [ ] Can run and test code locally

---

### Week 2 and Beyond

**Week 2 Focus:**

- Take on medium-complexity tasks (2-3 story points)
- Start participating in sprint planning discussions
- Learn about deployment process (observe a deployment)
- Deep dive into one domain area (e.g., Payment, Booking, Loyalty)

**Week 3 Focus:**

- Take ownership of a small feature end-to-end
- Participate in code reviews actively
- Write technical documentation for your features
- Understand monitoring and alerting (Azure Application Insights)

**Week 4 Focus:**

- Contribute to sprint planning estimations
- Take on complex tasks (5+ story points)
- Mentor another new joiner (if applicable)
- Present a technical topic in team learning session (optional)

**Month 2-3:**

- Full velocity contributor
- On-call rotation (with buddy)
- Lead small features or technical improvements
- Contribute to architectural decisions

---

## 14. Appendix

### 14.1 Sample Daily Workflow

**Morning Routine (9:00 AM)**

```bash
# 1. Pull latest changes
git checkout develop
git pull origin develop

# 2. Check if your branch needs rebasing
git checkout feature/HBS-123-add-feature
git rebase develop

# 3. Run tests to ensure nothing broke overnight
dotnet test

# 4. Start development
dotnet watch run --project src/HBS.API
```

**During Development**

```bash
# Commit frequently with conventional messages
git add .
git commit -m "feat: add email validation to guest service"

# Run format check before pushing
dotnet format --verify-no-changes

# Push to remote
git push origin feature/HBS-123-add-feature
```

**Before Leaving (5:00 PM)**

```bash
# Ensure all tests pass
dotnet test

# Push your work (even if incomplete)
git push origin feature/HBS-123-add-feature

# Update task status on Azure DevOps board
```

### 14.2 Developer Success Metrics

Our team tracks these metrics to ensure developer productivity and code quality:

| Metric | Target | Actual (Q3 2025) | Purpose |
|--------|--------|------------------|---------|
| Average PR review time | < 24h | 18h | Fast feedback loop |
| Unit test coverage | > 80% | 87% | Code quality |
| Build success rate | > 95% | 97% | CI stability |
| Bugs found post-release | < 5 per sprint | 3 | Quality assurance |
| Deployment frequency | Daily | 1.2x/day | Agility |
| Mean time to recovery | < 1h | 35min | Reliability |
| PR size (lines of code) | < 400 | 320 | Reviewability |

### 14.3 Useful Commands Cheatsheet

**Git Commands**

```bash
# Create and switch to new branch
git checkout -b feature/HBS-XXX-description

# Stash current work
git stash save "work in progress"
git stash pop

# Interactive rebase (clean up commits)
git rebase -i HEAD~3

# Undo last commit (keep changes)
git reset --soft HEAD~1

# View commit history graphically
git log --oneline --graph --all
```

**.NET CLI Commands**

```bash
# Watch mode (hot reload)
dotnet watch run --project src/HBS.API

# Run specific test class
dotnet test --filter "FullyQualifiedName~BookingServiceTests"

# Generate migration
dotnet ef migrations add MigrationName --project src/HBS.Infrastructure

# Update database to specific migration
dotnet ef database update MigrationName --project src/HBS.Infrastructure

# Drop database (careful!)
dotnet ef database drop --project src/HBS.Infrastructure
```

**Docker Commands**

```bash
# View running containers
docker ps

# View logs for specific container
docker logs -f hbs-api

# Execute command inside container
docker exec -it hbs-api bash

# Remove all stopped containers
docker container prune

# Rebuild specific service
docker-compose up -d --build hbs-api
```

### 14.4 IDE Extensions & Tools

**Visual Studio / Rider**

- **ReSharper** - Code analysis and refactoring
- **CodeMaid** - Code cleanup and formatting
- **.editorconfig Language Service** - Enforces coding style
- **SonarLint** - Real-time code quality feedback
- **Entity Framework Core UI Tools** - Visual migration management

**VS Code**

- **C# Dev Kit** - .NET development support
- **REST Client** - Test APIs without Postman
- **GitLens** - Advanced Git integration
- **Thunder Client** - API testing
- **Coverage Gutters** - Show code coverage inline

**Browser Extensions**

- **React DevTools** (for frontend development)
- **JSON Formatter** - Pretty print JSON responses

### 14.5 Learning Resources

**Internal Resources**

- **Confluence Wiki**: [Project Documentation](https://company.atlassian.net/wiki/hbs)
- **Recorded Sessions**: Architecture deep dives, tech talks (Slack #recordings)
- **Code Review Guidelines**: [Link to Confluence]
- **Postman Collection**: [Link to shared workspace]

**External Resources**

| Topic | Resource | Type |
|-------|----------|------|
| Clean Architecture | [Microsoft Docs](https://docs.microsoft.com/dotnet/architecture/) | Documentation |
| CQRS Pattern | [Martin Fowler Article](https://martinfowler.com/bliki/CQRS.html) | Article |
| EF Core Best Practices | [EF Core Docs](https://docs.microsoft.com/ef/core/) | Documentation |
| xUnit Testing | [xUnit Documentation](https://xunit.net/) | Documentation |
| Azure DevOps | [Azure DevOps Labs](https://azuredevopslabs.com/) | Hands-on Labs |

**Recommended Books**

- *Clean Code* by Robert C. Martin
- *Domain-Driven Design* by Eric Evans
- *Designing Data-Intensive Applications* by Martin Kleppmann

### 14.6 Team Contacts

| Role | Name | Slack | Email | Availability |
|------|------|-------|-------|--------------|
| Engineering Manager | Sarah Chen | @sarah.chen | sarah.chen@company.com | Mon-Fri 9am-6pm |
| Tech Lead | Michael Rodriguez | @michael.r | michael.r@company.com | Mon-Fri 10am-7pm |
| Senior Backend Dev | Priya Sharma | @priya | priya.sharma@company.com | Mon-Fri 9am-5pm |
| DevOps Engineer | James Wilson | @james.w | james.w@company.com | Mon-Fri 8am-4pm |
| QA Lead | Lisa Anderson | @lisa.a | lisa.a@company.com | Mon-Fri 9am-6pm |
| Product Owner | David Kim | @david.kim | david.kim@company.com | Mon-Fri 9am-5pm |

**On-Call Rotation:** Check PagerDuty schedule

### 14.7 Acronyms & Terminology

| Term | Full Form | Context |
|------|-----------|---------|
| HBS | Hotel Booking System | Our product |
| CQRS | Command Query Responsibility Segregation | Architecture pattern |
| DDD | Domain-Driven Design | Design approach |
| OTA | Online Travel Agency | External partner |
| PMS | Property Management System | Hotel's internal system |
| ADR | Average Daily Rate | Business metric |
| PR | Pull Request | Code review process |
| CI/CD | Continuous Integration/Deployment | DevOps pipeline |
| SUT | System Under Test | Testing terminology |

---

**Welcome aboard! 🚀**  

You are now part of the HBS Engineering Team. We're excited to have you here!

Remember: **It's okay to ask questions.** We'd rather you ask than be stuck!

*Last updated: October 25, 2025*  
*Next review: January 2026*  
*Maintained by: Engineering PMO*

---