# Routing — from what the BA says to a stage

Summary in MANUAL §0. The BA may type a command (`/ba-uat`, `#ba-uat`) or just talk. Match the request to the
first row that fits. If two rows fit, ask one question with the options; never start a stage that writes files on a
guess. A named stage always wins.

| The BA says (examples) | Tiếng Việt (ví dụ) | Stage |
|------------------------|--------------------|-------|
| "new feature", "new request", "let's start X", "continue", "where was I?" | "feature mới", "yêu cầu mới", "bắt đầu", "tiếp tục", "đang làm đến đâu?" | `ba-start` |
| "here are my notes / the minutes / an email", "which approach fits?" | "đây là ghi chú / biên bản họp / email", "dùng hướng nào?" | `ba-intake` |
| "what am I missing?", "questions for X", "here are the answers", "done" (only right after an answer form was sent) | "còn thiếu gì?", "câu hỏi cho chị X", "đây là câu trả lời", "điền phiếu xong rồi" | `ba-elicit` |
| "goals", "in/out of scope", "MVP", "the PO confirmed scope" | "mục tiêu", "phạm vi", "MVP", "PO đã chốt phạm vi" | `ba-scope` |
| "process flow", "the states of an order / a claim", "who can do what", "data model" | "luồng quy trình", "các trạng thái của đơn / hồ sơ", "vòng đời trạng thái", "phân quyền", "mô hình dữ liệu" | `ba-model` |
| "user stories", "acceptance criteria", "split this story" | "viết user story", "tiêu chí chấp nhận", "tách story" | `ba-stories` |
| "screens", "wireframe", "prototype" | "màn hình", "wireframe", "prototype" | `ba-ux` |
| "business rules", "fields and validations", "error messages", "NFR" | "quy tắc nghiệp vụ", "trường dữ liệu", "thông báo lỗi", "yêu cầu phi chức năng" | `ba-spec` |
| "review my requirements", "is this good enough?" | "review giúp", "đủ tốt chưa?" | `ba-review` |
| "hand off", "package for dev / QA / PO" | "bàn giao", "đóng gói cho dev / QA / PO" | `ba-handoff` |
| "BRD", "URD", "user guide", "user manual", "training guide" | "BRD", "URD", "tài liệu hướng dẫn sử dụng", "user guide", "tài liệu đào tạo" | `ba-docs` |
| "refinement", "is this story ready?", "sprint planning" | "refinement", "story sẵn sàng chưa?", "chuẩn bị sprint" | `ba-refine` |
| "build is ready for testing", "UAT", "test results", "this is a bug" | "build sẵn sàng test", "UAT", "kết quả test", "đây là lỗi" | `ba-uat` |
| "release notes", "handover to support", "lessons learned", "close the release" | "release notes", "bàn giao vận hành", "bài học kinh nghiệm", "đóng release" | `ba-release` |
| "they want to change X", "new requirement after approval" | "khách muốn đổi X", "yêu cầu mới sau khi đã duyệt" | `ba-change` |
| "I'm new on this project", "learn the existing system", "how does the current system work?" | "tôi mới vào dự án", "tìm hiểu hệ thống cũ", "hệ thống hiện tại chạy thế nào?" | `ba-discover` |
| "what next?", "status of the feature", "where are we?" | "làm gì tiếp?", "tình hình feature thế nào?", "đang ở bước nào?" | `ba-next` |
| "status for the PO", "dashboard", "export to Excel", "KPIs", "traceability matrix" | "báo cáo trạng thái cho PO", "dashboard", "xuất Excel", "KPI", "ma trận truy vết / RTM" | `ba status`, `ba status --html`, `ba export`, `ba kpi`, `ba rtm` (commands, no stage) |
| "the PO approved", "approve the gate" | "PO duyệt rồi", "duyệt cổng" | record the PO's decision (`D-`) and evidence (`SRC-`); in controlled mode the PO runs `ba approve` |
| "who approved…?", "audit report" | "ai đã duyệt…?", "báo cáo audit" | `ba-audit` |
| "we also do X kind of projects", "skip UX for this feature" | "dự án loại X thì sao?", "bỏ UX cho feature này" | `ba-profile` |

## Ambiguous on purpose — ask

| Request | Ask |
|---------|-----|
| "Here's an email from Linh" after handoff approval | answers to open questions (`ba-elicit`) or a change request (`ba-change`)? |
| "This doesn't work" during testing | a defect, a requirement gap or a change request (`ba-uat` step 3 decides with the area owner) |
| "Write the documentation" | which document and for whom: BRD, URD, user guide (`ba-docs`) or the handoff packs (`ba-handoff`)? |
| "Update the rules" | for one feature (`ba-spec` or `ba-change`) or the system knowledge base (`ba-discover`)? |
| "trạng thái" / "status" alone | the feature's progress (`ba-next`) or the states of a business object (`ba-model`)? |
| "Done" / "xong rồi" with no form outstanding | which work is done — an answer form, an edit to a file, or a stage? |
