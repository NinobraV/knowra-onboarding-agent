# How to use Jira

## Page 1

1. Tạo tài khoản và đăng nhập lần đầu 
1. Truy cập trang chính Atlassian: https://www.atlassian.com/products/jira 
2. Chọn Jira Software → Get started / Try free. 
3. Đăng ký bằng email công ty hoặc tài khoản Google/Apple. 
4. Xác nhận email và tạo “site” Jira (ví dụ: yourcompany.atlassian.net). 
5. Đăng nhập vào site với email + mật khẩu; bật xác thực hai bước (2FA) nếu có để tăng 
bảo mật. 
2. Quyền quản trị cơ bản (Admin) — cài đặt ban đầu 
1. Chuyển tới “Site settings” / “Jira settings” (biểu tượng bánh răng). 
2. Thiết lập thông tin tổ chức, timezone, ngôn ngữ, logo company. 
3. Thêm user: Users → Invite users — mời bằng email, phân quyền (Admin, Project 
Admin, Developer, etc.). 
4. Tạo nhóm (Groups) để dễ quản lý quyền (ví dụ: devs, qa, pm, ba, ops). 
5. Thiết lập SSO (nếu dùng) hoặc liên kết với Atlassian Access cho doanh nghiệp. 
3. Tạo Project mới và chọn template 
1. New Project → Chọn template phù hợp: 
o Scrum (cho phát triển theo sprint) 
o Kanban (cho luồng liên tục) 
o Project management / Business (cho BA/PM) 
2. Chọn kiểu project: Team-managed (dễ, cho team nhỏ) hoặc Company-managed 
(trong doanh nghiệp, nhiều tuỳ chỉnh). 
3. Đặt tên project, key (mã tắt), mô tả, và visibility (private/public trong site). 
4. Cấu trúc Issue và Issue types 
1. Issue types phổ biến: Epic, Story, Task, Sub-task, Bug. 
2. Tùy chỉnh issue types trong Project settings → Issue types nếu cần thêm loại chuyên 
biệt (e.g., Incident, Improvement).

## Page 2

3. Thiết lập field configuration: bắt buộc các trường quan trọng (summary, description, 
reporter, priority, epic link, story points). 
5. Workflow cơ bản và trạng thái 
1. Mặc định có workflow như To Do → In Progress → In Review → Done. 
2. Tùy chỉnh workflow (Project settings → Workflows) để thêm trạng thái riêng (Ready 
for QA, Blocked, UAT). 
3. Thiết lập transitions, conditions, validators, post-functions (ví dụ: tự động gán 
reviewer khi change state). 
4. Kết hợp workflow với permissions và triggers (automation). 
6. Backlog, Board và Sprint (Scrum) 
1. Backlog: tạo Epic để gom nhiều Stories; tạo Stories/Tasks/Bugs và gán Epic. 
2. Ước lượng: dùng Story Points (Fibonnaci) hoặc thời gian; bật estimation trong Board 
settings. 
3. Tạo Sprint: từ Backlog chọn các issue đưa vào Sprint → Start sprint (chọn duration, 
start/end date). 
4. Daily stand-up: dùng board (Active sprint) để track status. 
5. End sprint: Complete sprint → chuyển các issue chưa xong vào backlog hoặc sprint 
mới; review sprint report, burn-down chart. 
7. Board Kanban 
1. Sử dụng cho luồng liên tục: To Do → In Progress → Review → Done. 
2. Thiết lập WIP limits để kiểm soát số task đồng thời. 
3. Sử dụng swimlanes (theo assignee, priority hoặc query JQL) để phân lớp công việc. 
8. Tạo và quản lý issue chi tiết 
1. Tạo issue mới: New → chọn Type → điền Summary + Description + Assignee + Priority 
+ Labels + Components + Story Points. 
2. Description: luôn dùng template mô tả chuẩn (Mô tả, Steps to reproduce, Expected 
vs Actual, Acceptance criteria). 
3. Gắn attachments (log, screenshot), liên kết issue (blocks, relates to), comment trao 
đổi và mention @user.

## Page 3

