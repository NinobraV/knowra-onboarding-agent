# Roles in Project

## Page 1

Project Manager 
Định nghĩa và lý do cần thiết Project Manager (PM) là người chịu trách nhiệm tổng thể cho 
việc lập kế hoạch, điều phối, kiểm soát tiến độ, ngân sách và giao tiếp với stakeholders. PM 
đảm bảo mọi vai trò khác hoạt động nhịp nhàng để giao release ổn định cho web và mobile. 
Giai đoạn tham gia Tham gia xuyên suốt từ Initiation đến Closing; đặc biệt quan trọng ở 
Planning, Execution và Release. 
Trách nhiệm chi tiết 
• 
Xây dựng roadmap release cho Web và Mobile; xác định milestones chính. 
• 
Lập kế hoạch sprint, phân bổ nguồn lực, quản lý ngân sách và scope. 
• 
Quản lý rủi ro, approve change request, quyết go/no-go cho release. 
• 
Theo dõi KPI dự án, báo cáo tiến độ cho khách hàng. 
• 
Tổ chức các cuộc họp chính thức: kick-off, steering committee, retrospectives. 
Kỹ năng bắt buộc Quản lý dự án Agile/Scrum, giao tiếp stakeholder, negotiation, risk 
management, basic hiểu biết kỹ thuật để đánh giá ước lượng. 
Công cụ thường dùng Jira, Confluence, ClickUp hoặc MS Project; Slack/Teams; Zoom; 
Google Sheets/Excel cho tracking ngân sách; dashboard báo cáo. 
Cách phối hợp Làm việc trực tiếp với BA để ưu tiên backlog, với Tech Lead để đánh giá nỗ 
lực, với DevOps để lên kế hoạch release, và với Customer Success khi có issue sau release. 
Tech Lead Solution Architect 
Định nghĩa và lý do cần thiết Tech Lead/Architect định hướng giải pháp kỹ thuật, đảm bảo 
kiến trúc đáp ứng non-functional requirements (scalability, security, performance) cho cả 
web và mobile. 
Giai đoạn tham gia Quan trọng ở Initiation (tech spike), Planning (technical roadmap), 
Execution (code review, thiết kế module) và Release (performance tuning). 
Trách nhiệm chi tiết 
• 
Thiết kế high-level architecture, lựa chọn stack cho frontend, backend, mobile, 
infra. 
• 
Định nghĩa API contracts, data model, security controls, và strategy cho 
caching/search/payment.

## Page 2

• 
Phê duyệt thiết kế module lớn, review code critical paths, support tech spike. 
• 
Định nghĩa guidelines, patterns, và mentoring dev team. 
Kỹ năng bắt buộc System design, cloud architecture (AWS/GCP), CI/CD, database design, 
security best practices, leadership kỹ thuật. 
Công cụ thường dùng Diagrams trong Confluence/Miro, GitHub/GitLab, Terraform, 
Docker/Kubernetes, Sentry/Prometheus/Grafana. 
Cách phối hợp Làm việc với BA để map requirements thành giải pháp; phối hợp Dev để 
implement; làm việc với DevOps cho deployment và monitoring. 
Developer Backend 
Định nghĩa và lý do cần thiết Backend Developer xây dựng các API, business logic, 
payment handling, data layer cho hệ thống booking; đảm bảo tính ổn định và an toàn dữ 
liệu. 
Giai đoạn tham gia Tham gia chính ở Design, Execution, và Support giai đoạn sau release. 
Trách nhiệm chi tiết 
• 
Thiết kế và triển khai API (booking flow, user, payment, admin). 
• 
Thiết kế schema DB, tối ưu truy vấn, xử lý concurrency/transaction cho booking. 
• 
Viết unit/integration tests, tham gia code review, fix bug. 
• 
Thực hiện logging, metrics, và hỗ trợ investigation production incidents. 
Kỹ năng bắt buộc REST/GraphQL, transactional DB (Postgres), caching (Redis), payment 
integration, testing, security (OWASP). 
Công cụ thường dùng Node.js/NestJS hoặc Spring Boot, PostgreSQL, Redis, Docker, 
Postman, GitHub Actions. 
Cách phối hợp Nhận requirement từ BA, phối hợp Tech Lead cho architecture, sync với 
Frontend/Mobile để thống nhất API contract, làm việc với QA cho test scenarios, phối hợp 
DevOps cho deploy. 
Developer Frontend Web 
Định nghĩa và lý do cần thiết Frontend Developer xây dựng giao diện web responsive, SEO-
friendly cho listing, booking và quản lý booking. 
Giai đoạn tham gia Design -> Execution -> Release -> Maintenance.

## Page 3

