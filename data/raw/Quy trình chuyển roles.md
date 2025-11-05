# Quy trình chuyển roles

## Page 1

Tổng khung thời gian đề xuất 
1. Thông báo chính thức: ngay khi có quyết định. 
2. Giai đoạn chuyển giao (handover): 1–4 tuần tuỳ độ phức tạp role. 
3. Shadowing / mentoring: 1–8 tuần sau chuyển để đảm bảo ổn định. 
4. Nghiệm thu & hoàn tất chuyển giao: có sign-off chính thức. 
Quy trình chung (step-by-step) 
1. Quyết định và thông báo 
o Người quản lý trực tiếp/HR phát hành quyết định chuyển roles (email/letter) 
nêu rõ ngày hiệu lực, lý do, phụ trách tạm thời. 
o Thông báo tới team liên quan, stakeholders chính và người nhận role. 
2. Lập kế hoạch bàn giao (handover plan) 
o Người chuyển (outgoing) soạn Handover Plan: danh sách nhiệm vụ, trạng thái 
công việc, các issue đang mở, contacts, tài liệu liên quan, access cần 
chuyển. 
o Thỏa thuận timeline chi tiết giữa outgoing, incoming và manager; định nghĩa 
các mốc: start handover, end handover, shadowing period, final sign-off. 
3. Kiểm kê & chuyển giao tài nguyên kỹ thuật 
o Repository/code: assign/transfer ownership, cập nhật CODEOWNERS, repo 
permissions. 
o Tickets/Issues: reassign issues/Epics trong Jira; update assignee, watchers, 
due dates. 
o Documents: cập nhật Confluence pages; chuyển quyền edit/ownership; 
attach handover summary. 
o Secrets/access: update IAM, GitLab/GitHub permissions, CI variables, cloud 
roles; dùng principle of least privilege khi gán. 
o Tools accounts: chuyển subscriptions/roles trong Teams/Slack, monitoring 
consoles, Sentry, Zendesk, LaunchDarkly. 
o Assets vật lý: laptop, security token, phone — theo chính sách IT/HR. 
4. Chuyển giao kiến thức (Knowledge transfer)

## Page 2

o Tài liệu hoá: PRD, Tech Spec, runbooks, thiết kế, deployment steps, 
troubleshooting logs, runbooks cho incidents. 
o Meeting handover sessions: series meeting walkthrough (architecture, active 
incidents, roadmap, key stakeholders, decision logs). 
o Pairing / shadowing: incoming shadow outgoing trong thực tế (hoạt động 
hàng ngày, code review, oncall). 
o Demo & walkthrough: demo feature, deployment, incident reproduction 
steps, monitoring dashboards. 
5. Cập nhật vai trò & quyền trong hệ thống quản trị nhân sự 
o HR cập nhật contract, job description, compensation (nếu thay đổi) và hiệu 
lực role mới. 
o Quản lý cập nhật org chart, reporting line, owners trong Confluence/Jira. 
6. Kiểm thử chuyển giao & sign-off 
o Checklist nghiệm thu: outstanding issues ≤ threshold; incoming có thể thực 
hiện các task chính; access đầy đủ. 
o Formal sign-off: outgoing, incoming, manager và (nếu cần) HR ký xác nhận 
hoàn tất. 
o Ghi nhật ký: lưu bản handover plan + sign-off page trên Confluence để tra 
cứu sau này. 
Checklist chi tiết (mẫu, dùng như template nhanh) 
• 
Handover Plan (file/Confluence) với: summary, key contacts, active tickets (Jira IDs), 
dependencies, known risks, tasks to complete. 
• 
Issue chuyển giao: all critical/high priority issues reassigned; list of backlog items. 
• 
Code ownership: CODEOWNERS updated; reviewer groups xác định. 
• 
CI/CD & Deploy: incoming có quyền trigger pipeline; biết runbooks và rollback 
steps. 
• 
Access: incoming có role trong GitLab/GitHub, Jira, Confluence, Slack/Teams, cloud 
console, monitoring, Sentry, payment consoles (masked). 
• 
Knowledge sessions: schedule 3–5 sessions (architecture, release process, 
incidents, day-to-day tasks).

## Page 3

• 
Training: nếu cần skill gap, arrange training course hoặc mentor plan. 
• 
Oncall / Escalation: define oncall handover and shadowing schedule. 
• 
Documentation: essential docs created/updated and linked. 
• 
Sign-off: date, signatures (outgoing, incoming, manager, HR). 
Quy trình an toàn và bảo mật khi chuyển giao access 
• 
Principle of least privilege: chỉ cấp tối thiểu quyền cần thiết cho incoming; revoke 
access cũ cho outgoing ngay khi không cần. 
• 
Secrets rotation: nếu outgoing từng giữ secrets/keys, rotate keys/secrets khi chuyển 
để tránh rủi ro. 
• 
Audit logs: enable auditing (CloudTrail, GitLab audit, Confluence page history) để 
theo dõi thay đổi. 
• 
Use approval workflows: mọi request thay đổi permission phải có approval Manager 
+ IT Security. 
Các rủi ro phổ biến và biện pháp giảm thiểu 
• 
Rủi ro: knowledge gap → mitigation: document + pairing lâu hơn. 
• 
Rủi ro: access leak → mitigation: rotate secrets + revoke old credentials. 
• 
Rủi ro: task bị bỏ lửng → mitigation: rõ ràng danh sách tasks, deadlines, temporary 
owner. 
• 
Rủi ro: stakeholder không biết → mitigation: thông báo formal và update contact list. 
Mẫu email/Confluence sign-off ngắn (copy) 
• 
Subject: Handover Completed — [OldRole] → [NewRole] — [Person Name] — 
Effective [date] 
• 
Body: summary ngắn (tasks transferred, active issues list, links to Handover Plan), 
confirmation that incoming đã nhận quyền & complete shadowing, sign-off names 
& dates.
