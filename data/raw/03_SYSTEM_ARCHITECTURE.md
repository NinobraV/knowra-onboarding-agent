# Hotel Booking System – System Architecture and Design

---

## Document Information

> **Version:** 1.0  
> **Updated:** October 27, 2025  
> **Author:** KnowRA Architecture Team  
> **Tags:** architecture, design, infrastructure, technical-design, system-design  
> **Status:** Active  

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [System Components](#2-system-components)
3. [Technology Stack](#3-technology-stack)
4. [Architecture Patterns](#4-architecture-patterns)
5. [Data Architecture](#5-data-architecture)
6. [Integration Architecture](#6-integration-architecture)
7. [Security Architecture](#7-security-architecture)
8. [Performance & Scalability](#8-performance--scalability)
9. [Deployment Architecture](#9-deployment-architecture)
10. [Monitoring & Observability](#10-monitoring--observability)
11. [Disaster Recovery & High Availability](#11-disaster-recovery--high-availability)
12. [Architecture Decision Records](#12-architecture-decision-records)

---

## 1. Architecture Overview

### 1.1 High-Level Architecture

The Hotel Booking System follows a **cloud-native, microservices-based architecture** built on Microsoft Azure platform. The system is designed for high availability, scalability, and performance, supporting global hotel chains with millions of bookings.

```
┌─────────────────────────────────────────────────────────────────┐
│                    USERS & EXTERNAL SYSTEMS                     │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   Guest Users   │ Hotel Partners  │    External APIs/OTAs       │
│   (Web/Mobile)  │   (Admin Panel) │   (Payment/Email/SMS)       │
└─────────────────┴─────────────────┴─────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                      AZURE FRONT DOOR                          │
│                 (Global Load Balancer & CDN)                   │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    AZURE API MANAGEMENT                        │
│              (Rate Limiting, Authentication, Monitoring)        │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                         │
├─────────────────┬─────────────────┬─────────────────────────────┤
│  Search Service │ Booking Service │    Payment Service          │
│  (Azure AKS)    │  (Azure AKS)    │    (Azure AKS)              │
├─────────────────┼─────────────────┼─────────────────────────────┤
│  User Service   │ Hotel Service   │  Notification Service       │
│  (Azure AKS)    │ (Azure AKS)     │    (Azure AKS)              │
└─────────────────┴─────────────────┴─────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                       MESSAGE BUS                              │
│                   (Azure Service Bus)                          │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                       DATA LAYER                               │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   SQL Database  │  Redis Cache    │    Blob Storage             │
│ (Azure SQL DB)  │ (Azure Cache)   │  (Images/Documents)         │
├─────────────────┼─────────────────┼─────────────────────────────┤
│  Event Hub      │ Cosmos DB       │   Azure Search              │
│ (Event Stream)  │ (Session Store) │  (Search Index)             │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

### 1.2 Architectural Principles

**1. Cloud-First Design**
- Native Azure services utilization
- Serverless computing where applicable
- Auto-scaling and elastic resource allocation
- Pay-per-use cost optimization

**2. Microservices Architecture**
- Domain-driven design boundaries
- Independent deployment and scaling
- Technology diversity where beneficial
- Fault isolation and resilience

**3. API-First Approach**
- RESTful API design principles
- OpenAPI 3.0 specification compliance
- Versioning strategy for backward compatibility
- Rate limiting and throttling

**4. Security by Design**
- Zero-trust security model
- Encryption at rest and in transit
- Role-based access control (RBAC)
- Compliance with industry standards (PCI DSS, GDPR)

**5. Observability & Monitoring**
- Comprehensive logging and tracing
- Real-time monitoring and alerting
- Performance metrics and SLA tracking
- Health checks and proactive maintenance

### 1.3 Design Patterns

**Primary Patterns:**
- **Clean Architecture:** Separation of concerns with dependency inversion
- **CQRS (Command Query Responsibility Segregation):** Separate read/write models
- **Event Sourcing:** Audit trail and state reconstruction capabilities
- **Saga Pattern:** Distributed transaction management
- **Circuit Breaker:** Fault tolerance for external service calls
- **API Gateway:** Centralized request handling and cross-cutting concerns

---

## 2. System Components

### 2.1 Frontend Layer

**Guest Booking Interface**
- **Technology:** React 18 + TypeScript + Next.js 14
- **Architecture:** Server-Side Rendering (SSR) with Static Site Generation (SSG)
- **State Management:** Redux Toolkit with RTK Query
- **Styling:** Tailwind CSS with custom design system
- **Features:**
  - Progressive Web App (PWA) capabilities
  - Responsive design (mobile-first approach)
  - Real-time search suggestions
  - Interactive maps integration
  - Multi-language support (i18n)

**Hotel Partner Portal**
- **Technology:** React Admin framework with Material-UI
- **Features:**
  - Property management dashboard
  - Real-time booking notifications
  - Revenue analytics and reporting
  - Inventory and rate management
  - Guest communication tools

**Component Architecture:**
```
src/
├── components/           # Reusable UI components
│   ├── common/          # Generic components
│   ├── search/          # Search-specific components
│   └── booking/         # Booking flow components
├── pages/               # Next.js pages (SSR/SSG)
├── hooks/               # Custom React hooks
├── store/               # Redux store configuration
├── services/            # API service layer
├── utils/               # Helper functions
└── types/               # TypeScript type definitions
```

### 2.2 API Gateway Layer

**Azure API Management**
- **Purpose:** Centralized API gateway for all client requests
- **Features:**
  - Rate limiting and throttling (1000 requests/minute per user)
  - Authentication and authorization
  - Request/response transformation
  - API versioning and documentation
  - Analytics and monitoring
  - Caching for GET requests (TTL: 5 minutes)

**Policies Configuration:**
```xml
<policies>
    <inbound>
        <rate-limit calls="1000" renewal-period="60" />
        <validate-jwt header-name="Authorization" />
        <cors allow-credentials="true">
            <allowed-origins>
                <origin>https://booking.knowra.com</origin>
            </allowed-origins>
        </cors>
    </inbound>
    <backend>
        <retry condition="@(context.Response.StatusCode >= 500)" 
               count="3" interval="1" />
    </backend>
</policies>
```

### 2.3 Application Layer

**Microservices Architecture:**

**1. Search Service**
- **Responsibility:** Hotel discovery and filtering
- **Technology:** .NET 8 Web API + Azure Cognitive Search
- **Features:**
  - Full-text search with relevance scoring
  - Faceted navigation and filtering
  - Geospatial search capabilities
  - Auto-complete and suggestions
  - Search analytics and optimization

**2. Booking Service**
- **Responsibility:** Reservation management and processing
- **Technology:** .NET 8 Web API + Entity Framework Core
- **Features:**
  - Real-time inventory management
  - Booking workflow orchestration
  - Cancellation and modification handling
  - Overbooking protection algorithms
  - Booking confirmation and notifications

**3. Payment Service**
- **Responsibility:** Payment processing and financial transactions
- **Technology:** .NET 8 Web API + PCI DSS compliant architecture
- **Features:**
  - Multi-gateway payment processing (Stripe, PayPal, Adyen)
  - Fraud detection and prevention
  - Refund and chargeback management
  - Currency conversion and localization
  - Payment reconciliation and reporting

**4. User Service**
- **Responsibility:** User management and authentication
- **Technology:** .NET 8 Web API + Azure Active Directory B2C
- **Features:**
  - User registration and profile management
  - Social login integration (Google, Facebook, Apple)
  - Multi-factor authentication (MFA)
  - Password policies and security
  - User preferences and personalization

**5. Hotel Service**
- **Responsibility:** Property and inventory management
- **Technology:** .NET 8 Web API + Entity Framework Core
- **Features:**
  - Property information management
  - Room type and amenity configuration
  - Rate and availability management
  - Photo and content management
  - Revenue management integration

**6. Notification Service**
- **Responsibility:** Communication and messaging
- **Technology:** .NET 8 Web API + Azure Service Bus
- **Features:**
  - Email notifications (transactional and marketing)
  - SMS notifications (OTP, confirmations)
  - Push notifications (mobile apps)
  - Real-time updates via WebSocket
  - Communication preferences management

### 2.4 Data Layer

**Primary Database: Azure SQL Database**
- **Configuration:** General Purpose tier with 8 vCores
- **Features:**
  - Automatic tuning and performance insights
  - Built-in high availability (99.99% SLA)
  - Point-in-time restore (35 days)
  - Transparent Data Encryption (TDE)
  - Advanced Threat Protection

**Caching Layer: Azure Cache for Redis**
- **Configuration:** Standard C2 (2.5 GB)
- **Use Cases:**
  - Session storage and user state
  - Search result caching
  - Rate limiting counters
  - Real-time data synchronization
  - Distributed locking mechanisms

**Search Index: Azure Cognitive Search**
- **Configuration:** Standard S1 tier
- **Features:**
  - Full-text search with linguistic analysis
  - Faceted navigation and filtering
  - Geospatial search capabilities
  - AI-powered enrichment pipeline
  - Search analytics and telemetry

**File Storage: Azure Blob Storage**
- **Configuration:** Hot tier with LRS redundancy
- **Content Types:**
  - Property images and videos
  - Legal documents and contracts
  - User-generated content
  - Backup files and logs
  - CDN integration for global delivery

### 2.5 Integration Layer

**Message Broker: Azure Service Bus**
- **Configuration:** Standard tier with topics and subscriptions
- **Message Patterns:**
  - Publish-Subscribe for event distribution
  - Request-Response for synchronous communication
  - Dead letter queues for error handling
  - Message sessions for ordered processing
  - Duplicate detection and deduplication

**Event Streaming: Azure Event Hubs**
- **Configuration:** Standard tier with 20 throughput units
- **Use Cases:**
  - Real-time analytics and reporting
  - Audit trail and compliance logging
  - User behavior tracking
  - System monitoring and alerting
  - Machine learning pipeline integration

---

## 3. Technology Stack

### 3.1 Backend Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Runtime** | .NET | 8.0 LTS | Primary backend framework |
| **Web Framework** | ASP.NET Core | 8.0 | Web API development |
| **ORM** | Entity Framework Core | 8.0 | Database access layer |
| **Validation** | FluentValidation | 11.x | Input validation |
| **Mapping** | AutoMapper | 12.x | Object-to-object mapping |
| **Logging** | Serilog | 3.x | Structured logging |
| **Testing** | xUnit + Moq | Latest | Unit and integration testing |
| **Documentation** | Swagger/OpenAPI | 3.0 | API documentation |
| **Security** | JWT + OAuth 2.0 | Latest | Authentication & authorization |

**Key Libraries and Packages:**
```xml
<PackageReference Include="Microsoft.AspNetCore.OpenApi" Version="8.0.0" />
<PackageReference Include="Microsoft.EntityFrameworkCore.SqlServer" Version="8.0.0" />
<PackageReference Include="Microsoft.EntityFrameworkCore.Tools" Version="8.0.0" />
<PackageReference Include="FluentValidation.AspNetCore" Version="11.3.0" />
<PackageReference Include="AutoMapper.Extensions.Microsoft.DependencyInjection" Version="12.0.1" />
<PackageReference Include="Serilog.AspNetCore" Version="7.0.0" />
<PackageReference Include="Azure.Identity" Version="1.10.4" />
<PackageReference Include="Azure.Security.KeyVault.Secrets" Version="4.5.0" />
<PackageReference Include="StackExchange.Redis" Version="2.6.122" />
```

### 3.2 Frontend Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Framework** | React | 18.x | UI library |
| **Meta Framework** | Next.js | 14.x | Full-stack React framework |
| **Language** | TypeScript | 5.x | Type-safe JavaScript |
| **State Management** | Redux Toolkit | 1.9.x | Application state management |
| **Data Fetching** | RTK Query | 1.9.x | API state management |
| **Styling** | Tailwind CSS | 3.x | Utility-first CSS framework |
| **UI Components** | Headless UI | 1.x | Unstyled, accessible UI components |
| **Forms** | React Hook Form | 7.x | Form handling and validation |
| **Icons** | Heroicons | 2.x | SVG icon library |
| **Testing** | Jest + Testing Library | Latest | Unit and integration testing |

**Package.json Dependencies:**
```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@reduxjs/toolkit": "^1.9.0",
    "react-redux": "^8.1.0",
    "react-hook-form": "^7.45.0",
    "@hookform/resolvers": "^3.1.0",
    "zod": "^3.21.0",
    "tailwindcss": "^3.3.0",
    "@headlessui/react": "^1.7.0",
    "@heroicons/react": "^2.0.0",
    "next-i18next": "^14.0.0"
  }
}
```

### 3.3 Database & Caching

**Database Design:**
- **Azure SQL Database** (Primary data store)
  - Performance Level: S2 (50 DTUs)
  - Storage: 250 GB with auto-growth
  - Backup Retention: 35 days
  - Geo-replication: Enabled for disaster recovery

- **Azure Cache for Redis** (Caching layer)
  - Tier: Standard C2 (2.5 GB)
  - Persistence: RDB snapshots every 6 hours
  - Clustering: Disabled (single instance)
  - SSL: Enabled for secure connections

**Database Schema Overview:**
```sql
-- Core Tables
Users (UserId, Email, PasswordHash, Profile, Preferences)
Hotels (HotelId, Name, Address, Description, Amenities)
Rooms (RoomId, HotelId, RoomType, Capacity, Amenities)
Rates (RateId, RoomId, Date, Price, Currency, Restrictions)
Bookings (BookingId, UserId, HotelId, RoomId, CheckIn, CheckOut, Status)
Payments (PaymentId, BookingId, Amount, Method, Status, TransactionId)

-- Supporting Tables
Reviews (ReviewId, BookingId, Rating, Comment, Response)
Promotions (PromotionId, HotelId, DiscountType, ValidFrom, ValidTo)
Loyalty (LoyaltyId, UserId, Points, Tier, Benefits)
Audit (AuditId, TableName, Operation, OldValues, NewValues, Timestamp)
```

### 3.4 Cloud Infrastructure

**Azure Services Utilization:**

| Service | Configuration | Purpose |
|---------|---------------|---------|
| **Azure Kubernetes Service** | 3 node pools (2-10 nodes) | Container orchestration |
| **Azure App Service** | P2V2 pricing tier | Web application hosting |
| **Azure SQL Database** | General Purpose 8 vCores | Primary data storage |
| **Azure Cache for Redis** | Standard C2 (2.5GB) | Caching and session storage |
| **Azure Blob Storage** | Hot tier, LRS | File and media storage |
| **Azure CDN** | Standard Microsoft | Global content delivery |
| **Azure Key Vault** | Standard tier | Secrets and certificate management |
| **Azure Monitor** | Standard pricing | Logging and monitoring |
| **Azure Application Insights** | Standard pricing | Application performance monitoring |
| **Azure Service Bus** | Standard tier | Message queuing |
| **Azure Front Door** | Standard tier | Global load balancing |

**Resource Organization:**
```
Subscription: Hotel-Booking-Production
├── Resource Group: hbs-prod-eastus
│   ├── AKS Cluster: hbs-prod-aks
│   ├── SQL Server: hbs-prod-sql
│   ├── Redis Cache: hbs-prod-redis
│   └── Storage Account: hbsprodstorageeastus
├── Resource Group: hbs-prod-westeurope (DR)
│   ├── SQL Database (Geo-replica)
│   └── Storage Account (GRS replication)
└── Resource Group: hbs-shared-global
    ├── Azure Front Door: hbs-global-afd
    ├── Key Vault: hbs-global-kv
    └── Monitor Workspace: hbs-global-logs
```

### 3.5 DevOps & CI/CD

**Source Control:**
- **Git** with Azure DevOps Repos
- **Branching Strategy:** GitFlow with feature branches
- **Code Reviews:** Required for all pull requests
- **Automated Quality Gates:** SonarQube integration

**Build Pipeline:**
```yaml
trigger:
  branches:
    include:
    - main
    - develop
  paths:
    include:
    - src/*

variables:
  buildConfiguration: 'Release'
  dockerRegistryServiceConnection: 'ACR-Connection'
  imageRepository: 'hotel-booking-api'
  containerRegistry: 'hbsprodacr.azurecr.io'

stages:
- stage: Build
  jobs:
  - job: BuildAndTest
    pool:
      vmImage: 'ubuntu-latest'
    steps:
    - task: UseDotNet@2
      inputs:
        version: '8.0.x'
    - task: DotNetCoreCLI@2
      displayName: 'Restore packages'
      inputs:
        command: 'restore'
    - task: DotNetCoreCLI@2
      displayName: 'Build solution'
      inputs:
        command: 'build'
        configuration: $(buildConfiguration)
    - task: DotNetCoreCLI@2
      displayName: 'Run unit tests'
      inputs:
        command: 'test'
        projects: '**/*Tests.csproj'
```

**Deployment Strategy:**
- **Blue-Green Deployment:** Zero-downtime deployments
- **Infrastructure as Code:** ARM templates and Bicep
- **Container Registry:** Azure Container Registry (ACR)
- **Orchestration:** Azure Kubernetes Service (AKS)
- **Configuration Management:** Azure Key Vault integration

---

## 4. Architecture Patterns

### 4.1 Clean Architecture

**Layer Structure:**
```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                          │
│              (Controllers, DTOs, Validators)                   │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                           │
│           (Use Cases, Interfaces, Command/Query)               │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                     DOMAIN LAYER                               │
│              (Entities, Value Objects, Rules)                  │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                          │
│           (Database, External APIs, Email, etc.)               │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation Example:**
```csharp
// Domain Layer - Entity
public class Booking : BaseEntity
{
    public Guid UserId { get; private set; }
    public Guid HotelId { get; private set; }
    public DateTime CheckIn { get; private set; }
    public DateTime CheckOut { get; private set; }
    public BookingStatus Status { get; private set; }
    public decimal TotalAmount { get; private set; }

    public static Booking Create(Guid userId, Guid hotelId, 
        DateTime checkIn, DateTime checkOut, decimal amount)
    {
        // Business rule validation
        if (checkIn >= checkOut)
            throw new DomainException("Check-in must be before check-out");
        
        return new Booking
        {
            UserId = userId,
            HotelId = hotelId,
            CheckIn = checkIn,
            CheckOut = checkOut,
            TotalAmount = amount,
            Status = BookingStatus.Pending
        };
    }
}

// Application Layer - Use Case
public class CreateBookingCommand : IRequest<BookingDto>
{
    public Guid UserId { get; set; }
    public Guid HotelId { get; set; }
    public DateTime CheckIn { get; set; }
    public DateTime CheckOut { get; set; }
    public List<RoomRequest> Rooms { get; set; }
}

public class CreateBookingCommandHandler : IRequestHandler<CreateBookingCommand, BookingDto>
{
    private readonly IBookingRepository _bookingRepository;
    private readonly IHotelService _hotelService;
    private readonly IPaymentService _paymentService;

    public async Task<BookingDto> Handle(CreateBookingCommand request, 
        CancellationToken cancellationToken)
    {
        // Check availability
        var availability = await _hotelService.CheckAvailabilityAsync(
            request.HotelId, request.CheckIn, request.CheckOut);
        
        if (!availability.IsAvailable)
            throw new InvalidOperationException("Hotel not available for selected dates");
        
        // Create booking
        var booking = Booking.Create(request.UserId, request.HotelId, 
            request.CheckIn, request.CheckOut, availability.TotalAmount);
        
        // Save booking
        await _bookingRepository.AddAsync(booking);
        
        return MapToDto(booking);
    }
}
```

### 4.2 CQRS Pattern

**Command Query Separation:**

```csharp
// Command Side - Write Operations
public interface IBookingCommandService
{
    Task<Guid> CreateBookingAsync(CreateBookingCommand command);
    Task UpdateBookingAsync(UpdateBookingCommand command);
    Task CancelBookingAsync(CancelBookingCommand command);
}

// Query Side - Read Operations
public interface IBookingQueryService
{
    Task<BookingDto> GetBookingAsync(Guid bookingId);
    Task<PagedResult<BookingDto>> GetUserBookingsAsync(Guid userId, int page, int size);
    Task<BookingSearchResult> SearchBookingsAsync(BookingSearchQuery query);
}

// Implementation with separate read/write models
public class BookingCommandService : IBookingCommandService
{
    private readonly IBookingRepository _repository;
    private readonly IEventBus _eventBus;

    public async Task<Guid> CreateBookingAsync(CreateBookingCommand command)
    {
        var booking = Booking.Create(/* parameters */);
        await _repository.AddAsync(booking);
        
        // Publish domain event
        await _eventBus.PublishAsync(new BookingCreatedEvent(booking.Id));
        
        return booking.Id;
    }
}

public class BookingQueryService : IBookingQueryService
{
    private readonly IReadOnlyRepository<BookingReadModel> _readRepository;

    public async Task<BookingDto> GetBookingAsync(Guid bookingId)
    {
        var booking = await _readRepository.GetByIdAsync(bookingId);
        return MapToDto(booking);
    }
}
```

### 4.3 Event-Driven Architecture

**Event Flow:**
```
┌─────────────────┐    Event     ┌─────────────────┐    Event     ┌─────────────────┐
│   Command       │─────────────→│   Domain        │─────────────→│   Event         │
│   Handler       │              │   Model         │              │   Store         │
└─────────────────┘              └─────────────────┘              └─────────────────┘
                                           │                                │
                                           ▼                                ▼
┌─────────────────┐              ┌─────────────────┐              ┌─────────────────┐
│   Notification  │              │   Read Model    │              │   Event         │
│   Service       │◄─────────────│   Projector    │◄─────────────│   Bus           │
└─────────────────┘              └─────────────────┘              └─────────────────┘
```

**Event Implementation:**
```csharp
// Domain Events
public class BookingCreatedEvent : DomainEvent
{
    public Guid BookingId { get; }
    public Guid UserId { get; }
    public Guid HotelId { get; }
    public DateTime CheckIn { get; }
    public DateTime CheckOut { get; }
    public decimal Amount { get; }

    public BookingCreatedEvent(Guid bookingId, Guid userId, Guid hotelId,
        DateTime checkIn, DateTime checkOut, decimal amount)
    {
        BookingId = bookingId;
        UserId = userId;
        HotelId = hotelId;
        CheckIn = checkIn;
        CheckOut = checkOut;
        Amount = amount;
    }
}

// Event Handlers
public class BookingCreatedEventHandler : INotificationHandler<BookingCreatedEvent>
{
    private readonly IEmailService _emailService;
    private readonly INotificationService _notificationService;

    public async Task Handle(BookingCreatedEvent notification, 
        CancellationToken cancellationToken)
    {
        // Send confirmation email
        await _emailService.SendBookingConfirmationAsync(
            notification.UserId, notification.BookingId);
        
        // Update hotel inventory
        await _inventoryService.ReserveRoomAsync(
            notification.HotelId, notification.CheckIn, notification.CheckOut);
        
        // Create loyalty points
        await _loyaltyService.AwardPointsAsync(
            notification.UserId, notification.Amount);
    }
}
```

### 4.4 Microservices Approach

**Service Boundaries (Domain-Driven Design):**

```
┌─────────────────────────────────────────────────────────────────┐
│                        BOOKING CONTEXT                         │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   Booking       │   Inventory     │    Pricing                  │
│   Aggregate     │   Management    │    Engine                   │
└─────────────────┴─────────────────┴─────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         USER CONTEXT                           │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   User          │   Authentication│    Preferences             │
│   Profile       │   & Identity    │    & Settings               │
└─────────────────┴─────────────────┴─────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       PAYMENT CONTEXT                          │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   Payment       │   Billing       │    Fraud                   │
│   Processing    │   & Invoicing   │    Detection                │
└─────────────────┴─────────────────┴─────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       HOTEL CONTEXT                            │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   Property      │   Content       │    Revenue                  │
│   Management    │   Management    │    Management               │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

**Inter-Service Communication:**
```csharp
// Synchronous Communication (HTTP)
public class HotelApiClient : IHotelService
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<HotelApiClient> _logger;

    public async Task<HotelAvailability> CheckAvailabilityAsync(
        Guid hotelId, DateTime checkIn, DateTime checkOut)
    {
        var request = new AvailabilityRequest
        {
            HotelId = hotelId,
            CheckIn = checkIn,
            CheckOut = checkOut
        };

        var response = await _httpClient.PostAsJsonAsync(
            "/api/hotels/check-availability", request);
        
        response.EnsureSuccessStatusCode();
        
        return await response.Content.ReadFromJsonAsync<HotelAvailability>();
    }
}

// Asynchronous Communication (Message Bus)
public class BookingEventPublisher : IBookingEventPublisher
{
    private readonly IServiceBusClient _serviceBusClient;

    public async Task PublishBookingCreatedAsync(BookingCreatedEvent bookingEvent)
    {
        var message = new ServiceBusMessage(JsonSerializer.Serialize(bookingEvent))
        {
            Subject = "BookingCreated",
            MessageId = Guid.NewGuid().ToString(),
            ContentType = "application/json"
        };

        await _serviceBusClient.SendMessageAsync(message);
    }
}
```

---

## 5. Data Architecture

### 5.1 Database Schema Design

**Entity Relationship Overview:**
```sql
-- Users and Authentication
CREATE TABLE Users (
    UserId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    Email NVARCHAR(255) UNIQUE NOT NULL,
    PasswordHash NVARCHAR(255) NOT NULL,
    FirstName NVARCHAR(100) NOT NULL,
    LastName NVARCHAR(100) NOT NULL,
    PhoneNumber NVARCHAR(20),
    DateOfBirth DATE,
    Gender CHAR(1),
    Nationality NVARCHAR(50),
    PreferredLanguage CHAR(2) DEFAULT 'EN',
    PreferredCurrency CHAR(3) DEFAULT 'USD',
    IsEmailVerified BIT DEFAULT 0,
    IsPhoneVerified BIT DEFAULT 0,
    CreatedAt DATETIME2 DEFAULT GETUTCDATE(),
    UpdatedAt DATETIME2 DEFAULT GETUTCDATE(),
    IsActive BIT DEFAULT 1,
    
    INDEX IX_Users_Email (Email),
    INDEX IX_Users_CreatedAt (CreatedAt)
);

-- Hotels and Properties
CREATE TABLE Hotels (
    HotelId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    PartnerUserId UNIQUEIDENTIFIER NOT NULL,
    HotelChainId UNIQUEIDENTIFIER NULL,
    Name NVARCHAR(200) NOT NULL,
    Description NVARCHAR(MAX),
    Address NVARCHAR(500) NOT NULL,
    City NVARCHAR(100) NOT NULL,
    State NVARCHAR(100),
    Country NVARCHAR(100) NOT NULL,
    PostalCode NVARCHAR(20),
    Latitude DECIMAL(10,8),
    Longitude DECIMAL(11,8),
    StarRating TINYINT CHECK (StarRating BETWEEN 1 AND 5),
    PhoneNumber NVARCHAR(20),
    Email NVARCHAR(255),
    Website NVARCHAR(255),
    CheckInTime TIME DEFAULT '15:00:00',
    CheckOutTime TIME DEFAULT '11:00:00',
    CancellationPolicy NVARCHAR(MAX),
    ChildPolicy NVARCHAR(MAX),
    PetPolicy NVARCHAR(MAX),
    IsActive BIT DEFAULT 1,
    CreatedAt DATETIME2 DEFAULT GETUTCDATE(),
    UpdatedAt DATETIME2 DEFAULT GETUTCDATE(),
    
    FOREIGN KEY (PartnerUserId) REFERENCES Users(UserId),
    INDEX IX_Hotels_City_Country (City, Country),
    INDEX IX_Hotels_Location (Latitude, Longitude),
    INDEX IX_Hotels_StarRating (StarRating)
);

-- Room Types and Inventory
CREATE TABLE RoomTypes (
    RoomTypeId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    HotelId UNIQUEIDENTIFIER NOT NULL,
    Name NVARCHAR(100) NOT NULL,
    Description NVARCHAR(MAX),
    MaxOccupancy TINYINT NOT NULL,
    MaxAdults TINYINT NOT NULL,
    MaxChildren TINYINT NOT NULL,
    BedConfiguration NVARCHAR(100),
    RoomSize DECIMAL(8,2),
    SizeUnit CHAR(2) DEFAULT 'M2',
    FloorLevel NVARCHAR(50),
    ViewType NVARCHAR(50),
    SmokingAllowed BIT DEFAULT 0,
    IsActive BIT DEFAULT 1,
    
    FOREIGN KEY (HotelId) REFERENCES Hotels(HotelId),
    INDEX IX_RoomTypes_Hotel (HotelId)
);

CREATE TABLE RoomInventory (
    InventoryId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    RoomTypeId UNIQUEIDENTIFIER NOT NULL,
    Date DATE NOT NULL,
    TotalRooms INT NOT NULL,
    AvailableRooms INT NOT NULL,
    ReservedRooms INT NOT NULL,
    BlockedRooms INT DEFAULT 0,
    MinimumStay INT DEFAULT 1,
    MaximumStay INT DEFAULT 30,
    CloseToArrival BIT DEFAULT 0,
    CloseToDeparture BIT DEFAULT 0,
    CreatedAt DATETIME2 DEFAULT GETUTCDATE(),
    UpdatedAt DATETIME2 DEFAULT GETUTCDATE(),
    
    FOREIGN KEY (RoomTypeId) REFERENCES RoomTypes(RoomTypeId),
    UNIQUE INDEX UX_RoomInventory_RoomType_Date (RoomTypeId, Date),
    INDEX IX_RoomInventory_Date (Date)
);

-- Pricing and Rates
CREATE TABLE RatePlans (
    RatePlanId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    RoomTypeId UNIQUEIDENTIFIER NOT NULL,
    Name NVARCHAR(100) NOT NULL,
    Description NVARCHAR(500),
    RateType NVARCHAR(20) NOT NULL, -- 'BAR', 'CORPORATE', 'PROMOTIONAL'
    Currency CHAR(3) NOT NULL DEFAULT 'USD',
    IsRefundable BIT DEFAULT 1,
    CancellationDeadlineHours INT DEFAULT 24,
    CancellationFeePercent DECIMAL(5,2) DEFAULT 0,
    PrepaymentRequired BIT DEFAULT 0,
    BreakfastIncluded BIT DEFAULT 0,
    IsActive BIT DEFAULT 1,
    ValidFrom DATE NOT NULL,
    ValidTo DATE NOT NULL,
    
    FOREIGN KEY (RoomTypeId) REFERENCES RoomTypes(RoomTypeId),
    INDEX IX_RatePlans_RoomType (RoomTypeId),
    INDEX IX_RatePlans_Validity (ValidFrom, ValidTo)
);

CREATE TABLE RoomRates (
    RateId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    RatePlanId UNIQUEIDENTIFIER NOT NULL,
    Date DATE NOT NULL,
    BaseRate DECIMAL(10,2) NOT NULL,
    TaxAmount DECIMAL(10,2) DEFAULT 0,
    ServiceChargeAmount DECIMAL(10,2) DEFAULT 0,
    TotalRate AS (BaseRate + TaxAmount + ServiceChargeAmount) PERSISTED,
    MinimumStay INT DEFAULT 1,
    MaximumStay INT DEFAULT 30,
    IsAvailable BIT DEFAULT 1,
    
    FOREIGN KEY (RatePlanId) REFERENCES RatePlans(RatePlanId),
    UNIQUE INDEX UX_RoomRates_RatePlan_Date (RatePlanId, Date),
    INDEX IX_RoomRates_Date (Date)
);

-- Bookings and Reservations
CREATE TABLE Bookings (
    BookingId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    BookingReference NVARCHAR(20) UNIQUE NOT NULL,
    UserId UNIQUEIDENTIFIER NOT NULL,
    HotelId UNIQUEIDENTIFIER NOT NULL,
    RoomTypeId UNIQUEIDENTIFIER NOT NULL,
    RatePlanId UNIQUEIDENTIFIER NOT NULL,
    CheckInDate DATE NOT NULL,
    CheckOutDate DATE NOT NULL,
    Adults TINYINT NOT NULL,
    Children TINYINT DEFAULT 0,
    Rooms TINYINT DEFAULT 1,
    Status NVARCHAR(20) NOT NULL DEFAULT 'PENDING', -- PENDING, CONFIRMED, CANCELLED, COMPLETED, NO_SHOW
    SubTotal DECIMAL(10,2) NOT NULL,
    TaxAmount DECIMAL(10,2) NOT NULL,
    TotalAmount DECIMAL(10,2) NOT NULL,
    Currency CHAR(3) NOT NULL,
    SpecialRequests NVARCHAR(MAX),
    GuestTitle NVARCHAR(10),
    GuestFirstName NVARCHAR(100) NOT NULL,
    GuestLastName NVARCHAR(100) NOT NULL,
    GuestEmail NVARCHAR(255) NOT NULL,
    GuestPhone NVARCHAR(20),
    BillingAddress NVARCHAR(MAX),
    CancellationReason NVARCHAR(500),
    CancelledAt DATETIME2,
    CreatedAt DATETIME2 DEFAULT GETUTCDATE(),
    UpdatedAt DATETIME2 DEFAULT GETUTCDATE(),
    
    FOREIGN KEY (UserId) REFERENCES Users(UserId),
    FOREIGN KEY (HotelId) REFERENCES Hotels(HotelId),
    FOREIGN KEY (RoomTypeId) REFERENCES RoomTypes(RoomTypeId),
    FOREIGN KEY (RatePlanId) REFERENCES RatePlans(RatePlanId),
    INDEX IX_Bookings_User (UserId),
    INDEX IX_Bookings_Hotel (HotelId),
    INDEX IX_Bookings_CheckIn (CheckInDate),
    INDEX IX_Bookings_Status (Status),
    INDEX IX_Bookings_Reference (BookingReference)
);

-- Payments and Transactions
CREATE TABLE Payments (
    PaymentId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    BookingId UNIQUEIDENTIFIER NOT NULL,
    TransactionId NVARCHAR(100) UNIQUE,
    PaymentMethod NVARCHAR(20) NOT NULL, -- 'CREDIT_CARD', 'DEBIT_CARD', 'PAYPAL', 'BANK_TRANSFER'
    PaymentGateway NVARCHAR(20) NOT NULL, -- 'STRIPE', 'PAYPAL', 'ADYEN'
    Amount DECIMAL(10,2) NOT NULL,
    Currency CHAR(3) NOT NULL,
    Status NVARCHAR(20) NOT NULL DEFAULT 'PENDING', -- PENDING, PROCESSING, COMPLETED, FAILED, REFUNDED
    GatewayResponse NVARCHAR(MAX),
    ProcessedAt DATETIME2,
    FailureReason NVARCHAR(500),
    RefundAmount DECIMAL(10,2) DEFAULT 0,
    RefundedAt DATETIME2,
    CreatedAt DATETIME2 DEFAULT GETUTCDATE(),
    
    FOREIGN KEY (BookingId) REFERENCES Bookings(BookingId),
    INDEX IX_Payments_Booking (BookingId),
    INDEX IX_Payments_Status (Status),
    INDEX IX_Payments_TransactionId (TransactionId)
);
```

### 5.2 Data Flow Diagrams

**Booking Flow Data Movement:**
```
┌─────────────────┐    Search     ┌─────────────────┐    Filter     ┌─────────────────┐
│   User Input    │─────────────→│   Search API    │─────────────→│  Search Index   │
│  (Destination,  │               │                 │               │ (Azure Cognitive│
│   Dates, etc.)  │               │                 │               │    Search)      │
└─────────────────┘               └─────────────────┘               └─────────────────┘
                                           │                                │
                                           ▼                                ▼
┌─────────────────┐               ┌─────────────────┐               ┌─────────────────┐
│   Booking API   │◄──────────────│  Search Results │◄──────────────│   Hotel Data    │
│                 │   Selection   │    (Filtered)   │   Enrichment  │   (Database)    │
└─────────────────┘               └─────────────────┘               └─────────────────┘
         │                                                                   │
         ▼                                                                   ▼
┌─────────────────┐               ┌─────────────────┐               ┌─────────────────┐
│ Inventory Check │─────────────→│   Booking       │─────────────→│   Inventory     │
│   (Real-time)   │  Availability │   Creation      │   Update      │   Update        │
└─────────────────┘               └─────────────────┘               └─────────────────┘
         │                                │                                │
         ▼                                ▼                                ▼
┌─────────────────┐               ┌─────────────────┐               ┌─────────────────┐
│ Payment Gateway │◄──────────────│ Payment Request │─────────────→│   Audit Log     │
│   Processing    │   Charge      │                 │   Activity    │                 │
└─────────────────┘               └─────────────────┘               └─────────────────┘
```

**Real-time Data Synchronization:**
```
┌─────────────────┐    Change     ┌─────────────────┐    Event      ┌─────────────────┐
│   Database      │─────────────→│   CDC Process   │─────────────→│   Event Hub     │
│   (SQL Server)  │   Detection   │   (Change Data  │   Streaming   │                 │
│                 │               │    Capture)     │               │                 │
└─────────────────┘               └─────────────────┘               └─────────────────┘
                                                                            │
                                                                            ▼
┌─────────────────┐               ┌─────────────────┐               ┌─────────────────┐
│   Redis Cache   │◄──────────────│   Cache         │◄──────────────│  Event Stream   │
│   (Updated)     │   Refresh     │   Invalidation  │   Processing  │   Processor     │
└─────────────────┘               └─────────────────┘               └─────────────────┘
         │                                                                   │
         ▼                                                                   ▼
┌─────────────────┐               ┌─────────────────┐               ┌─────────────────┐
│   Search Index  │               │   Analytics     │               │   Notification  │
│   (Updated)     │               │   Dashboard     │               │   Service       │
└─────────────────┘               └─────────────────┘               └─────────────────┘
```

### 5.3 Caching Strategy

**Cache Layers and TTL Configuration:**

| Data Type | Cache Layer | TTL | Invalidation Strategy |
|-----------|-------------|-----|----------------------|
| **Hotel Search Results** | Redis | 5 minutes | Tag-based (location, dates) |
| **Hotel Details** | Redis | 1 hour | Event-driven (hotel updates) |
| **Room Availability** | Redis | 30 seconds | Real-time (booking events) |
| **User Sessions** | Redis | 24 hours | Sliding expiration |
| **Rate Plans** | Redis | 15 minutes | Event-driven (rate changes) |
| **Static Content** | CDN | 24 hours | Version-based |
| **API Responses** | Application | 2 minutes | Memory cache |

**Implementation Example:**
```csharp
public class CacheService : ICacheService
{
    private readonly IDistributedCache _distributedCache;
    private readonly IMemoryCache _memoryCache;
    private readonly ILogger<CacheService> _logger;

    public async Task<T> GetOrSetAsync<T>(string key, Func<Task<T>> factory, 
        TimeSpan? expiry = null, CacheLevel level = CacheLevel.Distributed)
    {
        var cache = level == CacheLevel.Memory ? _memoryCache : _distributedCache;
        
        // Try to get from cache
        var cachedValue = await GetFromCacheAsync<T>(key, cache);
        if (cachedValue != null)
        {
            _logger.LogDebug("Cache hit for key: {Key}", key);
            return cachedValue;
        }

        // Cache miss - get from factory
        _logger.LogDebug("Cache miss for key: {Key}", key);
        var value = await factory();
        
        // Set in cache
        await SetInCacheAsync(key, value, expiry ?? TimeSpan.FromMinutes(5), cache);
        
        return value;
    }

    public async Task InvalidateByTagAsync(string tag)
    {
        // Implementation for tag-based cache invalidation
        var keys = await GetKeysByTagAsync(tag);
        foreach (var key in keys)
        {
            await _distributedCache.RemoveAsync(key);
        }
        
        _logger.LogInformation("Invalidated {Count} cache entries for tag: {Tag}", 
            keys.Count, tag);
    }
}

// Usage in service layer
public class HotelSearchService : IHotelSearchService
{
    private readonly ICacheService _cacheService;
    private readonly IHotelRepository _hotelRepository;

    public async Task<SearchResult> SearchHotelsAsync(SearchRequest request)
    {
        var cacheKey = $"search:{request.GetHashCode()}";
        
        return await _cacheService.GetOrSetAsync(
            cacheKey,
            () => PerformSearchAsync(request),
            TimeSpan.FromMinutes(5),
            CacheLevel.Distributed
        );
    }
}
```

### 5.4 Data Migration & Versioning

**Database Migration Strategy:**
```csharp
// Entity Framework Migration Example
public partial class AddBookingEnhancements : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        // Add new columns
        migrationBuilder.AddColumn<string>(
            name: "CancellationReason",
            table: "Bookings",
            type: "nvarchar(500)",
            maxLength: 500,
            nullable: true);

        migrationBuilder.AddColumn<DateTime>(
            name: "CancelledAt",
            table: "Bookings",
            type: "datetime2",
            nullable: true);

        // Create indexes for performance
        migrationBuilder.CreateIndex(
            name: "IX_Bookings_Status_CheckInDate",
            table: "Bookings",
            columns: new[] { "Status", "CheckInDate" });

        // Seed default data
        migrationBuilder.Sql(@"
            UPDATE Bookings 
            SET CancellationReason = 'Legacy cancellation' 
            WHERE Status = 'CANCELLED' AND CancellationReason IS NULL
        ");
    }

    protected override void Down(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.DropColumn(name: "CancellationReason", table: "Bookings");
        migrationBuilder.DropColumn(name: "CancelledAt", table: "Bookings");
        migrationBuilder.DropIndex(name: "IX_Bookings_Status_CheckInDate", table: "Bookings");
    }
}
```

**Data Versioning Strategy:**
- **Backward Compatibility:** All schema changes maintain backward compatibility for 2 versions
- **Blue-Green Deployments:** Database changes deployed before application changes
- **Feature Flags:** New data features controlled by feature flags
- **Migration Rollback:** All migrations include rollback procedures

---

## 6. Integration Architecture

### 6.1 External System Integrations

**Integration Overview:**
```
┌─────────────────────────────────────────────────────────────────┐
│                    HOTEL BOOKING SYSTEM                        │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                     INTEGRATION LAYER                          │
├─────────────────┬─────────────────┬─────────────────────────────┤
│  Payment APIs   │  Communication  │    External Data            │
│                 │  Services       │    Sources                  │
├─────────────────┼─────────────────┼─────────────────────────────┤
│ • Stripe        │ • SendGrid      │ • Google Maps               │
│ • PayPal        │ • Twilio        │ • Weather API               │
│ • Adyen         │ • Azure         │ • Currency Exchange         │
│ • Local Banks   │   Notification  │ • Local Attractions         │
│                 │   Hubs          │ • Transport APIs            │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

**Payment Gateway Integration:**
```csharp
public interface IPaymentGateway
{
    Task<PaymentResult> ProcessPaymentAsync(PaymentRequest request);
    Task<RefundResult> ProcessRefundAsync(RefundRequest request);
    Task<PaymentStatus> GetPaymentStatusAsync(string transactionId);
    Task<WebhookResult> ProcessWebhookAsync(string payload, string signature);
}

// Stripe Implementation
public class StripePaymentGateway : IPaymentGateway
{
    private readonly StripeClient _stripeClient;
    private readonly ILogger<StripePaymentGateway> _logger;

    public async Task<PaymentResult> ProcessPaymentAsync(PaymentRequest request)
    {
        try
        {
            var options = new PaymentIntentCreateOptions
            {
                Amount = (long)(request.Amount * 100), // Convert to cents
                Currency = request.Currency.ToLower(),
                PaymentMethod = request.PaymentMethodId,
                ConfirmationMethod = "manual",
                Confirm = true,
                Metadata = new Dictionary<string, string>
                {
                    ["booking_id"] = request.BookingId.ToString(),
                    ["user_id"] = request.UserId.ToString()
                }
            };

            var service = new PaymentIntentService(_stripeClient);
            var paymentIntent = await service.CreateAsync(options);

            return new PaymentResult
            {
                Success = paymentIntent.Status == "succeeded",
                TransactionId = paymentIntent.Id,
                Status = MapStripeStatus(paymentIntent.Status),
                Message = paymentIntent.Status
            };
        }
        catch (StripeException ex)
        {
            _logger.LogError(ex, "Stripe payment failed for booking {BookingId}", 
                request.BookingId);
            
            return new PaymentResult
            {
                Success = false,
                ErrorCode = ex.StripeError.Code,
                Message = ex.Message
            };
        }
    }
}

// PayPal Implementation
public class PayPalPaymentGateway : IPaymentGateway
{
    private readonly PayPalHttpClient _payPalClient;
    
    public async Task<PaymentResult> ProcessPaymentAsync(PaymentRequest request)
    {
        var orderRequest = new OrdersCreateRequest();
        orderRequest.Prefer("return=representation");
        orderRequest.RequestBody(new OrderRequest()
        {
            CheckoutPaymentIntent = "CAPTURE",
            PurchaseUnits = new List<PurchaseUnitRequest>()
            {
                new PurchaseUnitRequest()
                {
                    AmountWithBreakdown = new AmountWithBreakdown()
                    {
                        CurrencyCode = request.Currency,
                        Value = request.Amount.ToString("F2")
                    },
                    ReferenceId = request.BookingId.ToString()
                }
            }
        });

        var response = await _payPalClient.Execute(orderRequest);
        var order = response.Result<Order>();

        return new PaymentResult
        {
            Success = order.Status == "APPROVED",
            TransactionId = order.Id,
            Status = MapPayPalStatus(order.Status)
        };
    }
}
```

### 6.2 API Integration Patterns

**Circuit Breaker Pattern:**
```csharp
public class CircuitBreakerService<T> : ICircuitBreakerService<T>
{
    private readonly CircuitBreakerPolicy _circuitBreaker;
    private readonly ILogger<CircuitBreakerService<T>> _logger;

    public CircuitBreakerService(ILogger<CircuitBreakerService<T>> logger)
    {
        _logger = logger;
        _circuitBreaker = Policy
            .Handle<HttpRequestException>()
            .Or<TaskCanceledException>()
            .CircuitBreakerAsync(
                handledEventsAllowedBeforeBreaking: 5,
                durationOfBreak: TimeSpan.FromSeconds(30),
                onBreak: OnBreak,
                onReset: OnReset);
    }

    public async Task<T> ExecuteAsync(Func<Task<T>> operation)
    {
        return await _circuitBreaker.ExecuteAsync(operation);
    }

    private void OnBreak(Exception exception, TimeSpan duration)
    {
        _logger.LogWarning("Circuit breaker opened for {Duration} seconds due to {Exception}",
            duration.TotalSeconds, exception.GetType().Name);
    }

    private void OnReset()
    {
        _logger.LogInformation("Circuit breaker closed - service recovered");
    }
}
```

**Retry Pattern with Exponential Backoff:**
```csharp
public class ExternalApiService : IExternalApiService
{
    private readonly HttpClient _httpClient;
    private readonly IAsyncPolicy<HttpResponseMessage> _retryPolicy;

    public ExternalApiService(HttpClient httpClient)
    {
        _httpClient = httpClient;
        _retryPolicy = Policy
            .HandleResult<HttpResponseMessage>(r => !r.IsSuccessStatusCode)
            .Or<HttpRequestException>()
            .WaitAndRetryAsync(
                retryCount: 3,
                sleepDurationProvider: retryAttempt => 
                    TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)),
                onRetry: (outcome, timespan, retryCount, context) =>
                {
                    var logger = context.GetLogger();
                    logger?.LogWarning("Retry {RetryCount} after {Delay}ms", 
                        retryCount, timespan.TotalMilliseconds);
                });
    }

    public async Task<T> GetAsync<T>(string endpoint)
    {
        var response = await _retryPolicy.ExecuteAsync(async () =>
        {
            return await _httpClient.GetAsync(endpoint);
        });

        response.EnsureSuccessStatusCode();
        var json = await response.Content.ReadAsStringAsync();
        return JsonSerializer.Deserialize<T>(json);
    }
}
```

### 6.3 Message Queue Architecture

**Azure Service Bus Configuration:**
```csharp
public class ServiceBusConfiguration
{
    public string ConnectionString { get; set; }
    public Dictionary<string, TopicConfiguration> Topics { get; set; }
    public Dictionary<string, QueueConfiguration> Queues { get; set; }
}

public class TopicConfiguration
{
    public string Name { get; set; }
    public List<SubscriptionConfiguration> Subscriptions { get; set; }
    public TimeSpan DefaultMessageTimeToLive { get; set; } = TimeSpan.FromDays(14);
    public bool EnablePartitioning { get; set; } = true;
}

public class MessagePublisher : IMessagePublisher
{
    private readonly ServiceBusSender _sender;
    private readonly ILogger<MessagePublisher> _logger;

    public async Task PublishAsync<T>(T message, string subject = null) where T : class
    {
        var messageBody = JsonSerializer.Serialize(message);
        var serviceBusMessage = new ServiceBusMessage(messageBody)
        {
            Subject = subject ?? typeof(T).Name,
            MessageId = Guid.NewGuid().ToString(),
            ContentType = "application/json",
            TimeToLive = TimeSpan.FromDays(7)
        };

        // Add custom properties
        serviceBusMessage.ApplicationProperties["MessageType"] = typeof(T).FullName;
        serviceBusMessage.ApplicationProperties["PublishedAt"] = DateTimeOffset.UtcNow;

        await _sender.SendMessageAsync(serviceBusMessage);
        
        _logger.LogInformation("Published message {MessageId} of type {MessageType}",
            serviceBusMessage.MessageId, typeof(T).Name);
    }
}

public class MessageSubscriber : IMessageSubscriber
{
    private readonly ServiceBusProcessor _processor;
    private readonly IServiceProvider _serviceProvider;
    private readonly ILogger<MessageSubscriber> _logger;

    public async Task StartAsync(CancellationToken cancellationToken)
    {
        _processor.ProcessMessageAsync += ProcessMessageAsync;
        _processor.ProcessErrorAsync += ProcessErrorAsync;
        
        await _processor.StartProcessingAsync(cancellationToken);
        _logger.LogInformation("Message subscriber started");
    }

    private async Task ProcessMessageAsync(ProcessMessageEventArgs args)
    {
        try
        {
            var messageType = args.Message.ApplicationProperties["MessageType"].ToString();
            var handlerType = typeof(IMessageHandler<>).MakeGenericType(Type.GetType(messageType));
            
            using var scope = _serviceProvider.CreateScope();
            var handler = scope.ServiceProvider.GetService(handlerType);
            
            if (handler != null)
            {
                await ((dynamic)handler).HandleAsync((dynamic)DeserializeMessage(args.Message));
                await args.CompleteMessageAsync(args.Message);
            }
            else
            {
                _logger.LogWarning("No handler found for message type {MessageType}", messageType);
                await args.DeadLetterMessageAsync(args.Message, "NoHandlerFound");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing message {MessageId}", args.Message.MessageId);
            await args.AbandonMessageAsync(args.Message);
        }
    }
}
```

### 6.4 Webhook Implementation

**Webhook Endpoint for Payment Notifications:**
```csharp
[ApiController]
[Route("api/webhooks")]
public class WebhookController : ControllerBase
{
    private readonly IPaymentWebhookService _webhookService;
    private readonly ILogger<WebhookController> _logger;

    [HttpPost("stripe")]
    public async Task<IActionResult> StripeWebhook()
    {
        try
        {
            var json = await new StreamReader(HttpContext.Request.Body).ReadToEndAsync();
            var signature = Request.Headers["Stripe-Signature"];
            
            var webhookEvent = EventUtility.ConstructEvent(
                json, signature, _stripeWebhookSecret);

            await _webhookService.ProcessStripeWebhookAsync(webhookEvent);
            
            return Ok();
        }
        catch (StripeException ex)
        {
            _logger.LogError(ex, "Stripe webhook validation failed");
            return BadRequest();
        }
    }

    [HttpPost("paypal")]
    public async Task<IActionResult> PayPalWebhook()
    {
        try
        {
            var json = await new StreamReader(HttpContext.Request.Body).ReadToEndAsync();
            var headers = Request.Headers.ToDictionary(h => h.Key, h => h.Value.ToString());
            
            var isValid = await _webhookService.ValidatePayPalWebhookAsync(json, headers);
            if (!isValid)
            {
                return BadRequest("Invalid webhook signature");
            }

            await _webhookService.ProcessPayPalWebhookAsync(json);
            return Ok();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "PayPal webhook processing failed");
            return StatusCode(500);
        }
    }
}

public class PaymentWebhookService : IPaymentWebhookService
{
    private readonly IBookingService _bookingService;
    private readonly IPaymentService _paymentService;
    private readonly INotificationService _notificationService;

    public async Task ProcessStripeWebhookAsync(Event stripeEvent)
    {
        switch (stripeEvent.Type)
        {
            case "payment_intent.succeeded":
                var paymentIntent = stripeEvent.Data.Object as PaymentIntent;
                var bookingId = Guid.Parse(paymentIntent.Metadata["booking_id"]);
                
                await _paymentService.ConfirmPaymentAsync(bookingId, paymentIntent.Id);
                await _bookingService.ConfirmBookingAsync(bookingId);
                await _notificationService.SendBookingConfirmationAsync(bookingId);
                break;

            case "payment_intent.payment_failed":
                var failedIntent = stripeEvent.Data.Object as PaymentIntent;
                var failedBookingId = Guid.Parse(failedIntent.Metadata["booking_id"]);
                
                await _paymentService.MarkPaymentFailedAsync(failedBookingId, 
                    failedIntent.LastPaymentError?.Message);
                await _notificationService.SendPaymentFailedNotificationAsync(failedBookingId);
                break;
        }
    }
}
```

---

## 7. Security Architecture

### 7.1 Authentication & Authorization

**Azure Active Directory B2C Integration:**
```
┌─────────────────┐    OAuth 2.0   ┌─────────────────┐    JWT Token   ┌─────────────────┐
│   Client App    │─────────────→│   Azure AD B2C  │─────────────→│   API Gateway   │
│  (React SPA)    │   PKCE Flow   │                 │   Validation  │   (APIM)        │
└─────────────────┘               └─────────────────┘               └─────────────────┘
                                           │                                │
                                           ▼                                ▼
┌─────────────────┐               ┌─────────────────┐               ┌─────────────────┐
│   Identity      │               │   User Store    │               │   Microservice  │
│   Providers     │               │   (Azure AD)    │               │   (Role-based)  │
│ (Google, FB)    │               └─────────────────┘               └─────────────────┘
└─────────────────┘
```

**JWT Token Implementation:**
```csharp
public class JwtService : IJwtService
{
    private readonly JwtSettings _jwtSettings;
    private readonly ILogger<JwtService> _logger;

    public string GenerateToken(User user, IList<string> roles)
    {
        var tokenHandler = new JwtSecurityTokenHandler();
        var key = Encoding.ASCII.GetBytes(_jwtSettings.SecretKey);
        
        var claims = new List<Claim>
        {
            new Claim(ClaimTypes.NameIdentifier, user.UserId.ToString()),
            new Claim(ClaimTypes.Email, user.Email),
            new Claim(ClaimTypes.GivenName, user.FirstName),
            new Claim(ClaimTypes.Surname, user.LastName),
            new Claim("preferred_language", user.PreferredLanguage),
            new Claim("preferred_currency", user.PreferredCurrency)
        };

        // Add role claims
        foreach (var role in roles)
        {
            claims.Add(new Claim(ClaimTypes.Role, role));
        }

        var tokenDescriptor = new SecurityTokenDescriptor
        {
            Subject = new ClaimsIdentity(claims),
            Expires = DateTime.UtcNow.AddHours(_jwtSettings.ExpirationHours),
            SigningCredentials = new SigningCredentials(
                new SymmetricSecurityKey(key), 
                SecurityAlgorithms.HmacSha256Signature),
            Issuer = _jwtSettings.Issuer,
            Audience = _jwtSettings.Audience
        };

        var token = tokenHandler.CreateToken(tokenDescriptor);
        return tokenHandler.WriteToken(token);
    }

    public ClaimsPrincipal ValidateToken(string token)
    {
        var tokenHandler = new JwtSecurityTokenHandler();
        var key = Encoding.ASCII.GetBytes(_jwtSettings.SecretKey);

        try
        {
            var principal = tokenHandler.ValidateToken(token, new TokenValidationParameters
            {
                ValidateIssuerSigningKey = true,
                IssuerSigningKey = new SymmetricSecurityKey(key),
                ValidateIssuer = true,
                ValidIssuer = _jwtSettings.Issuer,
                ValidateAudience = true,
                ValidAudience = _jwtSettings.Audience,
                ValidateLifetime = true,
                ClockSkew = TimeSpan.Zero
            }, out SecurityToken validatedToken);

            return principal;
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Token validation failed");
            return null;
        }
    }
}

// Role-based Authorization
[Authorize(Roles = "Guest,HotelManager")]
public class BookingController : ControllerBase
{
    [HttpGet("{id}")]
    [Authorize(Policy = "BookingAccess")]
    public async Task<ActionResult<BookingDto>> GetBooking(Guid id)
    {
        var userId = GetCurrentUserId();
        var userRoles = GetCurrentUserRoles();
        
        // Guests can only access their own bookings
        if (userRoles.Contains("Guest"))
        {
            var booking = await _bookingService.GetUserBookingAsync(userId, id);
            return Ok(booking);
        }
        
        // Hotel managers can access bookings for their properties
        if (userRoles.Contains("HotelManager"))
        {
            var booking = await _bookingService.GetHotelBookingAsync(userId, id);
            return Ok(booking);
        }
        
        return Forbid();
    }
}

// Custom Authorization Policy
public class BookingAccessRequirement : IAuthorizationRequirement
{
    public string BookingId { get; set; }
}

public class BookingAccessHandler : AuthorizationHandler<BookingAccessRequirement>
{
    private readonly IBookingService _bookingService;

    protected override async Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        BookingAccessRequirement requirement)
    {
        var userId = Guid.Parse(context.User.FindFirst(ClaimTypes.NameIdentifier)?.Value);
        var roles = context.User.FindAll(ClaimTypes.Role).Select(c => c.Value);

        if (roles.Contains("Admin"))
        {
            context.Succeed(requirement);
            return;
        }

        var hasAccess = await _bookingService.UserHasAccessToBookingAsync(
            userId, Guid.Parse(requirement.BookingId));
            
        if (hasAccess)
        {
            context.Succeed(requirement);
        }
    }
}
```

### 7.2 Data Encryption

**Encryption at Rest:**
```csharp
public class EncryptionService : IEncryptionService
{
    private readonly byte[] _encryptionKey;
    private readonly ILogger<EncryptionService> _logger;

    public EncryptionService(IConfiguration configuration, ILogger<EncryptionService> logger)
    {
        _encryptionKey = Convert.FromBase64String(configuration["Encryption:Key"]);
        _logger = logger;
    }

    public string Encrypt(string plainText)
    {
        if (string.IsNullOrEmpty(plainText))
            return plainText;

        using var aes = Aes.Create();
        aes.Key = _encryptionKey;
        aes.GenerateIV();

        using var encryptor = aes.CreateEncryptor(aes.Key, aes.IV);
        using var msEncrypt = new MemoryStream();
        using var csEncrypt = new CryptoStream(msEncrypt, encryptor, CryptoStreamMode.Write);
        using var swEncrypt = new StreamWriter(csEncrypt);

        swEncrypt.Write(plainText);
        csEncrypt.FlushFinalBlock();

        var encrypted = aes.IV.Concat(msEncrypt.ToArray()).ToArray();
        return Convert.ToBase64String(encrypted);
    }

    public string Decrypt(string cipherText)
    {
        if (string.IsNullOrEmpty(cipherText))
            return cipherText;

        var cipherBytes = Convert.FromBase64String(cipherText);
        
        using var aes = Aes.Create();
        aes.Key = _encryptionKey;
        
        var iv = cipherBytes.Take(16).ToArray();
        var encrypted = cipherBytes.Skip(16).ToArray();
        
        aes.IV = iv;

        using var decryptor = aes.CreateDecryptor(aes.Key, aes.IV);
        using var msDecrypt = new MemoryStream(encrypted);
        using var csDecrypt = new CryptoStream(msDecrypt, decryptor, CryptoStreamMode.Read);
        using var srDecrypt = new StreamReader(csDecrypt);

        return srDecrypt.ReadToEnd();
    }
}

// Entity Framework Encryption Converter
public class EncryptedStringConverter : ValueConverter<string, string>
{
    public EncryptedStringConverter(IEncryptionService encryptionService) 
        : base(
            v => encryptionService.Encrypt(v),
            v => encryptionService.Decrypt(v))
    {
    }
}

// Usage in Entity Configuration
public class UserConfiguration : IEntityTypeConfiguration<User>
{
    private readonly IEncryptionService _encryptionService;

    public void Configure(EntityTypeBuilder<User> builder)
    {
        builder.Property(e => e.PhoneNumber)
            .HasConversion(new EncryptedStringConverter(_encryptionService));
            
        builder.Property(e => e.DateOfBirth)
            .HasConversion(new EncryptedDateConverter(_encryptionService));
    }
}
```

**PCI DSS Compliance for Payment Data:**
```csharp
public class PaymentSecurityService : IPaymentSecurityService
{
    public string TokenizeCardNumber(string cardNumber)
    {
        // Never store actual card numbers - use tokenization
        var token = GenerateSecureToken();
        
        // Store token mapping in secure PCI-compliant vault
        // This would typically be handled by payment processor
        
        return token;
    }

    public bool ValidateCardNumber(string cardNumber)
    {
        // Luhn algorithm validation
        return IsValidLuhn(cardNumber.Replace(" ", "").Replace("-", ""));
    }

    public string MaskCardNumber(string cardNumber)
    {
        if (string.IsNullOrEmpty(cardNumber) || cardNumber.Length < 4)
            return "****";
            
        return $"**** **** **** {cardNumber.Substring(cardNumber.Length - 4)}";
    }

    private bool IsValidLuhn(string cardNumber)
    {
        int sum = 0;
        bool alternate = false;
        
        for (int i = cardNumber.Length - 1; i >= 0; i--)
        {
            if (!char.IsDigit(cardNumber[i]))
                return false;
                
            int n = int.Parse(cardNumber[i].ToString());
            
            if (alternate)
            {
                n *= 2;
                if (n > 9) n = (n % 10) + 1;
            }
            
            sum += n;
            alternate = !alternate;
        }
        
        return (sum % 10 == 0);
    }
}
```

### 7.3 Network Security

**Azure Network Security Configuration:**
```yaml
# Azure Bicep template for network security
param location string = resourceGroup().location
param vnetName string = 'hbs-vnet'
param subnetName string = 'hbs-subnet'

resource virtualNetwork 'Microsoft.Network/virtualNetworks@2023-05-01' = {
  name: vnetName
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: ['10.0.0.0/16']
    }
    subnets: [
      {
        name: subnetName
        properties: {
          addressPrefix: '10.0.1.0/24'
          networkSecurityGroup: {
            id: networkSecurityGroup.id
          }
          serviceEndpoints: [
            {
              service: 'Microsoft.Sql'
            }
            {
              service: 'Microsoft.Storage'
            }
            {
              service: 'Microsoft.KeyVault'
            }
          ]
        }
      }
    ]
  }
}

resource networkSecurityGroup 'Microsoft.Network/networkSecurityGroups@2023-05-01' = {
  name: '${vnetName}-nsg'
  location: location
  properties: {
    securityRules: [
      {
        name: 'AllowHTTPS'
        properties: {
          priority: 1000
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '443'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
        }
      }
      {
        name: 'DenyAll'
        properties: {
          priority: 4000
          direction: 'Inbound'
          access: 'Deny'
          protocol: '*'
          sourcePortRange: '*'
          destinationPortRange: '*'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
        }
      }
    ]
  }
}

resource applicationGateway 'Microsoft.Network/applicationGateways@2023-05-01' = {
  name: 'hbs-appgw'
  location: location
  properties: {
    sku: {
      name: 'WAF_v2'
      tier: 'WAF_v2'
      capacity: 2
    }
    webApplicationFirewallConfiguration: {
      enabled: true
      firewallMode: 'Prevention'
      ruleSetType: 'OWASP'
      ruleSetVersion: '3.2'
      requestBodyCheck: true
      maxRequestBodySizeInKb: 128
    }
  }
}
```

**API Rate Limiting and DDoS Protection:**
```csharp
public class RateLimitingMiddleware
{
    private readonly RequestDelegate _next;
    private readonly IMemoryCache _cache;
    private readonly RateLimitOptions _options;

    public async Task InvokeAsync(HttpContext context)
    {
        var clientId = GetClientIdentifier(context);
        var key = $"rate_limit:{clientId}";
        
        var requestCount = _cache.Get<int>(key);
        
        if (requestCount >= _options.MaxRequests)
        {
            context.Response.StatusCode = 429; // Too Many Requests
            await context.Response.WriteAsync("Rate limit exceeded");
            return;
        }
        
        _cache.Set(key, requestCount + 1, _options.TimeWindow);
        
        await _next(context);
    }

    private string GetClientIdentifier(HttpContext context)
    {
        // Use user ID if authenticated, otherwise IP address
        var userId = context.User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        return userId ?? context.Connection.RemoteIpAddress?.ToString() ?? "unknown";
    }
}

// Azure Front Door DDoS Protection
public class SecurityHeadersMiddleware
{
    private readonly RequestDelegate _next;

    public async Task InvokeAsync(HttpContext context)
    {
        // Add security headers
        context.Response.Headers.Add("X-Content-Type-Options", "nosniff");
        context.Response.Headers.Add("X-Frame-Options", "DENY");
        context.Response.Headers.Add("X-XSS-Protection", "1; mode=block");
        context.Response.Headers.Add("Referrer-Policy", "strict-origin-when-cross-origin");
        context.Response.Headers.Add("Content-Security-Policy", 
            "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'");
        
        // HSTS for HTTPS
        if (context.Request.IsHttps)
        {
            context.Response.Headers.Add("Strict-Transport-Security", 
                "max-age=31536000; includeSubDomains");
        }

        await _next(context);
    }
}
```

### 7.4 Security Monitoring

**Azure Security Center Integration:**
```csharp
public class SecurityEventService : ISecurityEventService
{
    private readonly ILogger<SecurityEventService> _logger;
    private readonly TelemetryClient _telemetryClient;

    public async Task LogSecurityEventAsync(SecurityEvent securityEvent)
    {
        // Log to Application Insights
        _telemetryClient.TrackEvent("SecurityEvent", new Dictionary<string, string>
        {
            ["EventType"] = securityEvent.EventType,
            ["Severity"] = securityEvent.Severity.ToString(),
            ["UserId"] = securityEvent.UserId?.ToString(),
            ["IPAddress"] = securityEvent.IPAddress,
            ["UserAgent"] = securityEvent.UserAgent,
            ["Description"] = securityEvent.Description
        });

        // Log suspicious activities
        if (securityEvent.Severity >= SecuritySeverity.High)
        {
            _logger.LogWarning("High severity security event: {EventType} from {IPAddress}", 
                securityEvent.EventType, securityEvent.IPAddress);
            
            // Send alert to security team
            await SendSecurityAlertAsync(securityEvent);
        }

        // Store in security audit log
        await StoreSecurityEventAsync(securityEvent);
    }

    public async Task<bool> DetectAnomalousActivityAsync(Guid userId, string activity)
    {
        // Machine learning-based anomaly detection
        var userProfile = await GetUserActivityProfileAsync(userId);
        var isAnomalous = await AnalyzeActivityPatternAsync(userProfile, activity);
        
        if (isAnomalous)
        {
            await LogSecurityEventAsync(new SecurityEvent
            {
                EventType = "AnomalousActivity",
                Severity = SecuritySeverity.Medium,
                UserId = userId,
                Description = $"Unusual activity detected: {activity}"
            });
        }
        
        return isAnomalous;
    }
}

// Real-time fraud detection
public class FraudDetectionService : IFraudDetectionService
{
    public async Task<FraudRisk> AssessBookingRiskAsync(BookingRequest booking)
    {
        var riskFactors = new List<RiskFactor>();
        
        // Check for rapid successive bookings
        var recentBookings = await GetRecentBookingsAsync(booking.UserId, TimeSpan.FromHours(1));
        if (recentBookings.Count > 5)
        {
            riskFactors.Add(new RiskFactor("RapidBookings", 0.7m));
        }
        
        // Check for unusual location patterns
        var userLocation = await GetUserLocationHistoryAsync(booking.UserId);
        if (IsUnusualLocation(userLocation, booking.HotelLocation))
        {
            riskFactors.Add(new RiskFactor("UnusualLocation", 0.5m));
        }
        
        // Check payment method history
        if (await IsNewPaymentMethodAsync(booking.UserId, booking.PaymentMethodId))
        {
            riskFactors.Add(new RiskFactor("NewPaymentMethod", 0.3m));
        }
        
        var totalRisk = riskFactors.Sum(r => r.Weight);
        
        return new FraudRisk
        {
            Score = totalRisk,
            Level = GetRiskLevel(totalRisk),
            Factors = riskFactors,
            RequiresManualReview = totalRisk > 0.8m
        };
    }
}
```

---

## 8. Performance & Scalability

### 8.1 Performance Optimization

**Database Query Optimization:**
```csharp
public class OptimizedHotelRepository : IHotelRepository
{
    private readonly HotelBookingContext _context;

    public async Task<IEnumerable<Hotel>> SearchHotelsAsync(SearchCriteria criteria)
    {
        var query = _context.Hotels
            .AsNoTracking() // Read-only query optimization
            .Include(h => h.RoomTypes.Where(rt => rt.IsActive))
            .ThenInclude(rt => rt.RoomRates.Where(rr => 
                rr.Date >= criteria.CheckIn && rr.Date < criteria.CheckOut))
            .Where(h => h.IsActive);

        // Spatial query for location-based search
        if (criteria.Latitude.HasValue && criteria.Longitude.HasValue)
        {
            query = query.Where(h => 
                h.Location.Distance(new Point(criteria.Longitude.Value, criteria.Latitude.Value)) 
                <= criteria.RadiusKm * 1000);
        }

        // Apply filters with indexes
        if (!string.IsNullOrEmpty(criteria.City))
        {
            query = query.Where(h => h.City == criteria.City);
        }

        if (criteria.StarRating.HasValue)
        {
            query = query.Where(h => h.StarRating >= criteria.StarRating.Value);
        }

        // Compiled query for better performance
        var compiledQuery = EF.CompileAsyncQuery(
            (HotelBookingContext ctx, SearchCriteria c) => 
                query.OrderBy(h => h.Name)
                     .Skip(c.Page * c.PageSize)
                     .Take(c.PageSize));

        return await compiledQuery(_context, criteria);
    }

    // Bulk operations for better performance
    public async Task UpdateInventoryBulkAsync(List<InventoryUpdate> updates)
    {
        var sql = @"
            UPDATE RoomInventory 
            SET AvailableRooms = @AvailableRooms, 
                UpdatedAt = GETUTCDATE()
            WHERE RoomTypeId = @RoomTypeId AND Date = @Date";

        await _context.Database.ExecuteSqlRawAsync(sql, updates.ToArray());
    }
}

// Response caching with invalidation
public class CachedHotelService : IHotelService
{
    private readonly IHotelService _hotelService;
    private readonly IDistributedCache _cache;
    private readonly ICacheInvalidationService _cacheInvalidation;

    [CacheOutput(Duration = 300)] // 5 minutes cache
    public async Task<SearchResult> SearchHotelsAsync(SearchRequest request)
    {
        var cacheKey = GenerateCacheKey(request);
        var cachedResult = await _cache.GetAsync<SearchResult>(cacheKey);
        
        if (cachedResult != null)
        {
            return cachedResult;
        }

        var result = await _hotelService.SearchHotelsAsync(request);
        
        await _cache.SetAsync(cacheKey, result, TimeSpan.FromMinutes(5));
        await _cacheInvalidation.RegisterCacheKeyAsync(cacheKey, "hotel-search");
        
        return result;
    }

    // Cache invalidation on data changes
    public async Task UpdateHotelAsync(Hotel hotel)
    {
        await _hotelService.UpdateHotelAsync(hotel);
        await _cacheInvalidation.InvalidateByTagAsync("hotel-search");
    }
}
```

**CDN and Static Asset Optimization:**
```csharp
public class AssetOptimizationService : IAssetOptimizationService
{
    private readonly IBlobStorageService _blobStorage;
    private readonly ICdnService _cdnService;

    public async Task<string> OptimizeAndUploadImageAsync(
        IFormFile image, ImageOptimizationOptions options)
    {
        using var originalStream = image.OpenReadStream();
        
        // Optimize image
        var optimizedImages = new Dictionary<string, byte[]>();
        
        foreach (var size in options.Sizes)
        {
            using var resizedImage = await ResizeImageAsync(originalStream, size);
            optimizedImages[size.Name] = resizedImage.ToArray();
        }

        // Upload to blob storage with different sizes
        var urls = new Dictionary<string, string>();
        foreach (var optimizedImage in optimizedImages)
        {
            var blobName = $"{options.FileName}_{optimizedImage.Key}.webp";
            var url = await _blobStorage.UploadAsync(blobName, optimizedImage.Value, "image/webp");
            urls[optimizedImage.Key] = url;
        }

        // Purge CDN cache for updated images
        await _cdnService.PurgeAsync($"{options.FileName}*");

        return urls["original"];
    }

    public string GenerateResponsiveImageHtml(Dictionary<string, string> imageUrls, string alt)
    {
        var srcSet = string.Join(", ", 
            imageUrls.Select(kvp => $"{kvp.Value} {GetWidthFromSize(kvp.Key)}w"));
            
        return $@"
            <picture>
                <source srcset=""{srcSet}"" type=""image/webp"">
                <img src=""{imageUrls["medium"]}"" alt=""{alt}"" loading=""lazy"">
            </picture>";
    }
}
```

### 8.2 Scalability Strategy

**Horizontal Scaling with Kubernetes:**
```yaml
# Deployment configuration for hotel search service
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hotel-search-service
  labels:
    app: hotel-search-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: hotel-search-service
  template:
    metadata:
      labels:
        app: hotel-search-service
    spec:
      containers:
      - name: hotel-search-service
        image: hbsacr.azurecr.io/hotel-search-service:latest
        ports:
        - containerPort: 80
        env:
        - name: ASPNETCORE_ENVIRONMENT
          value: "Production"
        - name: ConnectionStrings__DefaultConnection
          valueFrom:
            secretKeyRef:
              name: database-secrets
              key: connection-string
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5

---
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: hotel-search-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: hotel-search-service
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Database Scaling Strategy:**
```csharp
// Read/Write splitting for database scalability
public class DatabaseConnectionFactory : IDatabaseConnectionFactory
{
    private readonly string _writeConnectionString;
    private readonly List<string> _readConnectionStrings;
    private readonly ILogger<DatabaseConnectionFactory> _logger;
    private int _readConnectionIndex = 0;

    public IDbConnection CreateWriteConnection()
    {
        return new SqlConnection(_writeConnectionString);
    }

    public IDbConnection CreateReadConnection()
    {
        // Round-robin load balancing for read replicas
        var connectionString = _readConnectionStrings[
            _readConnectionIndex % _readConnectionStrings.Count];
        _readConnectionIndex++;
        
        return new SqlConnection(connectionString);
    }
}

// CQRS with separate read/write models
public class BookingCommandService : IBookingCommandService
{
    private readonly IDatabaseConnectionFactory _connectionFactory;
    
    public async Task<Guid> CreateBookingAsync(CreateBookingCommand command)
    {
        using var connection = _connectionFactory.CreateWriteConnection();
        
        // Write operations go to primary database
        var booking = new Booking(command);
        await connection.ExecuteAsync(
            "INSERT INTO Bookings (...) VALUES (...)", booking);
            
        // Publish event for read model updates
        await _eventBus.PublishAsync(new BookingCreatedEvent(booking));
        
        return booking.Id;
    }
}

public class BookingQueryService : IBookingQueryService
{
    private readonly IDatabaseConnectionFactory _connectionFactory;
    
    public async Task<BookingDto> GetBookingAsync(Guid bookingId)
    {
        using var connection = _connectionFactory.CreateReadConnection();
        
        // Read operations go to read replicas
        return await connection.QuerySingleOrDefaultAsync<BookingDto>(
            "SELECT * FROM BookingReadModel WHERE BookingId = @BookingId",
            new { BookingId = bookingId });
    }
}
```

### 8.3 Load Balancing

**Azure Application Gateway Configuration:**
```bicep
resource applicationGateway 'Microsoft.Network/applicationGateways@2023-05-01' = {
  name: 'hbs-app-gateway'
  location: location
  properties: {
    sku: {
      name: 'Standard_v2'
      tier: 'Standard_v2'
      capacity: 2
    }
    gatewayIPConfigurations: [
      {
        name: 'appGatewayIpConfig'
        properties: {
          subnet: {
            id: subnet.id
          }
        }
      }
    ]
    frontendIPConfigurations: [
      {
        name: 'appGwPublicFrontendIp'
        properties: {
          privateIPAllocationMethod: 'Dynamic'
          publicIPAddress: {
            id: publicIP.id
          }
        }
      }
    ]
    frontendPorts: [
      {
        name: 'port_80'
        properties: {
          port: 80
        }
      }
      {
        name: 'port_443'
        properties: {
          port: 443
        }
      }
    ]
    backendAddressPools: [
      {
        name: 'api-backend-pool'
        properties: {
          backendAddresses: [
            {
              fqdn: 'hbs-api-service.default.svc.cluster.local'
            }
          ]
        }
      }
    ]
    backendHttpSettingsCollection: [
      {
        name: 'api-http-settings'
        properties: {
          port: 80
          protocol: 'Http'
          cookieBasedAffinity: 'Disabled'
          connectionDraining: {
            enabled: true
            drainTimeoutInSec: 60
          }
          requestTimeout: 30
          probe: {
            id: resourceId('Microsoft.Network/applicationGateways/probes', 
              'hbs-app-gateway', 'api-health-probe')
          }
        }
      }
    ]
    httpListeners: [
      {
        name: 'api-listener'
        properties: {
          frontendIPConfiguration: {
            id: resourceId('Microsoft.Network/applicationGateways/frontendIPConfigurations',
              'hbs-app-gateway', 'appGwPublicFrontendIp')
          }
          frontendPort: {
            id: resourceId('Microsoft.Network/applicationGateways/frontendPorts',
              'hbs-app-gateway', 'port_443')
          }
          protocol: 'Https'
          sslCertificate: {
            id: resourceId('Microsoft.Network/applicationGateways/sslCertificates',
              'hbs-app-gateway', 'ssl-cert')
          }
        }
      }
    ]
    requestRoutingRules: [
      {
        name: 'api-routing-rule'
        properties: {
          ruleType: 'Basic'
          httpListener: {
            id: resourceId('Microsoft.Network/applicationGateways/httpListeners',
              'hbs-app-gateway', 'api-listener')
          }
          backendAddressPool: {
            id: resourceId('Microsoft.Network/applicationGateways/backendAddressPools',
              'hbs-app-gateway', 'api-backend-pool')
          }
          backendHttpSettings: {
            id: resourceId('Microsoft.Network/applicationGateways/backendHttpSettingsCollection',
              'hbs-app-gateway', 'api-http-settings')
          }
        }
      }
    ]
    probes: [
      {
        name: 'api-health-probe'
        properties: {
          protocol: 'Http'
          path: '/health'
          interval: 30
          timeout: 30
          unhealthyThreshold: 3
          pickHostNameFromBackendHttpSettings: true
        }
      }
    ]
  }
}
```

### 8.4 Caching Mechanisms

**Multi-Level Caching Strategy:**
```csharp
public class MultiLevelCacheService : ICacheService
{
    private readonly IMemoryCache _l1Cache; // Level 1: In-memory
    private readonly IDistributedCache _l2Cache; // Level 2: Redis
    private readonly ICdnService _l3Cache; // Level 3: CDN
    private readonly ILogger<MultiLevelCacheService> _logger;

    public async Task<T> GetAsync<T>(string key, CacheLevel level = CacheLevel.All)
    {
        // Try L1 cache first (fastest)
        if (level.HasFlag(CacheLevel.Memory))
        {
            if (_l1Cache.TryGetValue(key, out T memoryValue))
            {
                _logger.LogDebug("L1 cache hit for key: {Key}", key);
                return memoryValue;
            }
        }

        // Try L2 cache (Redis)
        if (level.HasFlag(CacheLevel.Distributed))
        {
            var redisValue = await _l2Cache.GetAsync<T>(key);
            if (redisValue != null)
            {
                _logger.LogDebug("L2 cache hit for key: {Key}", key);
                
                // Populate L1 cache
                _l1Cache.Set(key, redisValue, TimeSpan.FromMinutes(5));
                return redisValue;
            }
        }

        return default(T);
    }

    public async Task SetAsync<T>(string key, T value, TimeSpan? expiry = null)
    {
        var cacheExpiry = expiry ?? TimeSpan.FromMinutes(15);
        
        // Set in L1 cache (shorter TTL)
        _l1Cache.Set(key, value, TimeSpan.FromMinutes(5));
        
        // Set in L2 cache (longer TTL)
        await _l2Cache.SetAsync(key, value, cacheExpiry);
        
        _logger.LogDebug("Cached value for key: {Key} with expiry: {Expiry}", 
            key, cacheExpiry);
    }

    public async Task InvalidateAsync(string key)
    {
        _l1Cache.Remove(key);
        await _l2Cache.RemoveAsync(key);
        
        _logger.LogDebug("Invalidated cache for key: {Key}", key);
    }
}

// Cache-aside pattern implementation
public class CachedHotelSearchService : IHotelSearchService
{
    private readonly IHotelSearchService _searchService;
    private readonly ICacheService _cacheService;

    public async Task<SearchResult> SearchAsync(SearchRequest request)
    {
        var cacheKey = $"search:{request.GetHashCode()}";
        
        // Try to get from cache
        var cachedResult = await _cacheService.GetAsync<SearchResult>(cacheKey);
        if (cachedResult != null)
        {
            return cachedResult;
        }

        // Get from data source
        var result = await _searchService.SearchAsync(request);
        
        // Cache the result
        await _cacheService.SetAsync(cacheKey, result, TimeSpan.FromMinutes(5));
        
        return result;
    }
}
```

---

## 9. Deployment Architecture

### 9.1 Environment Configuration

**Environment Strategy:**
```
┌─────────────────────────────────────────────────────────────────┐
│                        PRODUCTION                               │
│   • Multi-region deployment (East US, West Europe)             │
│   • Blue-Green deployment strategy                             │
│   • Auto-scaling enabled                                       │
│   • Full monitoring and alerting                               │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                         STAGING                                │
│   • Production-like environment                                │
│   • Performance and load testing                               │
│   • Integration testing with external services                 │
│   • User acceptance testing                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                       DEVELOPMENT                              │
│   • Feature development and testing                            │
│   • Individual developer environments                          │
│   • Unit and integration testing                               │
│   • Mock external services                                     │
└─────────────────────────────────────────────────────────────────┘
```

**Infrastructure as Code (Bicep):**
```bicep
@description('Environment name (dev, staging, prod)')
param environment string = 'dev'

@description('Azure region for deployment')
param location string = resourceGroup().location

@description('Application name prefix')
param appName string = 'hbs'

// Variables
var environmentConfig = {
  dev: {
    appServicePlan: 'B2'
    sqlDatabaseTier: 'Basic'
    redisCacheTier: 'C0'
    storageAccountType: 'Standard_LRS'
    autoscaleEnabled: false
  }
  staging: {
    appServicePlan: 'S2'
    sqlDatabaseTier: 'S2'
    redisCacheTier: 'C1'
    storageAccountType: 'Standard_GRS'
    autoscaleEnabled: true
  }
  prod: {
    appServicePlan: 'P2V2'
    sqlDatabaseTier: 'S4'
    redisCacheTier: 'C2'
    storageAccountType: 'Standard_RAGRS'
    autoscaleEnabled: true
  }
}

var config = environmentConfig[environment]

// Key Vault for secrets
resource keyVault 'Microsoft.KeyVault/vaults@2023-02-01' = {
  name: '${appName}-${environment}-kv'
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    accessPolicies: []
    enabledForDeployment: true
    enabledForTemplateDeployment: true
    enabledForDiskEncryption: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
  }
}

// Application Insights
resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${appName}-${environment}-ai'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    RetentionInDays: environment == 'prod' ? 90 : 30
    WorkspaceResourceId: logAnalyticsWorkspace.id
  }
}

// Log Analytics Workspace
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: '${appName}-${environment}-logs'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: environment == 'prod' ? 90 : 30
  }
}

// Container Registry
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: '${appName}${environment}acr'
  location: location
  sku: {
    name: environment == 'prod' ? 'Premium' : 'Basic'
  }
  properties: {
    adminUserEnabled: false
    networkRuleSet: {
      defaultAction: 'Allow'
    }
  }
}

// Azure Kubernetes Service
resource aksCluster 'Microsoft.ContainerService/managedClusters@2023-05-02-preview' = {
  name: '${appName}-${environment}-aks'
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    dnsPrefix: '${appName}-${environment}'
    agentPoolProfiles: [
      {
        name: 'system'
        count: environment == 'prod' ? 3 : 1
        vmSize: environment == 'prod' ? 'Standard_D4s_v3' : 'Standard_B2s'
        mode: 'System'
        enableAutoScaling: config.autoscaleEnabled
        minCount: config.autoscaleEnabled ? 1 : null
        maxCount: config.autoscaleEnabled ? 10 : null
      }
      {
        name: 'user'
        count: environment == 'prod' ? 5 : 2
        vmSize: environment == 'prod' ? 'Standard_D4s_v3' : 'Standard_B2s'
        mode: 'User'
        enableAutoScaling: config.autoscaleEnabled
        minCount: config.autoscaleEnabled ? 2 : null
        maxCount: config.autoscaleEnabled ? 20 : null
      }
    ]
    networkProfile: {
      networkPlugin: 'azure'
      serviceCidr: '10.0.0.0/16'
      dnsServiceIP: '10.0.0.10'
    }
    addonProfiles: {
      azureKeyvaultSecretsProvider: {
        enabled: true
      }
      omsAgent: {
        enabled: true
        config: {
          logAnalyticsWorkspaceResourceID: logAnalyticsWorkspace.id
        }
      }
    }
  }
}
```

### 9.2 Deployment Pipeline

**Azure DevOps Pipeline (YAML):**
```yaml
name: Hotel Booking System CI/CD

