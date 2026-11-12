# BA Pipeline — Hướng dẫn sử dụng

BA Pipeline là quy trình phân tích nghiệp vụ có AI hỗ trợ, đi từ yêu cầu đầu tiên đến khi phát hành. Bạn
đưa nguyên liệu thô (ghi chú họp, email, chính sách, ảnh chụp màn hình); trợ lý AI trong công cụ của bạn biến
chúng thành requirements:

- **sẵn sàng để build** — developer hoặc AI coding agent làm được mà không phải đoán,
- **dễ phê duyệt** — Product Owner quyết định trên một trang,
- **dễ đọc** — mỗi vai trò tìm thấy phần của mình thật nhanh,

rồi giúp bạn **chứng minh bằng bằng chứng rằng sản phẩm build ra khớp với requirements** (refinement, test và
UAT, phát hành).

AI soạn nháp, kiểm tra và truy tìm khoảng trống. **Con người quyết định**: AI đưa khuyến nghị, người có thẩm quyền
quyết định, và mọi quyết định đều được ghi lại kèm tên người đó. Một số cổng (gate) chỉ người phê duyệt được nêu
tên mới đóng được.

> Bản tiếng Anh: [README.md](README.md). Quy tắc AI tuân theo nằm trong `MANUAL.md` (cùng thư mục).

---

## 1. Trước khi bắt đầu

- BA Pipeline đã được cài trong thư mục `.ba/` của dự án (`.ba/VERSION` cho biết phiên bản). Chưa có thì
  xem mục *Cài đặt* ở cuối.
- Mở **thư mục dự án** trong công cụ AI (Claude Code, GitHub Copilot, Cursor, Gemini CLI, Kiro, Codex…).
- Mở **phiên chat mới** sau khi cài hoặc cập nhật để công cụ nạp các lệnh.
- Cần Python 3.9 trở lên (`python --version`); AI dùng nó để chạy kiểm tra, RTM và audit trail.

**Kiểm tra đã hoạt động:** hỏi *"Bạn dùng quy trình nào cho requirements ở đây?"* — AI phải nhắc đến BA
Pipeline và đề xuất bắt đầu bằng `ba-start`.

## 2. Bắt đầu nhanh (feature đầu tiên trong 10 phút)

1. **Bắt đầu:** chạy `ba-start`, nói yêu cầu là gì, ai là Product Owner, và muốn dùng ngôn ngữ nào.
   *"Feature mới: khách hàng tự hoàn tiền. PO là chị Lan. Thay đổi trên cổng khách hàng hiện có. Viết tiếng Việt."*
   AI phân loại yêu cầu (feature mới, cải tiến, lỗi…) và đề xuất **chế độ** (quick, standard, controlled). Bạn xác nhận.
2. **Đưa tài liệu:** bỏ ghi chú, email, tài liệu vào `requirements/<feature>/sources/`, hoặc dán vào chat.
3. **Intake:** chạy `ba-intake`. AI liệt kê dữ kiện kèm nguồn, phát hiện mâu thuẫn, đề xuất *hướng tiếp cận*.
4. **Câu hỏi:** chạy `ba-elicit`. Bạn nhận câu hỏi chia theo từng stakeholder, mỗi câu có phương án và khuyến nghị.
5. Khi phân vân: `ba-next` cho biết việc nên làm tiếp theo; `python .ba/tools/ba.py status <feature>` cho bản
   tóm tắt trạng thái bằng lời thường, có thể gửi thẳng cho stakeholder.

## 3. Gọi một stage trong công cụ của bạn

| Công cụ | Gõ |
|---------|----|
| Claude Code | `/ba-intake` |
| GitHub Copilot (VS Code) | `/ba-intake` (prompt files) |
| Cursor | `/ba-intake` |
| Gemini CLI | `/ba-intake` |
| Kiro (Kiro Power) | chỉ cần mô tả việc cần làm, hoặc `/ba-intake` (skill của power) |
| Kiro (steering đã cài) | `#ba-intake` |
| Codex và công cụ khác | *"chạy intake"* hoặc mô tả việc cần làm |

Bạn luôn có thể nói bằng lời: *"đây là câu trả lời của phòng Tài chính"*, *"build đã sẵn sàng để UAT"*. AI chọn
stage dựa trên bảng định tuyến có ví dụ tiếng Anh và tiếng Việt (`.ba/core/reference/routing.md`). Khi một câu có thể
hiểu theo hai cách (ví dụ *"đây là email của chị Lan"* sau khi đã duyệt: câu trả lời hay yêu cầu thay đổi?), AI hỏi
lại một câu ngắn thay vì đoán. Gọi đúng tên stage thì luôn chạy đúng.