Trách nhiệm chi tiết 
• 
Chuyển Figma thành component, implement SSR/SEO pages. 
• 
Tối ưu performance (lazy load, code splitting), accessibility, và responsive behavior. 
• 
Tích hợp API, handle client-side validation và state management. 
• 
Viết unit/E2E tests và hỗ trợ QA reproduce UI bugs. 
Kỹ năng bắt buộc HTML/CSS, JavaScript/TypeScript, React/Next.js, state management, 
testing, performance tuning, a11y. 
Công cụ thường dùng React, Next.js, TypeScript, Storybook, Cypress, Jest, Figma. 
Cách phối hợp Làm việc với UI/UX để nhận design, BA để hiểu acceptance criteria, 
Backend để thống nhất API, QA để làm test coverage. 
Developer Mobile 
Định nghĩa và lý do cần thiết Developer Mobile xây dựng ứng dụng iOS/Android phục vụ 
booking, notification và quản lý booking di động. 
Giai đoạn tham gia Design -> Execution -> Beta testing -> Release -> Support. 
Trách nhiệm chi tiết 
• 
Implement UX flows mobile, tích hợp payment SDK và push notifications. 
• 
Xử lý offline/latency, caching, image optimization. 
• 
Tạo build release, quản lý provisioning, fix crash và support production issues. 
Kỹ năng bắt buộc React Native/Flutter, native module integration, debugging device, CI for 
mobile (Fastlane), testing trên thiết bị thật. 
Công cụ thường dùng React Native hoặc Flutter, Expo, Fastlane, Firebase/OneSignal, 
Detox/Appium, TestFlight/Play Console. 
Cách phối hợp Làm việc với BA và UI/UX để xác nhận flows; Backend để thống nhất API; 
DevOps cho pipeline and release; QA cho testing devices. 
Tester Quality Assurance 
Định nghĩa và lý do cần thiết QA đảm bảo chức năng và phi chức năng (performance, 
security) của hệ thống, phát hiện sớm lỗi để giảm rủi ro release.

## Page 4

Giai đoạn tham gia Từ Planning (test strategy) đến Execution (manual + automation), UAT 
và Release verification. 
Trách nhiệm chi tiết 
• 
Xây dựng test plan, test cases cho booking flow, payment, notification, admin 
functions. 
• 
Thực hiện automation regression; chạy performance/security tests; verify fixes. 
• 
Quản lý bug lifecycle, phối hợp với BA/Dev để reproduce và prioritise. 
Kỹ năng bắt buộc Test case design, automation (Cypress/Appium), performance testing, 
security testing basics, log/network trace analysis. 
Công cụ thường dùng TestRail/Jira, Cypress, Selenium/Appium, k6/JMeter, OWASP ZAP, CI 
integration. 
Cách phối hợp Nhận acceptance criteria từ BA; báo bug và test results cho Dev; phối hợp 
PM cho release readiness. 
DevOps Release Engineer 
Định nghĩa và lý do cần thiết DevOps đảm bảo môi trường deploy, pipeline CI/CD, 
monitoring và khả năng rollback để release an toàn cho backend và frontend. 
Giai đoạn tham gia Planning infra -> Implement CI/CD -> Release -> Monitor & Incident 
response. 
Trách nhiệm chi tiết 
• 
Xây dựng CI/CD pipelines, containerization và orchestration; quản lý secrets và infra 
as code. 
• 
Thiết lập staging/production parity, monitoring, alerting và runbooks. 
• 
Thực hiện blue-green/canary deployments, migrate DB khi cần, đảm bảo backup. 
Kỹ năng bắt buộc Docker, Kubernetes, Terraform, CI tools, monitoring/alerting, security và 
scripting. 
Công cụ thường dùng GitHub Actions/GitLab CI, Docker, Kubernetes (EKS/GKE), 
Terraform, Prometheus, Grafana, Sentry. 
Cách phối hợp Kết nối với Tech Lead để thực hiện kiến trúc infra, Dev để integrate 
pipelines, PM để plan release windows, QA cho môi trường test.

## Page 5

UI UX Designer 
Định nghĩa và lý do cần thiết UI/UX Designer tối ưu trải nghiệm booking, giảm drop-off và 
tăng tỷ lệ hoàn tất giao dịch trên web và mobile. 
Giai đoạn tham gia Discovery -> Design -> Prototyping -> Usability testing -> Handoff -> 
Iterate post-launch. 
Trách nhiệm chi tiết 
• 
Thực hiện user research, create personas và user journeys cho booking funnel. 
• 
Thiết kế wireframes, high-fidelity mockups, interactive prototypes và design system. 
• 
Thử nghiệm A/B cho checkout path; hỗ trợ QA/UAT để validate UX. 
Kỹ năng bắt buộc User research, interaction design, prototyping, usability testing, 
responsive design, accessibility. 
Công cụ thường dùng Figma, Miro, Hotjar, InVision, Zeplin, Google Analytics. 
Cách phối hợp Làm việc với BA để hiểu requirement, Dev để đảm bảo implement đúng 
design, QA để kiểm thử tính trực quan và accessibility. 
Support Customer Success 
Định nghĩa và lý do cần thiết Support/Customer Success xử lý ticket, hỗ trợ người dùng, 
và thu thập feedback để cải tiến sản phẩm sau release. 
Giai đoạn tham gia Post-launch chính, tham gia liên tục để support user issues và cải 
thiện sản phẩm. 
Trách nhiệm chi tiết 
• 
Tiếp nhận và xử lý ticket liên quan booking, payment, huỷ/đổi; escalate tới Dev/QA 
khi cần. 
• 
Duy trì knowledge base, FAQ và tổng hợp feedback khách hàng. 
• 
Theo dõi SLA, KPI hỗ trợ và phối hợp với PM/BA cho cải tiến sản phẩm. 
Kỹ năng bắt buộc Customer communication, problem triage, familiarity with 
booking/payment flows, CRM/ticketing tools. 
Công cụ thường dùng Zendesk/Freshdesk, Intercom, CRM, Google Sheets, internal 
dashboards.

## Page 6

Cách phối hợp Phối hợp trực tiếp với Dev/QA cho incident triage; báo cáo pattern issues 
cho BA/PM để ưu tiên fix.