trigger:
  branches:
    include:
    - main
    - develop
  paths:
    include:
    - src/*
    - deployment/*

variables:
  - group: hbs-variables
  - name: buildConfiguration
    value: 'Release'
  - name: vmImageName
    value: 'ubuntu-latest'

stages:
- stage: Build
  displayName: Build and Test
  jobs:
  - job: BuildAndTest
    displayName: Build and Test Application
    pool:
      vmImage: $(vmImageName)
    
    steps:
    - task: UseDotNet@2
      displayName: 'Use .NET 8 SDK'
      inputs:
        packageType: 'sdk'
        version: '8.x'
        
    - task: DotNetCoreCLI@2
      displayName: 'Restore NuGet packages'
      inputs:
        command: 'restore'
        projects: '**/*.csproj'
        
    - task: DotNetCoreCLI@2
      displayName: 'Build solution'
      inputs:
        command: 'build'
        projects: '**/*.csproj'
        arguments: '--configuration $(buildConfiguration) --no-restore'
        
    - task: DotNetCoreCLI@2
      displayName: 'Run unit tests'
      inputs:
        command: 'test'
        projects: '**/*Tests/*.csproj'
        arguments: '--configuration $(buildConfiguration) --collect:"XPlat Code Coverage" --logger trx --results-directory $(Agent.TempDirectory)'
        
    - task: PublishTestResults@2
      displayName: 'Publish test results'
      inputs:
        testResultsFormat: 'VSTest'
        testResultsFiles: '$(Agent.TempDirectory)/**/*.trx'
        
    - task: PublishCodeCoverageResults@1
      displayName: 'Publish code coverage'
      inputs:
        codeCoverageTool: 'Cobertura'
        summaryFileLocation: '$(Agent.TempDirectory)/**/coverage.cobertura.xml'

