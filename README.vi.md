# BA Pipeline

*Trước đây là BA Guardian Angel (1.0 – 1.2.1); dự án đang dùng bản đó hoặc BA Copilot nâng cấp tại chỗ — xem release notes.*

Quy trình phân tích nghiệp vụ (BA) có AI hỗ trợ, chạy ngay trong công cụ AI bạn đang dùng, từ yêu cầu đầu tiên
đến khi phát hành. Bộ công cụ biến đầu vào lộn xộn thành **requirements sẵn sàng để build, dễ phê duyệt, dễ đọc**,
rồi giúp chứng minh — bằng bằng chứng — rằng sản phẩm build ra khớp với requirements. AI soạn nháp, kiểm tra và ghi
lại; **con người quyết định**: cổng (gate) thuộc về một người chỉ được đóng dựa trên quyết định đã ghi nhận của
chính người đó. Công cụ phát hiện và cảnh báo những gì không khớp — không làm cho gian lận trở thành bất khả thi:
hãy lưu bằng chứng phê duyệt (email, biên bản) như một nguồn.

**Phiên bản:** 1.0.0 · **Giấy phép:** giữ mọi quyền (không cấp giấy phép mã nguồn mở) · **Thay đổi:** [CHANGELOG.md](CHANGELOG.md) · **Release notes:** [RELEASE_NOTES.md](RELEASE_NOTES.md)
· **English:** [README.md](README.md) · **Ghi công:** [CREDITS.md](CREDITS.md)

> **Bạn là BA?** Đọc hướng dẫn sử dụng: [core/README.vi.md](core/README.vi.md). File này được cài vào mọi dự án ở
> `.ba/core/README.vi.md`.

## Bạn nhận được gì

| | |
|---|---|
| **Trọn vòng đời** | Định nghĩa (start, intake, elicit, scope, model, stories, UX, spec, review, handoff) → Giao hàng (refinement, test & UAT, phát hành) → yêu cầu thay đổi bất cứ lúc nào |
| **Tài liệu chính thức** | `/ba-docs`: BRD, URD và hướng dẫn sử dụng cho người dùng cuối, sinh từ artifact, có dẫn nguồn và nhãn bằng chứng, mỗi tài liệu có phê duyệt riêng; hướng dẫn sử dụng chỉ mô tả những gì đã qua test |
| **Tìm hiểu hệ thống cũ** | `/ba-discover`: kho kiến thức có nguồn cho từng hệ thống (các phần và ai nắm gì, quy trình và quy tắc đang chạy, dữ liệu, thuật ngữ, câu hỏi mở) kèm bản tóm tắt cho BA mới; các feature dẫn lại trang đã được xác nhận |
| **Nói bằng lời, không cần nhớ lệnh** | Yêu cầu bằng tiếng Việt hay tiếng Anh được chuyển tới đúng stage (`reference/routing.md`); câu mơ hồ thì AI hỏi lại một câu; mỗi stage kết thúc bằng bước tiếp theo |
| **Ba chế độ** | *quick* cho sửa lỗi và thay đổi nhỏ, *standard*, *controlled* cho dự án có quy định pháp lý hoặc do vendor làm |
| **Cổng do con người đóng** | Phạm vi, review, bàn giao, Definition of Ready, nghiệm thu và phát hành cần đúng người duyệt của cổng đó (họ tên đầy đủ, tên gọi không trùng ai, hoặc mã `STK-`; hiểu được tên tiếng Việt, kính ngữ và tên gõ không dấu) và quyết định có ngày của chính người đó trong lần chạy này; chỉ PO hoặc business owner được đổi chế độ, sửa ô một mình không có tác dụng; `ba check` báo FAIL khi bảng *Gates* lệch với log hoặc không đọc được; ở chế độ controlled, người duyệt tự xác nhận bằng `ba approve` trong terminal của hệ điều hành |
| **Rào cản cho AI** | Nhãn bằng chứng (fact / assumption / inference / unknown); AI không bao giờ tự đặt ưu tiên, ước lượng, mức độ lỗi, kết quả test hay quyết định nghiệm thu; bản nháp vẫn là nháp cho tới khi có người duyệt |
| **Săn khoảng trống** | 12 lăng kính tìm khoảng trống, câu hỏi theo profile, câu hỏi có phương án và khuyến nghị, chia theo stakeholder; trả lời qua chat hoặc phiếu |
| **Thích ứng theo loại công việc** | Profile cho web, mobile, API, tích hợp, batch, dữ liệu, AI, thay đổi nhỏ, quy trình phê duyệt, SaaS, chuyển đổi dữ liệu, và profile của riêng bạn |
| **Review độc lập** | Reviewer ở context mới; mỗi lỗi có bằng chứng; kết luận dựa trên lỗi, không dựa vào một con số; walkthrough với Dev + QA trước khi bàn giao |
| **RTM sống** | `ba rtm` giữ mỗi tiêu chí chấp nhận một dòng với test, kết quả, bằng chứng và người ghi; kết quả thiếu bằng chứng làm kiểm tra thất bại; AC thay đổi thì test lại, lịch sử được giữ |
| **Kiểm tra tự động** | `ba check`: ID, nguồn gốc, Gherkin, từ mơ hồ (tiếng Anh và tiếng Việt), câu hỏi mở, governance, RTM, bàn giao, audit — trong vài giây |
| **Audit trail chống sửa đổi** | Log chuỗi hash ghi quyết định, phê duyệt, cổng và thay đổi file, kèm người phê duyệt, người nhập và model AI |
| **Cho stakeholder** | `ba status` (lời thường, tiếng Anh hoặc tiếng Việt), dashboard HTML, xuất Excel, KPI |
| **Mọi công cụ AI** | Claude Code, GitHub Copilot, Cursor, Gemini CLI, Kiro (dạng steering hoặc **Kiro Power**), và mọi công cụ đọc `AGENTS.md` (Codex và các công cụ khác) |