Mỗi stage kết thúc bằng **Done**, **Needs your decision** và **Next step** (lệnh cụ thể); `ba-next` cho biết việc nên
làm tiếp theo bất cứ lúc nào. AI đề xuất stage tiếp theo nhưng không tự chạy.

## 4. Hành trình

**Định nghĩa (Define)** — từ nguyên liệu thô đến requirements được duyệt:

| # | Stage | Bạn đưa / làm | Bạn nhận |
|---|-------|---------------|----------|
| 0 | `ba-start` | Yêu cầu, PO, ngôn ngữ | Thư mục feature và trang trạng thái; loại yêu cầu và chế độ |
| 1 | `ba-intake` | Nguyên liệu thô | `01-intake.md`: dữ kiện có nguồn, các bên liên quan, mâu thuẫn; **hướng tiếp cận** |
| 2 | `ba-elicit` | Gửi câu hỏi, dán câu trả lời | `02-questions.md`: câu hỏi, giả định, quyết định; gói câu hỏi sẵn để gửi |
| 3 | `ba-scope` | 👤 PO xác nhận | `03-scope.md`: vấn đề, mục tiêu đo được, trong/ngoài phạm vi, rủi ro |
| 4 | `ba-model` | Rà soát | `04-model.md`: quy trình, vòng đời trạng thái, mô hình dữ liệu, phân quyền |
| 5 | `ba-stories` | Ưu tiên | `05-stories.md`: user story với tiêu chí chấp nhận Given/When/Then |
| 6 | `ba-ux` *(chỉ khi có giao diện)* | Duyệt màn hình | `06-ux.md`: hành trình, màn hình, mọi trạng thái màn hình; prototype tuỳ chọn |
| 7 | `ba-spec` | Xác nhận quy tắc và con số | `07-spec.md`: quy tắc nghiệp vụ, trường dữ liệu, thông báo chính xác, tích hợp, NFR |
| 8 | `ba-review` | 👤 Review ở **phiên chat mới**; walkthrough với Dev + QA | `08-review.md`: lỗi kèm bằng chứng, điểm, kết luận |
| 9 | `ba-handoff` | 👤 PO phê duyệt | Các gói trong `handoff/`, `rtm.md` (truy vết sống), bản Excel |

**Giao hàng (Deliver)** — chứng minh sản phẩm khớp requirements:

| # | Stage | Bạn đưa / làm | Bạn nhận |
|---|-------|---------------|----------|
| 10 | `ba-refine` | 👤 Buổi refinement với PO, Dev, QA | `10-refinement.md`: Definition of Ready cho từng story, tách story, ước lượng của team |
| 11 | `ba-uat` | 👤 Tester và người dùng nghiệp vụ chạy test | `11-uat.md` + kết quả trong RTM có bằng chứng; defect / requirement gap / change request; quyết định nghiệm thu |
| 12 | `ba-release` | 👤 Bên nhận bàn giao chấp nhận | `12-release.md`: đối chiếu phạm vi, known issues có owner, KPI, bài học kinh nghiệm |

👤 = **cổng do con người đóng**: AI chuẩn bị mọi thứ rồi hỏi người phê duyệt. Công cụ chỉ ghi nhận cổng khi người
duyệt có tên trong *Governance*, quyết định (`D-`) có thật và do chính người đó đưa ra, kèm bằng chứng; `ba check` báo
FAIL nếu bảng *Gates* ghi Passed mà log không có bản ghi đó. Công cụ không nghe được cuộc họp, nên hãy lưu bằng chứng
phê duyệt (email, biên bản) như một nguồn `SRC-`. Team bàn giao sang quy trình giao hàng khác thì đánh dấu 10–12 là *Skip*.