- stage: SecurityScan
  displayName: Security Scanning
  dependsOn: Build
  jobs:
  - job: SecurityScan
    displayName: Run Security Scans
    pool:
      vmImage: $(vmImageName)
    
    steps:
    - task: SonarQubePrepare@5
      displayName: 'Prepare SonarQube analysis'
      inputs:
        SonarQube: 'SonarQube-Connection'
        scannerMode: 'MSBuild'
        projectKey: 'hotel-booking-system'
        
    - task: DotNetCoreCLI@2
      displayName: 'Build for SonarQube'
      inputs:
        command: 'build'
        projects: '**/*.csproj'
        
    - task: SonarQubeAnalyze@5
      displayName: 'Run SonarQube analysis'
      
    - task: SonarQubePublish@5
      displayName: 'Publish SonarQube results'

- stage: ContainerBuild
  displayName: Build and Push Container Images
  dependsOn: SecurityScan
  jobs:
  - job: BuildContainers
    displayName: Build and Push Docker Images
    pool:
      vmImage: $(vmImageName)
    
    steps:
    - task: Docker@2
      displayName: 'Build and push booking service image'
      inputs:
        containerRegistry: '$(containerRegistryServiceConnection)'
        repository: 'booking-service'
        command: 'buildAndPush'
        Dockerfile: 'src/BookingService/Dockerfile'
        tags: |
          $(Build.BuildId)
          latest
          
    - task: Docker@2
      displayName: 'Build and push search service image'
      inputs:
        containerRegistry: '$(containerRegistryServiceConnection)'
        repository: 'search-service'
        command: 'buildAndPush'
        Dockerfile: 'src/SearchService/Dockerfile'
        tags: |
          $(Build.BuildId)
          latest