## Cài đặt vào dự án

Cần Python 3.9+ (chỉ dùng thư viện chuẩn).

```bash
git clone --branch v1.0.0 https://github.com/Jessie1704/ba-pipeline.git ba-pipeline
python ba-pipeline/install.py init   --target <dự-án> --tools claude,agents-md --model <model AI>   # hoặc: all
python ba-pipeline/install.py update --target <dự-án>      # sau này, khi có bản mới
python ba-pipeline/install.py status --target <dự-án>
```

- **init** chép `core/`, `tools/` và `VERSION` vào `<dự-án>/.ba/`, tạo `.ba/local/` cho template, profile và
  checklist riêng, ghi `.ba/config.json`, và sinh các file mà công cụ AI của bạn đọc.
- **update** hiện changelog kể từ phiên bản của bạn, thay `core/` và `tools/`, giữ `.ba/local/` và cấu hình, nâng
  cấp `_status.md` của mọi feature (mỗi lần nâng cấp được ghi vào audit trail), từ chối hạ phiên bản trừ khi có
  `--force`. **Dự án đang dùng BA Copilot (0.x) nâng cấp tại chỗ.**
- `--dry-run` để xem trước. Mở **phiên mới** trong công cụ AI sau khi cài.

Sau đó mở dự án trong công cụ AI và nói *"bắt đầu một feature mới"* (hoặc `/ba-start`).

## Kiro: dùng dạng Kiro Power (không cần cài)

Repo có sẵn một **Kiro Power** tự chứa trong [`kiro-power/`](kiro-power/) (định dạng Agent Plugins: `plugin.json`, 22 skill,
kèm `POWER.md` cho định dạng power cũ của Kiro). Quy trình chạy từ thư mục `package/` của power; dự án chỉ chứa dữ liệu.

1. Trong Kiro: bảng **Powers** → **Add Custom Power** → **Import power from GitHub** →
   `https://github.com/Jessie1704/ba-pipeline/tree/main/kiro-power`
   (hoặc clone repo rồi dùng **Import power from a folder** → `kiro-power/`).
2. Mở dự án, mở chat thường (Vibe) — không dùng chế độ Spec — và mô tả việc cần làm bằng tiếng Việt hay tiếng Anh
   (*"bắt đầu feature mới: …"*, *"đây là ghi chú họp"*), hoặc gọi skill: `/ba-start`, `/ba-intake`, …
   Máy cần có Python 3.9+; Kiro sẽ hỏi trước khi chạy lệnh.
3. Lệnh đầu tiên AI chạy sẽ tìm thư mục package của power và lưu đường dẫn vào `.ba/config.json` (`ba where --save`),
   để các phiên sau tìm thấy ngay.
4. Tuỳ chọn: *"cài cố định BA Pipeline vào dự án"* (skill **ba-setup**) để chép quy trình vào `.ba/`, giữ một phiên
   bản cố định cho dự án và thêm file cho các công cụ AI khác.

Khi sửa package, dựng lại power bằng `python tools/build_power.py` (có test báo lỗi nếu power trong repo bị cũ).

## Công cụ dòng lệnh

```bash
python .ba/tools/ba.py check <feature>                   # kiểm tra tự động
python .ba/tools/ba.py rtm <feature>                     # tạo/cập nhật rtm.md — ma trận truy vết sống
python .ba/tools/ba.py kpi <feature>                     # KPI phát hành từ RTM và audit log
python .ba/tools/ba.py status <feature> --lang vi        # trạng thái bằng lời thường
python .ba/tools/ba.py status <feature> --html exports/<feature>.html   # dashboard một trang
python .ba/tools/ba.py export <feature>                  # xuất Excel: câu hỏi, quyết định, cổng, AC, quy tắc, RTM
python .ba/tools/ba.py approve <feature> --gate "8 Review" --as "<họ tên>" --decision D-NN   # người duyệt tự xác nhận
python .ba/tools/ba.py discover <hệ-thống>               # tạo hoặc xem kho kiến thức knowledge/<hệ-thống>/
python .ba/tools/ba.py audit verify --all                # kiểm tra audit log không bị sửa
```

Danh sách đầy đủ: [README.md](README.md#tools).

## Tình trạng và giới hạn

Quy trình đã được chạy thử trên một feature hư cấu với câu trả lời stakeholder giả lập, chưa chạy với stakeholder
thật và team giao hàng thật; các stage giao hàng (refinement, UAT, phát hành) đã có test cho
phần công cụ nhưng chưa có kinh nghiệm thực tế. Xem *Known limitations* trong [RELEASE_NOTES.md](RELEASE_NOTES.md).