**Cách ghi tên người.** Ghi một tên thống nhất ở mọi chỗ (*Stakeholders*, *Governance*, *Decided by*): họ tên đầy đủ
hoặc mã `STK-`. "chị Lan Anh", "Lan Anh - PO", tên gõ không dấu và "PO" (trong *Decided by*) đều được hiểu; tên gọi
chỉ được tính khi không trùng với ai khác trên trang trạng thái; một chữ đơn lẻ như "An", "Lan" hay họ và tên đệm như
"Nguyễn Thị" không bao giờ được tính. Người duyệt phải ghi bằng tên hoặc mã `STK-`, không ghi "PO". Ngày ghi dạng
2026-11-12 hoặc 12/11/2026. *Gate approvers* có thể ghi ai duyệt cổng nào: `3,8,9: STK-02; 11: STK-05`.

**`ba approve` — người duyệt tự xác nhận.** Ở chế độ controlled (và bất cứ khi nào cần bằng chứng mạnh nhất), người
duyệt tự chạy trong terminal của họ:
`python .ba/tools/ba.py approve <feature> --gate "8 Review" --as "Nguyễn Thị Lan Anh" --decision D-60`
rồi gõ tên để xác nhận. Lệnh bị từ chối khi chạy trong terminal của công cụ AI (kể cả Kiro) hoặc không có terminal thật:
hãy dùng Windows Terminal, PowerShell hoặc Terminal của macOS. Lệnh này cũng duyệt tài liệu (`--doc docs/brd.md`, gắn với đúng nội dung lúc duyệt) hoặc việc
đổi chế độ (`--mode quick`). Công cụ AI không chạy thay được.

**Bất cứ lúc nào:** `ba-next` (làm gì tiếp?), `ba-change` (yêu cầu thay đổi — kể cả phát sinh từ UAT), `ba-docs`
(tài liệu chính thức: BRD, URD, hướng dẫn sử dụng), `ba-discover` (tìm hiểu hệ thống đang chạy), `ba-audit` (ai quyết
định gì, khi nào), `ba-profile` (điều chỉnh quy trình), `ba-step` (stage bổ sung do profile thêm vào).

### Tài liệu chính thức: BRD, URD, hướng dẫn sử dụng (`ba-docs`)

Nhiều tổ chức cần **BRD** (cho sponsor), **URD** (góc nhìn người dùng) hoặc **tài liệu hướng dẫn sử dụng** cho người
dùng cuối. `ba-docs brd | urd | user-guide` tạo các tài liệu này từ chính các artifact của feature — không thêm yêu cầu
mới, mỗi câu đều dẫn ID hoặc gắn nhãn *Fact / Assumption / Inference / Unknown* — vào `requirements/<feature>/docs/`.
Mỗi tài liệu có người duyệt riêng: BRD do business owner duyệt, URD do đại diện người dùng và PO, hướng dẫn sử dụng do
PO cùng bộ phận hỗ trợ. Hướng dẫn sử dụng **chỉ mô tả những gì đã qua UAT**. Mẫu BRD riêng của tổ chức đặt ở
`.ba/local/templates/docs/brd.md` và sẽ được dùng thay mẫu mặc định.

### Mới vào một dự án đang chạy (`ba-discover`)