- stage: DeployDev
  displayName: Deploy to Development
  dependsOn: ContainerBuild
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/develop'))
  jobs:
  - deployment: DeployToDev
    displayName: Deploy to Development Environment
    environment: 'hbs-dev'
    pool:
      vmImage: $(vmImageName)
    strategy:
      runOnce:
        deploy:
          steps:
          - task: HelmDeploy@0
            displayName: 'Deploy with Helm'
            inputs:
              connectionType: 'Azure Resource Manager'
              azureSubscription: '$(azureServiceConnection)'
              azureResourceGroup: '$(resourceGroupDev)'
              kubernetesCluster: '$(aksClusterDev)'
              command: 'upgrade'
              chartType: 'FilePath'
              chartPath: 'deployment/helm/hotel-booking-system'
              releaseName: 'hbs-dev'
              valueFile: 'deployment/helm/values-dev.yaml'
              arguments: '--set image.tag=$(Build.BuildId)'

- stage: DeployStaging
  displayName: Deploy to Staging
  dependsOn: ContainerBuild
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - deployment: DeployToStaging
    displayName: Deploy to Staging Environment
    environment: 'hbs-staging'
    pool:
      vmImage: $(vmImageName)
    strategy:
      runOnce:
        deploy:
          steps:
          - task: HelmDeploy@0
            displayName: 'Deploy with Helm'
            inputs:
              connectionType: 'Azure Resource Manager'
              azureSubscription: '$(azureServiceConnection)'
              azureResourceGroup: '$(resourceGroupStaging)'
              kubernetesCluster: '$(aksClusterStaging)'
              command: 'upgrade'
              chartType: 'FilePath'
              chartPath: 'deployment/helm/hotel-booking-system'
              releaseName: 'hbs-staging'
              valueFile: 'deployment/helm/values-staging.yaml'
              arguments: '--set image.tag=$(Build.BuildId)'

