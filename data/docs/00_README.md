# 🏨 Hotel Booking System — Internal Knowledge Base

> Version: 1.0  
> Updated: 2025-10-25  
> Author: KnowRA
> Tags: business, architecture, booking, hospitality, ai-training

---

## 🔍 Overview

**Hotel Booking System (HBS)** is an online hotel reservation platform designed for hotel chains.  
The main objectives are to enable users to:
- Search for hotels, rooms, rates, and promotions.
- Book rooms and make online payments.
- Manage bookings, cancellations, and post-stay feedback.

The system serves two main roles:
- **End User:** The customer booking a room.  
- **Hotel Admin:** The property manager controlling availability, pricing, and schedules.

---

## ⚙️ Technology Stack

| Component | Technology |
|------------|-------------|
| Backend | .NET 8 Web API (Clean Architecture, CQRS) |
| Database | SQL Server, Redis |
| Frontend | React + TypeScript |
| Cloud Platform | Azure (App Service, Service Bus, SQL Database, Blob Storage) |
| Integrations | Payment Gateway, Email Service, SMS OTP |
| Monitoring | Application Insights, Azure Log Analytics |

---

## 📚 Core Modules

| Module | Description |
|---------|-------------|
| Search & Booking | Search rooms, check availability, and confirm booking |
| Payment | Handle payments via card or e-wallet |
| Cancellation | Manage room cancellations and refunds according to policy |
| Loyalty | Reward points, membership tiers |
| Admin Panel | Manage hotels, rooms, and pricing |
| Analytics | Reports and insights for hotel owners |
| Integration | External system connections (Payment, SMS, Email) |

---

## 🧭 Developer Quick Links

| Document | Description |
|-----------|-------------|
| [01_ONBOARDING_GUIDE.md](./01_ONBOARDING_GUIDE.md) | Developer onboarding guide |
| [02_BUSINESS_OVERVIEW.md](./02_BUSINESS_OVERVIEW.md) | Business and domain overview |
| [03_SYSTEM_ARCHITECTURE.md](./03_SYSTEM_ARCHITECTURE.md) | System architecture and design |
| [04_API_REFERENCE.md](./04_API_REFERENCE.md) | API documentation |
| [06_TEST_CASE_TEMPLATE.md](./06_TEST_CASE_TEMPLATE.md) | Standard test case format |
| [09_SECURITY_COMPLIANCE.md](./09_SECURITY_COMPLIANCE.md) | Security and compliance policies |

---

## 🧩 Notes

All documentation within this repository represents the **official knowledge source** for the Hotel Booking System.  
When training internal AI assistants, each section can be split into “knowledge chunks” (≈300–600 tokens) and embedded into a vector database such as **Azure Cognitive Search** or **Pinecone**.

---