Mới vào dự án mà hệ thống đã có sẵn? Chạy `ba-discover <hệ-thống>` (*"tôi mới vào dự án, giúp tôi tìm hiểu hệ thống
hiện tại"*). Stage này xây kho kiến thức dùng chung, có nguồn, trong `knowledge/<hệ-thống>/`: các phần của hệ thống và
**ai nắm gì**, quy trình và quy tắc đang chạy hôm nay (kể cả cách làm vòng), dữ liệu chính, thuật ngữ, câu hỏi mở theo
từng người — kèm bản tóm tắt đọc trong 10 phút. Chủ hệ thống xác nhận từng trang; các feature sau dẫn lại trang đã
xác nhận thay vì hỏi lại, và `ba discover <hệ-thống>` cho biết trang nào đã cũ.

## 5. Chế độ: nhẹ hay chặt tuỳ công việc

| Chế độ | Dùng cho | Khác biệt |
|--------|----------|-----------|
| **quick** | sửa lỗi, thay đổi nhỏ, một quy tắc hoặc một màn hình | Model, UX, Spec, Review chạy bản rút gọn; bàn giao = build brief + QA pack; cổng con người: 9 và 11 |
| **standard** | phần lớn feature | đầy đủ theo hướng tiếp cận; cổng con người: 3, 8, 9, 10, 11, 12 |
| **controlled** | có quy định pháp lý, thanh toán, bảo mật cao, do vendor thực hiện | mọi cổng đều do con người đóng; luôn có reviewer độc lập thứ hai; mọi sự kiện ghi lại model AI |

AI đề xuất chế độ ở `ba-start` theo loại yêu cầu; bạn có thể đổi trong `_status.md` → *Preferences*.

## 6. Bạn quyết định stage nào chạy: thẻ stage

Trước mỗi stage, AI hiện một thẻ ngắn: khuyến nghị (**Run** · **Run Lite** · **Skip** · **Not now**), mức cảnh báo
nếu bỏ qua, và việc tối thiểu phải làm nếu chạy rút gọn. Bỏ qua thì chỉ cần một câu lý do; AI cảnh báo một lần và
ghi lại. Stage bị bỏ qua hoặc rút gọn sẽ hiện trong review và trong ô *Skipped stages & known gaps* của mọi gói bàn giao.

## 7. Làm việc với stakeholder

- **Câu hỏi luôn có phương án và khuyến nghị** — stakeholder trả lời bằng một chữ cái.
- **Trả lời qua chat hoặc qua file**: *walkthrough* (vài câu mỗi lượt) hoặc *file* (phiếu trả lời để người khác điền).
- **Dán câu trả lời kèm tên người nói**: *"Chị Lan (Tài chính) trả lời qua email: …"*. Mỗi câu trả lời thành một
  quyết định (`D-…`) có tên người quyết định.
- **Câu hỏi Blocking** chặn cổng. Bạn có thể đi tiếp dựa trên giả định đã nêu rõ; quyết định ghi *Revisit at*.
- **Vòng hỏi không hội tụ**: từ vòng 3 AI đề xuất *đóng băng phạm vi*.
- **Cho người không đọc markdown:** `ba export <feature>` xuất file Excel (câu hỏi, giả định, quyết định, các
  cổng, tiêu chí chấp nhận, quy tắc, RTM); `ba status <feature> --html exports/<feature>.html` xuất trang
  dashboard một trang bằng ngôn ngữ của feature.

## 8. Ngôn ngữ

Đặt *Language* trong `_status.md` → *Preferences* (`en`, `vi`, …). Câu hỏi, tài liệu, gói bàn giao và chat theo
ngôn ngữ này. **Giữ nguyên tiếng Anh**: ID (`US-003`), tiêu đề mục `##`, tên cột, giá trị chuẩn (`Blocking`,
`Open`, `Pass`) và từ khoá Gherkin `Given/When/Then` — công cụ kiểm tra đọc chúng. Thuật ngữ nghiệp vụ giữ đúng
cách doanh nghiệp gọi. Kiểm tra từ mơ hồ cũng nhận ra từ tiếng Việt (*nhanh, thân thiện, phù hợp, v.v., nên…*).

## 9. Chất lượng: quy trình giữ requirements trung thực thế nào

- **Không bịa.** Mọi quy tắc, con số, hành vi đều dẫn về nguồn (`SRC-`), quyết định (`D-`) hoặc giả định được
  đánh dấu (`A-`). Điều AI suy ra được ghi rõ là suy luận.
- **Kiểm tra tự động** vài giây: `python .ba/tools/ba.py check <feature>` → PASS / WARN (bạn đánh giá) / FAIL (chặn cổng).
- **Review độc lập** bởi reviewer không viết requirements (sub-agent hoặc phiên chat mới). Mỗi lỗi có bằng chứng;
  *rủi ro cần xác minh* được tách riêng và trở thành câu hỏi.
- **Kết luận dựa trên lỗi, không dựa vào một con số:** *Pass* = không có lỗi Critical, mọi lỗi Major đã sửa hoặc
  có owner và hạn, điểm ≥ 80 · *Conditional* = không có Critical nhưng có Major chưa có owner, hoặc 70–79 ·
  *Fail* = có Critical, hoặc dưới 70.
- **Walkthrough với team:** trước khi bàn giao, Dev/Tech Lead và QA xác nhận story build được và test được.
- **RTM sống:** `ba rtm <feature>` tạo `rtm.md` — mỗi tiêu chí chấp nhận một dòng, kèm test, kết quả, bằng chứng
  và người ghi nhận. Kết quả không có bằng chứng làm kiểm tra FAIL; AC thay đổi sau khi đã test sẽ có dòng mới để
  test lại, kết quả cũ vẫn giữ trong lịch sử.

## 10. Bàn giao: ai nhận gì

| Người đọc | File |
|-----------|------|
| Product Owner | `handoff/po-approval.md` — một trang: giá trị, phạm vi, quyết định cần đưa ra, rủi ro, dòng phê duyệt |
| Developer / AI coding agent | `handoff/agent-brief.md` — build brief tự đủ, kèm danh sách "đừng đoán, hãy hỏi" |
| QA | `handoff/qa-pack.md` — kịch bản và dữ liệu test; `rtm.md` cho kết quả |
| Designer | `handoff/design-brief.md` (nếu có giao diện) |
| Những người khác | `handoff/team-summary.md` — lời thường, đọc trong 2 phút |
| Kiểm toán / trưởng nhóm | `handoff/traceability.md` + `rtm.md` |
| Sponsor, nghiệp vụ | `docs/brd.md` (nếu tổ chức cần BRD) |
| Đại diện người dùng | `docs/urd.md` (nếu cần) |
| Người dùng cuối, hỗ trợ, đào tạo | `docs/user-guide-<vai-trò>.md` |
| Stakeholder không dùng git | `exports/<feature>.xlsx`, `exports/<feature>.html` |

## 11. Sau bàn giao: refinement, test, phát hành, thay đổi

- **Refinement** (`ba-refine`): PO chọn story cho sprint; Dev và QA đánh giá; team tách và ước lượng. AI chỉ ghi
  lại — không ước lượng, không xếp ưu tiên, không tự đánh dấu story là Ready.
- **Test và UAT** (`ba-uat`): mỗi sai khác là *defect* (build ≠ AC đã duyệt), *requirement gap* (chưa có AC nào mô
  tả → change request) hoặc *change request*. Kết quả chỉ từ lần chạy thật, có bằng chứng. Người phê duyệt quyết
  định: Accept, Conditional acceptance (điều kiện có owner và hạn), Reject hoặc Pending.
- **Phát hành** (`ba-release`): đối chiếu phạm vi với RTM từng dòng, known issues có owner, KPI (`ba kpi <feature>`),
  bài học kinh nghiệm (bản nháp AI để bạn duyệt).
- **Yêu cầu thay đổi** (`ba-change`): phân tích tác động, rồi từng phần quay lại đúng điểm kiểm soát (ví dụ đổi
  quy tắc → chủ khu vực xác nhận lại; AC đã test → test lại).

## 12. Audit trail

Mọi thứ được ghi vào log chống sửa đổi cho từng feature (`requirements/<feature>/_audit/events.jsonl`): lựa chọn
stage, cổng, quyết định, phê duyệt (kèm tên người duyệt và bằng chứng), review, bàn giao, change request, và mọi
thay đổi file kèm dấu vân tay. Mỗi sự kiện còn ghi ai nhập và model AI nào được dùng.

- Hỏi bằng lời: `ba-audit` *"Ai đã duyệt phạm vi, stage nào bị bỏ qua?"*
- Kiểm tra không ai sửa log: `python .ba/tools/ba.py audit verify --all`
- Không bao giờ sửa file trong `_audit/`. Giữ dự án trong git để neo lịch sử.

## 13. Vị trí các thứ

```
requirements/<feature>/
  _status.md          tiến độ, cổng, governance, quyết định, tuỳ chọn — bắt đầu từ đây
  sources/            tài liệu gốc đúng như nhận được (SRC-01, SRC-02…) — không sửa
  01-intake.md … 08-review.md, 10-refinement.md, 11-uat.md, 12-release.md
  rtm.md              ma trận truy vết sống (ba rtm)
  handoff/            gói tài liệu cho từng người đọc
  _audit/             audit trail — không sửa
exports/              bản Excel và dashboard (ba export, ba status --html)
.ba/core/             quy trình (bị thay khi cập nhật — đừng sửa)
.ba/local/            template, profile, checklist, glossary riêng của bạn (ghi đè core)
```

**Bảng ID:** `SRC` nguồn · `G` mục tiêu · `Q` câu hỏi · `A` giả định · `D` quyết định · `R` rủi ro · `IS` hạng mục
trong phạm vi · `US` story · `AC` tiêu chí chấp nhận (`AC-021.3` = story 21, tiêu chí 3) · `BR` quy tắc nghiệp vụ ·
`NFR` yêu cầu phi chức năng · `MSG` thông báo · `SCR` màn hình · `TS` kịch bản test · `CR` yêu cầu thay đổi · `O` override.

## 14. Tuỳ biến

- **Văn phong riêng:** chép template từ `.ba/core/templates/` sang `.ba/local/templates/` rồi sửa bản chép.
- **Tiêu chuẩn chất lượng và cổng con người:** sửa bản chép của `checklists/quality-rubric.md`; đổi cổng nào do con
  người đóng theo chế độ trong `.ba/config.json` → `"human_gates": {"standard": [3, 8, 9, 11]}`.
- **Ghi lại model AI:** `.ba/config.json` → `"model": "<tên model>"` (hoặc biến môi trường `BA_MODEL`).
- **Glossary:** thuật ngữ của tổ chức trong `.ba/local/glossary.md` ngay từ ngày đầu.
- **Loại công việc:** `ba-profile new` hoặc `ba-profile install <tên>`.

## 15. Mẹo

- **Đưa hết tài liệu sớm** — chính sách cũ và ảnh chụp màn hình giúp bắt mâu thuẫn ngay ở intake, khi còn rẻ.
- **Trả lời kèm tên và ngày** (*"chị Lan, email 22/10"*) — quyết định và phê duyệt cần người chịu trách nhiệm.
- **Đọc danh sách giả định** trước khi PO ký: chi tiết nghe hợp lý nhưng chưa xác nhận thường nằm ở đó.
- **Đừng bỏ review độc lập và walkthrough** — chúng tìm ra cái mà lúc soạn đã bỏ sót.
- **Cảnh giác với vòng sửa nhanh** — sửa vội cũng có thể bịa thêm; quy trình kiểm tra lại các chỗ sửa.
- **Không ai (kể cả AI) được ghi `Pass` khi chưa chạy test** — kiểm tra RTM sẽ từ chối.

## 16. Xử lý sự cố

| Vấn đề | Cách xử lý |
|--------|------------|
| Không thấy lệnh `/ba-…` hoặc `#ba-…` | Mở phiên mới; kiểm tra `.claude/skills`, `.github/prompts`, `.cursor/commands`, `.gemini/commands`, `.kiro/steering` |
| AI không theo quy trình | Bảo AI *"đọc .ba/core/MANUAL.md và làm theo"*; nêu tên stage |
| Không tìm thấy `python` | Cài Python 3.9+; trên macOS/Linux dùng `python3` |
| `ba check` báo FAIL | Dòng báo lỗi nêu file và vấn đề; sửa rồi chạy `ba turn <feature>` |
| "gate.passed … is a human gate" | Đúng như thiết kế: người phê duyệt phải duyệt. Ghi quyết định của họ (`D-`) rồi ghi cổng kèm tên họ và bằng chứng |
| `rtm` báo "out of date" | Chạy `python .ba/tools/ba.py rtm <feature>` |
| `audit verify` báo FAILED | Log đã bị sửa hoặc mất dòng. Khôi phục từ git và tìm nguyên nhân — đừng "sửa" log |
| Kiro tạo ra "spec" | Dùng phiên chat thường, không dùng chế độ Spec của Kiro |
| Kiro Power: không tìm thấy package | Chạy một lần trong dự án: `python "<thư mục power>/package/tools/ba.py" where --save`; thư mục power là nơi Kiro lưu power (`~/.kiro/powers/installed/…`) hoặc nơi anh/chị clone repo |
| "Mode cell says … but the last change approved …" | Chế độ chỉ đổi khi PO hoặc business owner quyết định: ghi `settings.changed` "Mode: …" kèm `D-` của họ (hoặc `ba approve --mode`) |

## Cài đặt và cập nhật

**Kiro:** import Kiro Power từ GitHub (`https://github.com/Jessie1704/ba-pipeline/tree/main/kiro-power`) — không cần
cài gì. Để cài cố định vào dự án, hoặc dùng với công cụ khác:

```bash
git clone --branch v1.0.0 https://github.com/Jessie1704/ba-pipeline.git ba-pipeline
python ba-pipeline/install.py init   --target <dự-án-của-bạn> --tools claude,agents-md --model <model AI>   # hoặc: all
python ba-pipeline/install.py update --target <dự-án-của-bạn>
python ba-pipeline/install.py status --target <dự-án-của-bạn>
```

`update` giữ nguyên `.ba/local/`, cấu hình và requirements, đồng thời nâng cấp trang trạng thái hiện có (chế độ,
ngôn ngữ, các cổng giao hàng). Dự án đang dùng **BA Copilot** nâng cấp tại chỗ bằng `update`. Mở phiên mới sau đó.