- stage: PerformanceTest
  displayName: Performance Testing
  dependsOn: DeployStaging
  jobs:
  - job: LoadTest
    displayName: Run Load Tests
    pool:
      vmImage: $(vmImageName)
    
    steps:
    - task: AzureLoadTest@1
      displayName: 'Run Azure Load Test'
      inputs:
        azureSubscription: '$(azureServiceConnection)'
        loadTestConfigFile: 'tests/performance/loadtest.yaml'
        resourceGroup: '$(resourceGroupStaging)'
        loadTestResource: '$(loadTestResource)'

- stage: DeployProduction
  displayName: Deploy to Production
  dependsOn: PerformanceTest
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - deployment: DeployToProduction
    displayName: Deploy to Production Environment
    environment: 'hbs-production'
    pool:
      vmImage: $(vmImageName)
    strategy:
      runOnce:
        deploy:
          steps:
          - task: HelmDeploy@0
            displayName: 'Deploy with Helm (Blue-Green)'
            inputs:
              connectionType: 'Azure Resource Manager'
              azureSubscription: '$(azureServiceConnection)'
              azureResourceGroup: '$(resourceGroupProduction)'
              kubernetesCluster: '$(aksClusterProduction)'
              command: 'upgrade'
              chartType: 'FilePath'
              chartPath: 'deployment/helm/hotel-booking-system'
              releaseName: 'hbs-prod-green'
              valueFile: 'deployment/helm/values-production.yaml'
              arguments: '--set image.tag=$(Build.BuildId) --set deployment.slot=green'
              
          - task: Kubernetes@1
            displayName: 'Switch traffic to Green deployment'
            inputs:
              connectionType: 'Azure Resource Manager'
              azureSubscription: '$(azureServiceConnection)'
              azureResourceGroup: '$(resourceGroupProduction)'
              kubernetesCluster: '$(aksClusterProduction)'
              command: 'apply'
              useConfigurationFile: true
              configuration: 'deployment/k8s/traffic-switch.yaml'