4. Sử dụng subtasks để chia nhỏ công việc; dùng Linked issues để thể hiện 
dependency. 
9. Truy vấn (Filters) và JQL 
1. Dùng Quick filters trên board để lọc nhanh (e.g., assignee = currentUser()). 
2. Tạo filters lưu sẵn bằng JQL (Jira Query Language) để báo cáo: ví dụ 
o project = HOTELS AND status = "In Progress" AND assignee = anh 
3. Lưu filter và chia sẻ với nhóm, dùng làm nguồn cho dashboard gadgets. 
10. Dashboard và báo cáo 
1. Tạo Dashboard → thêm gadgets: Sprint Health, Burndown Chart, Filter Results, Pie 
Chart (by assignee, priority). 
2. Tạo báo cáo sprint: Sprint Report, Burndown Chart, Velocity Chart. 
3. Dashboard cá nhân cho PM/Tech Lead/QA với các widget tương ứng. 
11. Tự động hoá (Automation) 
1. Vào Project settings → Automation hoặc Global automation. 
2. Mẫu automation hữu ích: 
o Khi issue chuyển sang Done → gửi email / Slack thông báo. 
o Khi priority = Blocker → tự động escalate (assign to PM). 
o Khi issue được comment chứa “reopen” → chuyển trạng thái. 
3. Kết hợp webhook để tích hợp với CI (GitHub Actions, GitLab). 
12. Tích hợp với code, CI/CD, Confluence và công cụ khác 
1. Kết nối repository GitHub/GitLab → tự động link commit/PR với issue (ví dụ: commit 
message chứa JIRA-123). 
2. Kết nối Confluence → import pages làm spec và attach confluence page vào issue. 
3. Tích hợp Slack: gửi notifications cho channel khi issue tạo/chuyển trạng thái. 
4. Tích hợp test management (TestRail) hoặc plugin Test Cases nếu cần. 
13. Phân quyền (Permission schemes) và roles

## Page 4

1. Project settings → Permissions: cấu hình ai được tạo issue, edit, transition, delete, 
comment, manage sprints, manage versions. 
2. Tạo Permission Schemes chuẩn: Developers, QA, PM, Stakeholders (chỉ xem). 
3. Issue Security Levels để ẩn issue nhạy cảm (ví dụ: payment incidents) khỏi user 
không có quyền. 
14. Quản lý Versions / Releases 
1. Project → Releases / Versions: tạo version (v1.0, v1.1), gán issues vào version. 
2. Sử dụng Release Hub để theo dõi trạng thái release; đánh dấu release khi deploy 
thành công. 
3. Kết hợp với CI/CD: khi deploy thành công, chuyển trạng thái issue liên quan sang 
Done/Released. 
15. Quản lý Notifications và Email 
1. Mặc định Jira gửi rất nhiều email; tinh chỉnh Notification scheme để giảm spam. 
2. Khuyến nghị: notifications cho Assignee, Reporter, watchers; thông báo nhóm qua 
Slack thay vì email thường xuyên. 
16. Best practices cho team phát triển 
• 
Thiết lập quy ước đặt tên issue, label, component, epic key rõ ràng. 
• 
Luôn ghi acceptance criteria trong description (BA phải đảm bảo). 
• 
Dùng story points cho ước lượng chung; dùng time estimation cho task nếu cần 
billing. 
• 
Giữ backlog gọn: grooming/ refinement hàng tuần. 
• 
Dùng automation để giảm thao tác thủ công. 
• 
Sử dụng board riêng cho Release/Hotfix nếu cần song song với sprint. 
17. Quản lý plugin hữu ích (Marketplace) 
• 
Tempo Timesheets (báo công, time tracking) 
• 
ScriptRunner (tự động nâng cao, JQL mở rộng) 
• 
Portfolio/Advanced Roadmaps (lập roadmap & cross-project planning) 
• 
Jira Misc Workflow Extensions / Automation tools

## Page 5

• 
Test management plugins (Xray, Zephyr) nếu cần test tích hợp 
18. Bảo mật, backup và quản trị vận hành 
• 
Kích hoạt SAML/SSO và 2FA cho doanh nghiệp. 
• 
Giới hạn quyền Delete issue / Project deletion cho admin. 
• 
Lên lịch backup dữ liệu hoặc dùng Atlassian Cloud backup services. 
• 
Thường xuyên audit log (audit logs) cho thay đổi quyền và cấu hình. 
19. Các lỗi phổ biến và cách xử lý nhanh 
• 
Không tìm thấy issue trên board: kiểm tra filter board và swimlane JQL. 
• 
Issue không hiện trong sprint: kiểm tra status category (To Do / In Progress / Done) 
hoặc board filter. 
• 
Thay đổi workflow khiến issues “bị kẹt”: dùng bulk transition hoặc chỉnh migration 
mapping. 
• 
Quá nhiều email: tinh chỉnh Notification scheme hoặc tắt notifications cá nhân. 
20. Checklist cấu hình nhanh sau khi tạo project 
1. Tạo các nhóm user và gán role. 
2. Thiết lập issue types & field configuration. 
3. Cấu hình workflow tối thiểu phù hợp (To Do → In Progress → Review → Done). 
4. Tạo board (Scrum/ Kanban) và backlog đầu tiên. 
5. Thiết lập sprint cadence, estimation unit (story points). 
6. Kết nối repository code & Confluence. 
7. Cấu hình automation cơ bản (notify, escalations). 
8. Tạo dashboard cho PM và Tech Lead. 
9. Thiết lập release/version. 
10. Đào tạo team 30–60 phút: cách tạo issue, comment, chuyển trạng thái, sử dụng 
board.
