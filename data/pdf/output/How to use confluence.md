# How to use confluence

## Page 1

Đăng ký, đăng nhập và cài đặt site cơ bản 
• 
Đăng ký: truy cập trang Confluence Cloud của Atlassian, chọn gói phù hợp, đăng ký 
bằng email công ty hoặc tài khoản tổ chức. 
• 
Tạo site: khi đăng ký, bạn sẽ tạo site (ví dụ: yourcompany.atlassian.net). Chọn tên 
site, timezone và ngôn ngữ. 
• 
Đăng nhập: dùng email + mật khẩu Atlassian; bật 2FA/SAML nếu tổ chức yêu cầu. 
• 
Cài đặt admin ban đầu: vào Site administration → General settings để cấu hình logo, 
tên tổ chức, địa chỉ liên hệ và bật tính năng cần thiết (analytics, macros). 
• 
Mời user: Site administration → User management → Invite users; tạo nhóm mặc định 
(pm, ba, dev, qa, ops, designer, support). 
Cấu trúc Space và Page cho dự án booking hotel 
• 
Space dự án: tạo một Space riêng cho dự án (Project: BookingHotel). Chọn Space 
type “Team” hoặc “Documentation” tùy nhu cầu. 
• 
Cây Page khuyến nghị: 
o Home (Project overview, quick links) 
o  
1. Project charter (scope, objectives, stakeholders) 
o  
2. Roadmap & Releases (timeline, versions) 
o  
3. Requirements (BRD / PRD / user stories) 
o  
4. UX & Design (links Figma, prototypes) 
o  
5. Architecture & Tech Specs (diagrams, API contracts) 
o  
6. Development (guidelines, coding standard, repo links)

## Page 2

o  
7. QA & Test (test plan, test cases, test reports) 
o  
8. DevOps & Deploy (CI/CD pipelines, infra docs, runbooks) 
o  
9. Support & KB (FAQ, troubleshooting, contact) 
o  
10. Retrospectives & Reports (sprint reviews, metrics) 
• 
Page templates: tạo templates cho PRD, user story template, tech spec template, 
runbook template để chuẩn hóa nội dung. 
Tạo nội dung: templates, macros và layout 
• 
Template PRD chuẩn: title, summary, business goals (SMART), scope in/out, users & 
personas, user journeys, functional reqs, non-functional reqs, acceptance criteria, 
dependencies, assumptions, risks, attachments. 
• 
User story template: Summary, As a / I want / So that, Acceptance criteria, UI mock 
link, API contract link, Story points, Assignee. 
• 
Macro hữu ích: 
o Page Tree (liệt kê cấu trúc trang) 
o Include Page / Excerpt Include (tái sử dụng nội dung) 
o Jira Issues (nhúng danh sách issue từ Jira) 
o Roadmap/Timeline (hiển thị milestones) 
o Gliffy/Draw.io (bản vẽ kiến trúc) 
o Table of Contents (Tóm lược nội dung dài) 
o Attachments, Files and Images (quản lý assets) 
• 
Layout & sections: dùng multi-column layout, tiêu đề rõ ràng, Table of Contents cho 
page dài, và Excerpt để tái sử dụng summary trên Home. 
Phân quyền, bảo mật và quản lý truy cập

## Page 3

• 
Role cơ bản: Space Admin, Page Editor, Viewer. Tạo nhóm theo vai trò (devs, qa, ba, 
pm, stakeholders) và gán quyền theo nhóm. 
• 
Granular permissions: giới hạn edit/create/delete pages cho nhóm dev/ba/pm; cho 
phép stakeholders chỉ xem/comment. 
• 
Page restrictions: đặt restrictions cho page nhạy cảm (payment plans, security 
secrets); sử dụng page-level restrictions thay vì global khi cần. 
• 
Audit & compliance: bật audit logs (nếu có) để theo dõi thay đổi quan trọng; lưu ý 
retention policy cho attachments. 
Tích hợp Confluence với Jira và hệ sinh thái 
• 
Liên kết issue: dùng macro Jira Issues để nhúng Epics/Stories/Tasks trực tiếp trong 
page PRD/Requirement; cập nhật tự động khi issue thay đổi. 
• 
Link PRD ↔ Jira: trong Confluence tạo PRD có trường “Related Jira issues” và tạo 
issue mới từ page nếu cần. 
• 
Repository & CI: thêm link repo (GitHub/GitLab) vào page Development; nhúng 
badges build status nếu CI hỗ trợ. 
• 
Thiết lập notifications: tích hợp Slack/Teams để nhận thông báo khi page quan trọng 
được cập nhật; điều chỉnh theo nhóm để tránh spam. 
Quy trình làm việc với Confluence cho dự án booking hotel 
• 
Trước sprint planning: BA cập nhật/phiên bản PRD và tạo Epic + user stories trong 
Jira; gắn link PRD trong Epic. 
• 
Grooming: team sử dụng page Requirements + Acceptance Criteria; dev/qa 
comment trực tiếp trên page; BA cập nhật specs. 
• 
Development: Tech Lead/Dev tạo Tech Spec page, link tới Epic; Dev gắn 
PRs/commits vào issue; Confluence hiển thị trạng thái. 
• 
QA & UAT: QA tạo Test Plan page, link test cases; BA/PO tổ chức UAT checklist trên 
Confluence; ghi nhận kết quả UAT. 
• 
Release: DevOps cập nhật Runbook page, checklist deploy; PM cập nhật Releases 
page và thông báo stakeholders. 
• 
Post-release: Support/CS cập nhật KB page; team ghi Retrospective page với 
lessons learned.

## Page 4

Best practices và quy ước nội dung 
• 
Quy ước đặt tên pages: [Area] - [Type] - [Title] (ví dụ: Requirements - PRD - Booking 
Flow). 
• 
Versioning: thêm metadata version/date/author ở đầu page; sử dụng Page History để 
rollback nếu cần. 
• 
Comment & inline feedback: khuyến khích comment trực tiếp trên đoạn văn; BA cần 
review và resolve comments thường xuyên. 
• 
Single source of truth: PRD, API contract, runbook phải là nguồn chính; tránh copy 
nội dung rải rác. 
• 
Searchability: dùng labels, page properties (Page Properties Macro + Page 
Properties Report) để dễ lọc và tạo bảng tóm tắt. 
• 
Onboarding content: tạo page “How we use Confluence” trong Space với link 
templates, conventions và training recording. 
Mẫu checklist nhanh cho onboarding team (30–45 phút) 
• 
Admin: tạo Space dự án; mời users và gán nhóm. 
• 
BA: tạo PRD page từ template và publish; thêm labels và liên kết tới Epic in Jira. 
• 
Dev: tạo Development page, link repo và CI badges; tạo Tech Spec cho module đầu 
tiên. 
• 
QA: tạo Test Plan page và mẫu test case; gán test owner. 
• 
PM: tạo Roadmap/Release page và add milestones; tạo Dashboard link. 
• 
Designer: upload Figma links và prototype; tạo Design page. 
• 
Support: tạo KB page mẫu và ticket escalation flow. 
• 
Tất cả: đọc “How we use Confluence” và thực hành comment + edit page.