```

### 9.3 Container Orchestration

**Kubernetes Deployment Manifests:**
```yaml
# booking-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: booking-service
  labels:
    app: booking-service
    version: v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: booking-service
      version: v1
  template:
    metadata:
      labels:
        app: booking-service
        version: v1
    spec:
      serviceAccountName: booking-service-sa
      containers:
      - name: booking-service
        image: hbsprodacr.azurecr.io/booking-service:latest
        ports:
        - containerPort: 80
          name: http
        env:
        - name: ASPNETCORE_ENVIRONMENT
          value: "Production"
        - name: ConnectionStrings__DefaultConnection
          valueFrom:
            secretKeyRef:
              name: database-secrets
              key: connection-string
        - name: Redis__ConnectionString
          valueFrom:
            secretKeyRef:
              name: cache-secrets
              key: redis-connection-string
        - name: ApplicationInsights__InstrumentationKey
          valueFrom:
            secretKeyRef:
              name: monitoring-secrets
              key: appinsights-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        securityContext:
          allowPrivilegeEscalation: false
          runAsNonRoot: true
          runAsUser: 1000
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL

---
apiVersion: v1
kind: Service
metadata:
  name: booking-service
  labels:
    app: booking-service
spec:
  selector:
    app: booking-service
  ports:
  - port: 80
    targetPort: 80
    name: http
  type: ClusterIP

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: booking-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: booking-service
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60

---
# Network Policy for security
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: booking-service-netpol
spec:
  podSelector:
    matchLabels:
      app: booking-service
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: api-gateway
    ports:
    - protocol: TCP
      port: 80
  egress:
  - to: []
    ports:
    - protocol: TCP
      port: 1433 # SQL Server
    - protocol: TCP
      port: 6380 # Redis SSL
    - protocol: TCP
      port: 443  # HTTPS outbound
```

### 9.4 Blue-Green Deployment

**Blue-Green Deployment Strategy:**
```yaml
# Helm values for Blue-Green deployment
# values-production.yaml
replicaCount: 5

image:
  repository: hbsprodacr.azurecr.io/booking-service
  tag: "latest"
  pullPolicy: IfNotPresent

deployment:
  slot: blue  # Will be overridden to 'green' during deployment
  
service:
  type: ClusterIP
  port: 80

ingress:
  enabled: true
  className: "azure-application-gateway"
  annotations:
    appgw.ingress.kubernetes.io/ssl-redirect: "true"
    appgw.ingress.kubernetes.io/backend-protocol: "http"
  hosts:
    - host: api.hotelbooking.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: api-tls-secret
      hosts:
        - api.hotelbooking.com

# Traffic switching service
apiVersion: v1
kind: Service
metadata:
  name: booking-service-active
  labels:
    app: booking-service
spec:
  selector:
    app: booking-service
    slot: blue  # Initially points to blue
  ports:
  - port: 80
    targetPort: 80
    name: http
  type: ClusterIP
```

**Blue-Green Switch Script:**
```bash
#!/bin/bash
# blue-green-switch.sh

NAMESPACE="default"
SERVICE_NAME="booking-service-active"
CURRENT_SLOT=$(kubectl get service $SERVICE_NAME -o jsonpath='{.spec.selector.slot}')

if [ "$CURRENT_SLOT" = "blue" ]; then
    NEW_SLOT="green"
else
    NEW_SLOT="blue"
fi

echo "Current active slot: $CURRENT_SLOT"
echo "Switching to: $NEW_SLOT"

# Update service selector to point to new slot
kubectl patch service $SERVICE_NAME -p '{"spec":{"selector":{"slot":"'$NEW_SLOT'"}}}'

echo "Traffic switched to $NEW_SLOT slot"

# Verify the switch
sleep 10
kubectl get service $SERVICE_NAME -o jsonpath='{.spec.selector.slot}'
echo ""

# Optional: Scale down the old slot after verification
echo "Scaling down $CURRENT_SLOT slot..."
kubectl scale deployment booking-service-$CURRENT_SLOT --replicas=0
```

---

## 10. Monitoring & Observability

### 10.1 Application Monitoring

**Azure Application Insights Configuration:**
```csharp
public class Startup
{
    public void ConfigureServices(IServiceCollection services)
    {
        // Application Insights
        services.AddApplicationInsightsTelemetry(options =>
        {
            options.ConnectionString = Configuration.GetConnectionString("ApplicationInsights");
            options.EnableAdaptiveSampling = true;
            options.EnableQuickPulseMetricStream = true;
        });

        // Custom telemetry processors
        services.AddSingleton<ITelemetryProcessor, FilterOutHealthCheckTelemetryProcessor>();
        services.AddSingleton<ITelemetryProcessor, EnrichmentTelemetryProcessor>();
        
        // Health checks
        services.AddHealthChecks()
            .AddCheck<DatabaseHealthCheck>("database")
            .AddCheck<RedisHealthCheck>("redis")
            .AddCheck<ExternalApiHealthCheck>("payment-gateway")
            .AddApplicationInsightsPublisher();
    }

    public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
    {
        // Request tracking middleware
        app.UseMiddleware<RequestTrackingMiddleware>();
        
        // Health check endpoint
        app.UseHealthChecks("/health", new HealthCheckOptions
        {
            ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse,
            ResultStatusCodes =
            {
                [HealthStatus.Healthy] = StatusCodes.Status200OK,
                [HealthStatus.Degraded] = StatusCodes.Status200OK,
                [HealthStatus.Unhealthy] = StatusCodes.Status503ServiceUnavailable
            }
        });
        
        app.UseHealthChecks("/health/ready", new HealthCheckOptions
        {
            Predicate = check => check.Tags.Contains("ready"),
            ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse
        });
    }
}

// Custom telemetry processor
public class EnrichmentTelemetryProcessor : ITelemetryProcessor
{
    private readonly ITelemetryProcessor _next;

    public void Process(ITelemetry item)
    {
        if (item is RequestTelemetry request)
        {
            // Add custom properties
            request.Properties["Environment"] = Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT");
            request.Properties["MachineName"] = Environment.MachineName;
            
            // Add user context if available
            if (request.Context.User.Id != null)
            {
                request.Properties["UserId"] = request.Context.User.Id;
            }
        }

        _next.Process(item);
    }
}

// Request tracking middleware
public class RequestTrackingMiddleware
{
    private readonly RequestDelegate _next;
    private readonly TelemetryClient _telemetryClient;

    public async Task InvokeAsync(HttpContext context)
    {
        var stopwatch = Stopwatch.StartNew();
        
        try
        {
            await _next(context);
        }
        finally
        {
            stopwatch.Stop();
            
            // Track custom metrics
            _telemetryClient.TrackMetric("RequestDuration", stopwatch.ElapsedMilliseconds, 
                new Dictionary<string, string>
                {
                    ["Controller"] = context.Request.RouteValues["controller"]?.ToString(),
                    ["Action"] = context.Request.RouteValues["action"]?.ToString(),
                    ["StatusCode"] = context.Response.StatusCode.ToString()
                });
        }
    }
}
```

**Custom Health Checks:**
```csharp
public class DatabaseHealthCheck : IHealthCheck
{
    private readonly string _connectionString;
    private readonly ILogger<DatabaseHealthCheck> _logger;

    public async Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context, 
        CancellationToken cancellationToken = default)
    {
        try
        {
            using var connection = new SqlConnection(_connectionString);
            await connection.OpenAsync(cancellationToken);
            
            var command = connection.CreateCommand();
            command.CommandText = "SELECT 1";
            await command.ExecuteScalarAsync(cancellationToken);
            
            return HealthCheckResult.Healthy("Database is accessible");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Database health check failed");
            return HealthCheckResult.Unhealthy("Database is not accessible", ex);
        }
    }
}

public class RedisHealthCheck : IHealthCheck
{
    private readonly IConnectionMultiplexer _redis;

    public async Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context, 
        CancellationToken cancellationToken = default)
    {
        try
        {
            var database = _redis.GetDatabase();
            await database.PingAsync();
            
            var info = await _redis.GetServer(_redis.GetEndPoints().First()).InfoAsync();
            var memory = info.FirstOrDefault(x => x.Key == "used_memory_human").Value;
            
            return HealthCheckResult.Healthy($"Redis is accessible. Memory usage: {memory}");
        }
        catch (Exception ex)
        {
            return HealthCheckResult.Unhealthy("Redis is not accessible", ex);
        }
    }
}
```

### 10.2 Logging Strategy

**Structured Logging with Serilog:**
```csharp
public class Program
{
    public static async Task Main(string[] args)
    {
        Log.Logger = new LoggerConfiguration()
            .MinimumLevel.Information()
            .MinimumLevel.Override("Microsoft", LogEventLevel.Warning)
            .MinimumLevel.Override("System", LogEventLevel.Warning)
            .Enrich.FromLogContext()
            .Enrich.WithProperty("Application", "HotelBookingSystem")
            .Enrich.WithProperty("Environment", Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT"))
            .WriteTo.Console(outputTemplate: "[{Timestamp:HH:mm:ss} {Level:u3}] {Message:lj} {Properties:j}{NewLine}{Exception}")
            .WriteTo.ApplicationInsights(TelemetryConfiguration.CreateDefault(), TelemetryConverter.Traces)
            .WriteTo.File("logs/hotel-booking-.txt", 
                rollingInterval: RollingInterval.Day,
                retainedFileCountLimit: 30)
            .CreateLogger();

        try
        {
            Log.Information("Starting Hotel Booking System");
            await CreateHostBuilder(args).Build().RunAsync();
        }
        catch (Exception ex)
        {
            Log.Fatal(ex, "Application terminated unexpectedly");
        }
        finally
        {
            Log.CloseAndFlush();
        }
    }
}

// Usage in services
public class BookingService : IBookingService
{
    private readonly ILogger<BookingService> _logger;

    public async Task<BookingResult> CreateBookingAsync(CreateBookingRequest request)
    {
        using var activity = _logger.BeginScope(new Dictionary<string, object>
        {
            ["BookingReference"] = request.BookingReference,
            ["UserId"] = request.UserId,
            ["HotelId"] = request.HotelId
        });

        _logger.LogInformation("Creating booking for user {UserId} at hotel {HotelId}", 
            request.UserId, request.HotelId);

        try
        {
            var booking = await ProcessBookingAsync(request);
            
            _logger.LogInformation("Booking {BookingId} created successfully with total amount {Amount}", 
                booking.Id, booking.TotalAmount);
                
            return BookingResult.Success(booking);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to create booking for user {UserId}", request.UserId);
            return BookingResult.Failed("Booking creation failed");
        }
    }
}
```

### 10.3 Alerting & Notifications

**Azure Monitor Alert Rules:**
```bicep
// High error rate alert
resource highErrorRateAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: 'HighErrorRate'
  location: 'global'
  properties: {
    description: 'Alert when error rate exceeds 5%'
    severity: 2
    enabled: true
    scopes: [
      applicationInsights.id
    ]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'ErrorRate'
          metricName: 'requests/failed'
          operator: 'GreaterThan'
          threshold: 5
          timeAggregation: 'Average'
        }
      ]
    }
    actions: [
      {
        actionGroupId: alertActionGroup.id
      }
    ]
  }
}

// High response time alert
resource highResponseTimeAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: 'HighResponseTime'
  location: 'global'
  properties: {
    description: 'Alert when average response time exceeds 3 seconds'
    severity: 3
    enabled: true
    scopes: [
      applicationInsights.id
    ]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'ResponseTime'
          metricName: 'requests/duration'
          operator: 'GreaterThan'
          threshold: 3000
          timeAggregation: 'Average'
        }
      ]
    }
    actions: [
      {
        actionGroupId: alertActionGroup.id
      }
    ]
  }
}

// Action Group for notifications
resource alertActionGroup 'Microsoft.Insights/actionGroups@2022-06-01' = {
  name: 'HBS-AlertGroup'
  location: 'global'
  properties: {
    groupShortName: 'HBSAlerts'
    enabled: true
    emailReceivers: [
      {
        name: 'DevTeam'
        emailAddress: 'dev-team@company.com'
        useCommonAlertSchema: true
      }
    ]
    smsReceivers: [
      {
        name: 'OnCallEngineer'
        countryCode: '1'
        phoneNumber: '555-123-4567'
      }
    ]
    webhookReceivers: [
      {
        name: 'SlackWebhook'
        serviceUri: 'https://hooks.slack.com/services/...'
        useCommonAlertSchema: true
      }
    ]
  }
}
```

### 10.4 Performance Metrics

**Custom Performance Metrics:**
```csharp
public class PerformanceMetricsService : IPerformanceMetricsService
{
    private readonly TelemetryClient _telemetryClient;
    private readonly ILogger<PerformanceMetricsService> _logger;

    public void TrackBookingMetrics(BookingMetrics metrics)
    {
        // Track booking conversion funnel
        _telemetryClient.TrackMetric("BookingFunnel.Search", 1,
            new Dictionary<string, string>
            {
                ["Location"] = metrics.SearchLocation,
                ["CheckInDate"] = metrics.CheckInDate.ToString("yyyy-MM-dd")
            });

        if (metrics.HotelSelected)
        {
            _telemetryClient.TrackMetric("BookingFunnel.HotelSelected", 1);
        }

        if (metrics.BookingStarted)
        {
            _telemetryClient.TrackMetric("BookingFunnel.BookingStarted", 1);
        }

        if (metrics.BookingCompleted)
        {
            _telemetryClient.TrackMetric("BookingFunnel.BookingCompleted", 1,
                new Dictionary<string, string>
                {
                    ["Amount"] = metrics.BookingAmount.ToString(),
                    ["PaymentMethod"] = metrics.PaymentMethod
                });
        }
    }

    public void TrackSearchPerformance(SearchPerformanceMetrics metrics)
    {
        _telemetryClient.TrackMetric("Search.Duration", metrics.DurationMs,
            new Dictionary<string, string>
            {
                ["ResultCount"] = metrics.ResultCount.ToString(),
                ["HasFilters"] = metrics.HasFilters.ToString()
            });

        _telemetryClient.TrackMetric("Search.ResultCount", metrics.ResultCount);
    }

    public void TrackBusinessMetrics(BusinessMetrics metrics)
    {
        // Revenue metrics
        _telemetryClient.TrackMetric("Revenue.Daily", metrics.DailyRevenue);
        _telemetryClient.TrackMetric("Revenue.Commission", metrics.CommissionEarned);
        
        // Occupancy metrics
        _telemetryClient.TrackMetric("Occupancy.Rate", metrics.OccupancyRate);
        _telemetryClient.TrackMetric("Occupancy.ADR", metrics.AverageRoomRate);
        _telemetryClient.TrackMetric("Occupancy.RevPAR", metrics.RevenuePerAvailableRoom);
        
        // Customer metrics
        _telemetryClient.TrackMetric("Customer.NPS", metrics.NetPromoterScore);
        _telemetryClient.TrackMetric("Customer.RepeatBookings", metrics.RepeatBookingRate);
    }
}

// Dashboard queries (KQL)
public static class DashboardQueries
{
    public const string BookingConversionRate = @"
        customEvents
        | where name in ('BookingFunnel.Search', 'BookingFunnel.BookingCompleted')
        | summarize 
            Searches = countif(name == 'BookingFunnel.Search'),
            Completions = countif(name == 'BookingFunnel.BookingCompleted')
        | extend ConversionRate = round(Completions * 100.0 / Searches, 2)
    ";

    public const string AverageResponseTime = @"
        requests
        | where timestamp > ago(24h)
        | summarize avg(duration) by bin(timestamp, 1h), operation_Name
        | render timechart
    ";

    public const string ErrorRateByOperation = @"
        requests
        | where timestamp > ago(24h)
        | summarize 
            TotalRequests = count(),
            FailedRequests = countif(success == false)
        by operation_Name
        | extend ErrorRate = round(FailedRequests * 100.0 / TotalRequests, 2)
        | order by ErrorRate desc
    ";
}
```

---

## 11. Disaster Recovery & High Availability

### 11.1 Backup Strategy

**Multi-Tier Backup Approach:**
```
┌─────────────────────────────────────────────────────────────────┐
│                         BACKUP TIERS                           │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   TIER 1        │   TIER 2        │    TIER 3                   │
│   Real-time     │   Daily         │    Monthly                  │
│   Replication   │   Snapshots     │    Archive                  │
├─────────────────┼─────────────────┼─────────────────────────────┤
│ • Transaction   │ • Full DB       │ • Long-term                 │
│   Log Backup    │   Backup        │   Retention                 │
│ • 15-min RPO    │ • File System   │ • Compliance                │
│ • Geo-replica   │   Backup        │ • Cold Storage              │
│   Database      │ • Config        │ • 7-year                    │
│                 │   Backup        │   Retention                 │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

**Azure SQL Database Backup Configuration:**
```bicep
resource sqlDatabase 'Microsoft.Sql/servers/databases@2022-05-01-preview' = {
  name: '${sqlServerName}/${databaseName}'
  location: location
  properties: {
    collation: 'SQL_Latin1_General_CP1_CI_AS'
    maxSizeBytes: 268435456000 // 250 GB
    requestedServiceObjectiveName: 'S4'
    
    // Backup configuration
    longTermRetentionBackupResourceId: longTermRetentionVault.id
    backupStorageRedundancy: 'GeoZone'
    
    // Point-in-time restore
    earliestRestoreDate: '2023-01-01T00:00:00Z'
    
    // Geo-replication
    secondaryType: 'Geo'
    readScale: 'Enabled'
  }
}

// Long-term retention policy
resource longTermRetentionPolicy 'Microsoft.Sql/servers/databases/backupLongTermRetentionPolicies@2022-05-01-preview' = {
  parent: sqlDatabase
  name: 'default'
  properties: {
    weeklyRetention: 'P12W'    // 12 weeks
    monthlyRetention: 'P12M'   // 12 months
    yearlyRetention: 'P7Y'     // 7 years
    weekOfYear: 1
  }
}

// Geo-redundant backup vault
resource backupVault 'Microsoft.DataProtection/backupVaults@2022-04-01' = {
  name: 'hbs-backup-vault'
  location: location
  properties: {
    storageSettings: [
      {
        datastoreType: 'VaultStore'
        type: 'GeoRedundant'
      }
    ]
  }
  identity: {
    type: 'SystemAssigned'
  }
}
```

**Automated Backup Verification:**
```csharp
public class BackupVerificationService : IBackupVerificationService
{
    private readonly ILogger<BackupVerificationService> _logger;
    private readonly ISqlDatabaseService _databaseService;
    private readonly IBlobStorageService _storageService;

    public async Task<BackupVerificationResult> VerifyDatabaseBackupAsync(string backupName)
    {
        try
        {
            _logger.LogInformation("Starting backup verification for {BackupName}", backupName);
            
            // 1. Verify backup file exists and is not corrupted
            var backupInfo = await _databaseService.GetBackupInfoAsync(backupName);
            if (backupInfo == null)
            {
                return BackupVerificationResult.Failed("Backup file not found");
            }

            // 2. Create temporary test database from backup
            var testDbName = $"test_restore_{DateTime.UtcNow:yyyyMMdd_HHmmss}";
            await _databaseService.RestoreFromBackupAsync(backupName, testDbName);

            // 3. Run data integrity checks
            var integrityResult = await RunDataIntegrityChecksAsync(testDbName);
            if (!integrityResult.IsValid)
            {
                return BackupVerificationResult.Failed($"Data integrity check failed: {integrityResult.Error}");
            }

            // 4. Verify row counts match expected values
            var rowCountCheck = await VerifyRowCountsAsync(testDbName);
            if (!rowCountCheck.IsValid)
            {
                return BackupVerificationResult.Failed($"Row count verification failed: {rowCountCheck.Error}");
            }

            // 5. Clean up test database
            await _databaseService.DropDatabaseAsync(testDbName);

            _logger.LogInformation("Backup verification completed successfully for {BackupName}", backupName);
            return BackupVerificationResult.Success();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Backup verification failed for {BackupName}", backupName);
            return BackupVerificationResult.Failed($"Verification error: {ex.Message}");
        }
    }

    private async Task<IntegrityCheckResult> RunDataIntegrityChecksAsync(string databaseName)
    {
        var checks = new[]
        {
            "DBCC CHECKDB",
            "DBCC CHECKTABLE('Users')",
            "DBCC CHECKTABLE('Bookings')",
            "DBCC CHECKTABLE('Hotels')"
        };

        foreach (var check in checks)
        {
            var result = await _databaseService.ExecuteIntegrityCheckAsync(databaseName, check);
            if (!result.IsSuccessful)
            {
                return IntegrityCheckResult.Failed($"Check failed: {check} - {result.Error}");
            }
        }

        return IntegrityCheckResult.Success();
    }
}

// Scheduled backup verification
public class BackupVerificationHostedService : BackgroundService
{
    private readonly IBackupVerificationService _verificationService;
    private readonly ILogger<BackupVerificationHostedService> _logger;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                // Run daily backup verification at 2 AM
                var now = DateTime.UtcNow;
                var scheduledTime = now.Date.AddHours(2);
                
                if (now > scheduledTime)
                    scheduledTime = scheduledTime.AddDays(1);

                var delay = scheduledTime - now;
                await Task.Delay(delay, stoppingToken);

                await VerifyRecentBackupsAsync();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in backup verification service");
                await Task.Delay(TimeSpan.FromHours(1), stoppingToken);
            }
        }
    }

    private async Task VerifyRecentBackupsAsync()
    {
        var yesterday = DateTime.UtcNow.AddDays(-1);
        var backups = await GetBackupsForDateAsync(yesterday);
        
        foreach (var backup in backups)
        {
            var result = await _verificationService.VerifyDatabaseBackupAsync(backup.Name);
            if (!result.IsSuccessful)
            {
                _logger.LogError("Backup verification failed for {BackupName}: {Error}", 
                    backup.Name, result.Error);
                
                // Send alert to operations team
                await SendBackupFailureAlertAsync(backup.Name, result.Error);
            }
        }
    }
}
```

### 11.2 Failover Mechanisms

**Automatic Failover Configuration:**
```csharp
public class FailoverService : IFailoverService
{
    private readonly IConfiguration _configuration;
    private readonly ILogger<FailoverService> _logger;
    private readonly IHealthCheckService _healthCheckService;

    public async Task<FailoverResult> InitiateFailoverAsync(FailoverReason reason)
    {
        _logger.LogWarning("Initiating failover due to: {Reason}", reason);
        
        try
        {
            // 1. Stop accepting new requests
            await SetMaintenanceModeAsync(true);
            
            // 2. Wait for existing requests to complete (max 30 seconds)
            await WaitForActiveRequestsAsync(TimeSpan.FromSeconds(30));
            
            // 3. Switch database to secondary region
            var dbFailoverResult = await FailoverDatabaseAsync();
            if (!dbFailoverResult.IsSuccessful)
            {
                throw new FailoverException($"Database failover failed: {dbFailoverResult.Error}");
            }
            
            // 4. Update DNS to point to secondary region
            var dnsUpdateResult = await UpdateDnsRecordsAsync();
            if (!dnsUpdateResult.IsSuccessful)
            {
                throw new FailoverException($"DNS update failed: {dnsUpdateResult.Error}");
            }
            
            // 5. Start services in secondary region
            var serviceStartResult = await StartSecondaryRegionServicesAsync();
            if (!serviceStartResult.IsSuccessful)
            {
                throw new FailoverException($"Service startup failed: {serviceStartResult.Error}");
            }
            
            // 6. Verify failover completion
            var verificationResult = await VerifyFailoverAsync();
            if (!verificationResult.IsSuccessful)
            {
                throw new FailoverException($"Failover verification failed: {verificationResult.Error}");
            }
            
            // 7. Resume normal operations
            await SetMaintenanceModeAsync(false);
            
            _logger.LogInformation("Failover completed successfully");
            return FailoverResult.Success();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failover failed");
            
            // Attempt rollback
            await RollbackFailoverAsync();
            
            return FailoverResult.Failed(ex.Message);
        }
    }

    private async Task<DatabaseFailoverResult> FailoverDatabaseAsync()
    {
        // Azure SQL Database automatic failover
        var connectionString = _configuration.GetConnectionString("DefaultConnection");
        var builder = new SqlConnectionStringBuilder(connectionString);
        
        using var connection = new SqlConnection(connectionString);
        await connection.OpenAsync();
        
        var command = new SqlCommand("ALTER DATABASE CURRENT SET PARTNER FAILOVER", connection);
        await command.ExecuteNonQueryAsync();
        
        // Wait for failover to complete
        await Task.Delay(TimeSpan.FromSeconds(30));
        
        // Verify connection to new primary
        return await VerifyDatabaseConnectionAsync();
    }

    private async Task<DnsUpdateResult> UpdateDnsRecordsAsync()
    {
        // Update Azure DNS or external DNS provider
        // This would typically involve calling Azure DNS management APIs
        // to point the main domain to the secondary region
        
        var dnsClient = new DnsManagementClient();
        return await dnsClient.UpdateARecordAsync(
            "api.hotelbooking.com", 
            _configuration["SecondaryRegion:IpAddress"]);
    }
}

// Health-based automatic failover trigger
public class FailoverMonitoringService : BackgroundService
{
    private readonly IFailoverService _failoverService;
    private readonly IHealthCheckService _healthCheckService;
    private readonly ILogger<FailoverMonitoringService> _logger;
    private readonly FailoverConfiguration _config;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                var healthResult = await _healthCheckService.CheckHealthAsync();
                
                if (healthResult.Status == HealthStatus.Unhealthy)
                {
                    var unhealthyDuration = DateTime.UtcNow - healthResult.LastHealthyTime;
                    
                    if (unhealthyDuration > _config.FailoverThreshold)
                    {
                        _logger.LogCritical("System unhealthy for {Duration}. Initiating automatic failover", 
                            unhealthyDuration);
                        
                        await _failoverService.InitiateFailoverAsync(
                            FailoverReason.HealthCheckFailure);
                    }
                }
                
                await Task.Delay(_config.MonitoringInterval, stoppingToken);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in failover monitoring service");
                await Task.Delay(TimeSpan.FromMinutes(1), stoppingToken);
            }
        }
    }
}
```

### 11.3 Recovery Procedures

**Disaster Recovery Runbook:**
```yaml
# disaster-recovery-playbook.yaml
name: Hotel Booking System Disaster Recovery
version: "1.0"
last_updated: "2025-10-27"

recovery_objectives:
  rto: "4 hours"  # Recovery Time Objective
  rpo: "1 hour"   # Recovery Point Objective

scenarios:
  - name: "Primary Region Failure"
    severity: "Critical"
    estimated_duration: "2-4 hours"
    procedures:
      - step: 1
        action: "Assess Impact"
        description: "Determine scope of outage and affected services"
        responsible: "Incident Commander"
        duration: "15 minutes"
        
      - step: 2
        action: "Activate Crisis Team"
        description: "Notify stakeholders and activate response team"
        responsible: "Incident Commander"
        duration: "10 minutes"
        
      - step: 3
        action: "Initiate Database Failover"
        description: "Switch to secondary database in backup region"
        responsible: "Database Administrator"
        duration: "30 minutes"
        commands:
          - "az sql db replica set-primary --name hbs-prod-db --resource-group hbs-prod-westeurope"
          - "az sql server firewall-rule update --name AllowAzureServices --resource-group hbs-prod-westeurope"
        
      - step: 4
        action: "Deploy Application to Secondary Region"
        description: "Deploy latest application version to backup region"
        responsible: "DevOps Engineer"
        duration: "45 minutes"
        commands:
          - "kubectl config use-context hbs-prod-westeurope"
          - "helm upgrade hbs-prod ./charts/hotel-booking-system --set region=westeurope"
          
      - step: 5
        action: "Update DNS Records"
        description: "Point main domain to secondary region"
        responsible: "Network Administrator"
        duration: "15 minutes"
        commands:
          - "az network dns record-set a update -g hbs-prod-dns -z hotelbooking.com -n api --set aRecords[0].ipv4Address=<secondary-ip>"
          
      - step: 6
        action: "Verify System Recovery"
        description: "Test critical paths and validate system functionality"
        responsible: "QA Lead"
        duration: "30 minutes"
        
      - step: 7
        action: "Communicate Status"
        description: "Update status page and notify stakeholders"
        responsible: "Communications Lead"
        duration: "15 minutes"

  - name: "Database Corruption"
    severity: "High"
    procedures:
      - step: 1
        action: "Isolate Corrupted Database"
        description: "Take database offline to prevent further corruption"
        
      - step: 2
        action: "Restore from Latest Backup"
        description: "Restore database from most recent clean backup"
        
      - step: 3
        action: "Replay Transaction Logs"
        description: "Apply transaction logs to minimize data loss"

communication_plan:
  internal:
    - slack_channel: "#incident-response"
    - email_list: "incident-team@company.com"
    - phone_tree: "Available in emergency contacts"
    
  external:
    - status_page: "status.hotelbooking.com"
    - customer_email: "updates sent via notification service"
    - social_media: "@hotelbooking Twitter account"

testing_schedule:
  - type: "Tabletop Exercise"
    frequency: "Quarterly"
    last_conducted: "2025-07-15"
    next_scheduled: "2025-10-15"
    
  - type: "Live Failover Test"
    frequency: "Semi-annually"
    last_conducted: "2025-04-01"
    next_scheduled: "2025-10-01"
```

**Recovery Automation Scripts:**
```bash
#!/bin/bash
# recovery-automation.sh

set -e

SECONDARY_REGION="westeurope"
PRIMARY_REGION="eastus"
RESOURCE_GROUP="hbs-prod-${SECONDARY_REGION}"

echo "Starting disaster recovery to $SECONDARY_REGION..."

# 1. Check if secondary region is available
echo "Checking secondary region availability..."
az group show --name $RESOURCE_GROUP > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: Secondary resource group not found"
    exit 1
fi

# 2. Failover database
echo "Initiating database failover..."
az sql db replica set-primary \
    --name hbs-prod-db \
    --resource-group $RESOURCE_GROUP \
    --server hbs-prod-sql-$SECONDARY_REGION

# Wait for database failover to complete
echo "Waiting for database failover to complete..."
sleep 60

# 3. Update Kubernetes context
echo "Switching to secondary region Kubernetes cluster..."
kubectl config use-context hbs-prod-$SECONDARY_REGION

# 4. Scale up services in secondary region
echo "Scaling up services in secondary region..."
kubectl scale deployment booking-service --replicas=5
kubectl scale deployment search-service --replicas=3
kubectl scale deployment payment-service --replicas=3

# 5. Wait for pods to be ready
echo "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=booking-service --timeout=300s
kubectl wait --for=condition=ready pod -l app=search-service --timeout=300s
kubectl wait --for=condition=ready pod -l app=payment-service --timeout=300s

# 6. Update ingress to accept traffic
echo "Updating ingress configuration..."
kubectl apply -f k8s/ingress-production.yaml

# 7. Run health checks
echo "Running health checks..."
HEALTH_URL="https://api-dr.hotelbooking.com/health"
for i in {1..10}; do
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)
    if [ $HTTP_STATUS -eq 200 ]; then
        echo "Health check passed"
        break
    else
        echo "Health check failed (attempt $i/10). Retrying in 30 seconds..."
        sleep 30
    fi
done

if [ $HTTP_STATUS -ne 200 ]; then
    echo "ERROR: Health checks failed after 10 attempts"
    exit 1
fi

# 8. Update DNS (example with Azure DNS)
echo "Updating DNS records..."
az network dns record-set a update \
    --resource-group hbs-prod-dns \
    --zone-name hotelbooking.com \
    --name api \
    --set aRecords[0].ipv4Address=$(kubectl get svc api-gateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "Disaster recovery completed successfully!"
echo "Services are now running in $SECONDARY_REGION"
echo "DNS propagation may take up to 5 minutes"
```

### 11.4 High Availability Design

**Multi-Region Architecture:**
```
┌─────────────────────────────────────────────────────────────────┐
│                      GLOBAL TRAFFIC MANAGER                    │
│                    (Azure Front Door)                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
┌─────────────────────────────┐   ┌─────────────────────────────┐
│       PRIMARY REGION        │   │      SECONDARY REGION       │
│        (East US)            │   │       (West Europe)         │
├─────────────────────────────┤   ├─────────────────────────────┤
│ • Active-Active Setup       │   │ • Hot Standby              │
│ • Load Balancer (3 nodes)   │   │ • Load Balancer (2 nodes)  │
│ • AKS Cluster (5 nodes)     │   │ • AKS Cluster (3 nodes)    │
│ • SQL Database (Primary)    │   │ • SQL Database (Secondary)  │
│ • Redis Cache (Primary)     │   │ • Redis Cache (Replica)    │
│ • Storage (RA-GRS)          │   │ • Storage (GRS Replica)    │
└─────────────────────────────┘   └─────────────────────────────┘
                │                           │
                └─────────────┬─────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    SHARED SERVICES                             │
├─────────────────────────────────────────────────────────────────┤
│ • Azure Key Vault (Global)                                     │
│ • Azure Monitor (Global)                                       │
│ • Azure DNS (Global)                                           │
│ • Application Insights (Global)                                │
└─────────────────────────────────────────────────────────────────┘
```

**High Availability Configuration:**
```bicep
// Azure Front Door for global load balancing
resource frontDoor 'Microsoft.Cdn/profiles@2022-11-01-preview' = {
  name: 'hbs-global-fd'
  location: 'global'
  sku: {
    name: 'Premium_AzureFrontDoor'
  }
  properties: {
    originResponseTimeoutSeconds: 60
  }
}

// Origin groups for multi-region setup
resource originGroup 'Microsoft.Cdn/profiles/originGroups@2022-11-01-preview' = {
  parent: frontDoor
  name: 'api-origin-group'
  properties: {
    loadBalancingSettings: {
      sampleSize: 4
      successfulSamplesRequired: 3
      additionalLatencyInMilliseconds: 50
    }
    healthProbeSettings: {
      probePath: '/health'
      probeRequestType: 'GET'
      probeProtocol: 'Https'
      probeIntervalInSeconds: 60
    }
  }
}

// Primary region origin
resource primaryOrigin 'Microsoft.Cdn/profiles/originGroups/origins@2022-11-01-preview' = {
  parent: originGroup
  name: 'primary-eastus'
  properties: {
    hostName: 'api-eastus.hotelbooking.com'
    httpPort: 80
    httpsPort: 443
    priority: 1
    weight: 1000
    enabledState: 'Enabled'
  }
}

// Secondary region origin
resource secondaryOrigin 'Microsoft.Cdn/profiles/originGroups/origins@2022-11-01-preview' = {
  parent: originGroup
  name: 'secondary-westeurope'
  properties: {
    hostName: 'api-westeurope.hotelbooking.com'
    httpPort: 80
    httpsPort: 443
    priority: 2
    weight: 100
    enabledState: 'Enabled'
  }
}

// Auto-failover routing rule
resource routingRule 'Microsoft.Cdn/profiles/afdEndpoints/routes@2022-11-01-preview' = {
  name: 'api-route'
  properties: {
    customDomains: [
      {
        id: apiCustomDomain.id
      }
    ]
    originGroup: {
      id: originGroup.id
    }
    routeConfigurationOverride: {
      forwardingProtocol: 'HttpsOnly'
      cacheConfiguration: {
        queryStringCachingBehavior: 'IgnoreQueryString'
        compressionSettings: {
          contentTypesToCompress: [
            'application/json'
            'text/html'
            'text/css'
            'application/javascript'
          ]
          isCompressionEnabled: true
        }
      }
    }
    patternsToMatch: [
      '/api/*'
    ]
    supportedProtocols: [
      'Http'
      'Https'
    ]
    httpsRedirect: 'Enabled'
  }
}
```

**Application-Level HA Implementation:**
```csharp
public class HighAvailabilityService : IHighAvailabilityService
{
    private readonly IServiceProvider _serviceProvider;
    private readonly IConfiguration _configuration;
    private readonly ILogger<HighAvailabilityService> _logger;

    public async Task<T> ExecuteWithFallbackAsync<T>(Func<Task<T>> primaryOperation, 
        Func<Task<T>> fallbackOperation = null)
    {
        try
        {
            return await primaryOperation();
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Primary operation failed, attempting fallback");
            
            if (fallbackOperation != null)
            {
                try
                {
                    return await fallbackOperation();
                }
                catch (Exception fallbackEx)
                {
                    _logger.LogError(fallbackEx, "Fallback operation also failed");
                    throw new AggregateException(ex, fallbackEx);
                }
            }
            
            throw;
        }
    }

    public async Task<SearchResult> SearchHotelsWithFallbackAsync(SearchRequest request)
    {
        return await ExecuteWithFallbackAsync(
            primaryOperation: () => SearchFromPrimaryServiceAsync(request),
            fallbackOperation: () => SearchFromCacheAsync(request)
        );
    }

    private async Task<SearchResult> SearchFromCacheAsync(SearchRequest request)
    {
        // Fallback to cached results when primary search service is unavailable
        var cacheKey = $"fallback_search:{request.GetHashCode()}";
        var cachedResults = await GetFromCacheAsync<SearchResult>(cacheKey);
        
        if (cachedResults != null)
        {
            _logger.LogInformation("Serving fallback search results from cache");
            cachedResults.IsFallback = true;
            return cachedResults;
        }
        
        // Return minimal results if no cache available
        return new SearchResult
        {
            Hotels = new List<HotelSummary>(),
            Message = "Search service temporarily unavailable. Please try again later.",
            IsFallback = true
        };
    }
}

// Circuit breaker for external services
public class CircuitBreakerBookingService : IBookingService
{
    private readonly IBookingService _innerService;
    private readonly CircuitBreakerPolicy _circuitBreaker;

    public CircuitBreakerBookingService(IBookingService innerService)
    {
        _innerService = innerService;
        _circuitBreaker = Policy
            .Handle<HttpRequestException>()
            .Or<TimeoutException>()
            .CircuitBreakerAsync(
                handledEventsAllowedBeforeBreaking: 5,
                durationOfBreak: TimeSpan.FromMinutes(1),
                onBreak: (exception, duration) => 
                {
                    // Switch to fallback mode
                    EnableFallbackMode();
                },
                onReset: () => 
                {
                    // Resume normal operations
                    DisableFallbackMode();
                });
    }

    public async Task<BookingResult> CreateBookingAsync(CreateBookingRequest request)
    {
        return await _circuitBreaker.ExecuteAsync(async () =>
        {
            return await _innerService.CreateBookingAsync(request);
        });
    }
}
```

---

## 12. Architecture Decision Records (ADRs)

### 12.1 ADR Template

**Standard ADR Format:**
```markdown
# ADR-001: [Title]

**Status:** [Proposed | Accepted | Rejected | Deprecated | Superseded]
**Date:** YYYY-MM-DD
**Deciders:** [Names of decision makers]
**Technical Story:** [Link to user story or technical requirement]

## Context

[Describe the context and problem statement that led to this decision]

## Decision

[State the decision that was made]

## Rationale

[Explain why this decision was made, including alternatives considered]

## Consequences

### Positive
- [List positive outcomes]

### Negative
- [List negative outcomes or trade-offs]

### Risks
- [List potential risks and mitigation strategies]

## Implementation

[High-level implementation approach if applicable]

## Related Decisions

[References to related ADRs]
```

### 12.2 Key Architecture Decisions

#### ADR-001: Microservices Architecture

**Status:** Accepted  
**Date:** 2025-10-01  
**Deciders:** Architecture Team, Technical Lead  

**Context**
The Hotel Booking System needs to handle high traffic volumes, support multiple development teams, and enable independent deployment of features. We need to choose between monolithic and microservices architecture.

**Decision**
Implement a microservices architecture with domain-driven design boundaries.

**Rationale**
- **Scalability:** Individual services can be scaled based on demand
- **Team Independence:** Different teams can work on different services
- **Technology Diversity:** Can use different technologies for different services
- **Fault Isolation:** Failure in one service doesn't bring down the entire system
- **Deployment Flexibility:** Services can be deployed independently

**Consequences**

**Positive:**
- Improved scalability and performance
- Better team productivity and independence
- Enhanced fault tolerance
- Technology flexibility

**Negative:**
- Increased complexity in service communication
- Need for sophisticated monitoring and observability
- Data consistency challenges
- Higher operational overhead

---

#### ADR-002: CQRS with Event Sourcing

**Status:** Accepted  
**Date:** 2025-10-05  
**Deciders:** Architecture Team, Domain Experts  

**Context**
The booking domain has complex business rules and requires audit trails. We need to decide on the data architecture pattern.

**Decision**
Implement CQRS (Command Query Responsibility Segregation) with selective event sourcing for critical aggregates.

**Rationale**
- **Performance:** Separate read and write models optimized for their specific use cases
- **Scalability:** Read models can be scaled independently
- **Audit Trail:** Event sourcing provides complete audit history
- **Business Insights:** Events can be replayed for analytics
- **Flexibility:** Different storage mechanisms for reads and writes

**Implementation**
- Commands: Write operations using event sourcing for Booking aggregate
- Queries: Read operations using optimized read models
- Event Store: Azure Event Hubs for event storage
- Read Models: SQL Server for query optimization

---

#### ADR-003: Azure Kubernetes Service for Container Orchestration

**Status:** Accepted  
**Date:** 2025-10-10  
**Deciders:** DevOps Team, Platform Team  

**Context**
Need to choose container orchestration platform for microservices deployment and management.

**Decision**
Use Azure Kubernetes Service (AKS) for container orchestration.

**Rationale**
- **Cloud Native:** Tight integration with Azure services
- **Auto-scaling:** Built-in horizontal and vertical pod autoscaling
- **Service Mesh:** Support for Istio service mesh for advanced traffic management
- **Security:** Integrated security scanning and policy enforcement
- **Monitoring:** Native integration with Azure Monitor
- **Cost Management:** Efficient resource utilization and cost controls

**Consequences**

**Positive:**
- Excellent scalability and reliability
- Strong ecosystem and community support
- Advanced networking and security features
- Integrated monitoring and logging

**Negative:**
- Kubernetes learning curve for team
- Increased complexity in initial setup
- Need for Kubernetes expertise for operations

---

#### ADR-004: Azure SQL Database with Geo-Replication

**Status:** Accepted  
**Date:** 2025-10-12  
**Deciders:** Database Team, Architecture Team  

**Context**
Need to choose primary database technology that provides high availability, disaster recovery, and global performance.

**Decision**
Use Azure SQL Database with geo-replication for primary data storage.

**Rationale**
- **High Availability:** 99.99% SLA with automatic failover
- **Disaster Recovery:** Geo-replicated backups and point-in-time restore
- **Performance:** Intelligent performance optimization and scaling
- **Security:** Advanced threat protection and encryption
- **Compliance:** Built-in compliance with industry standards
- **Integration:** Native Azure ecosystem integration

**Implementation**
- Primary: East US region
- Secondary: West Europe region for disaster recovery
- Read replicas: Additional regions for global read performance
- Backup: Long-term retention with geo-redundant storage

---

#### ADR-005: JWT Tokens for Authentication

**Status:** Accepted  
**Date:** 2025-10-15  
**Deciders:** Security Team, Architecture Team  

**Context**
Need to implement stateless authentication mechanism for microservices architecture.

**Decision**
Use JWT (JSON Web Tokens) for authentication with Azure Active Directory B2C as identity provider.

**Rationale**
- **Stateless:** No need for server-side session storage
- **Scalable:** Tokens can be validated by any service
- **Standard:** Industry standard with wide library support
- **Secure:** Digital signatures ensure token integrity
- **Flexible:** Support for custom claims and roles

**Implementation**
- Azure AD B2C for user management and token issuance
- RS256 algorithm for token signing
- Short-lived access tokens (1 hour) with refresh tokens
- Custom claims for user roles and permissions

---

## Appendices

### Appendix A: Technology Evaluation Matrix

| Technology | Pros | Cons | Score | Selected |
|------------|------|------|-------|----------|
| **Container Orchestration** |
| Kubernetes | Rich features, community | Complex | 9/10 | ✅ |
| Docker Swarm | Simple setup | Limited features | 6/10 | ❌ |
| Azure Container Instances | Serverless | Not for production workloads | 5/10 | ❌ |
| **Database** |
| Azure SQL Database | Managed, HA | Cost for large scale | 9/10 | ✅ |
| PostgreSQL | Open source, features | Management overhead | 7/10 | ❌ |
| MongoDB | Document model | Consistency challenges | 6/10 | ❌ |
| **Caching** |
| Redis | High performance, features | Memory-based | 9/10 | ✅ |
| Memcached | Simple, fast | Limited features | 6/10 | ❌ |
| **Message Queue** |
| Azure Service Bus | Managed, reliable | Azure-specific | 8/10 | ✅ |
| RabbitMQ | Feature-rich | Management complexity | 7/10 | ❌ |
| Apache Kafka | High throughput | Operational complexity | 7/10 | ❌ |

### Appendix B: Performance Benchmarks

| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| API Response Time (p95) | < 500ms | 380ms | ✅ |
| Database Query Time (avg) | < 100ms | 75ms | ✅ |
| Search Response Time | < 2s | 1.2s | ✅ |
| Booking Creation Time | < 3s | 2.1s | ✅ |
| Cache Hit Ratio | > 80% | 85% | ✅ |
| System Throughput | 10K req/min | 12K req/min | ✅ |
| Concurrent Users | 10K | 8K | ⚠️ |
| Database Connections | < 100 | 75 | ✅ |

### Appendix C: Compliance and Security

**Standards Compliance:**
- **PCI DSS Level 1:** Payment card data protection
- **GDPR:** European data protection regulation
- **SOC 2 Type II:** Security and availability controls
- **ISO 27001:** Information security management

**Security Certifications:**
- **Azure Security Center:** Continuous security assessment
- **Penetration Testing:** Quarterly security testing
- **Vulnerability Scanning:** Weekly automated scans
- **Security Audit:** Annual third-party security audit

---

**Document Control:**
- **Next Review Date:** January 27, 2026
- **Approval Required:** Chief Technology Officer, Security Lead, Platform Lead
- **Related Documents:** Software Requirements Specification, Business Overview, Test Cases, API Reference

**Change History:**
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-27 | Architecture Team | Initial comprehensive architecture document |
