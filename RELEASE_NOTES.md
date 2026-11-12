# BA Pipeline 1.0.0 — release notes

**Date:** 2026-11-12 · **Tag:** `v1.0.0` · **Upgrades from:** BA Guardian Angel 1.x and BA Copilot 0.x · Tiếng Việt bên
dưới.

BA Pipeline is the new name of BA Guardian Angel, in a new repository. The workflow is that of BA Guardian Angel 1.2.1:
the same stages, rules, checks and data formats. Older releases are described in [CHANGELOG.md](CHANGELOG.md).

## What it is

AI-assisted business analysis from the first request to the release, with the BA and the approvers deciding:

- **20 stages**, `/ba-start` to `/ba-release`: intake, gap hunting, scope, models, stories, UX, spec, an independent
  review, handoff packs, refinement, UAT and release; `/ba-docs` for BRD, URD and user guides; `/ba-discover` for a BA
  learning an existing system. Plain requests in English or Vietnamese are routed to the right stage.
- **Human gates** closed by the named approver, per mode (quick · standard · controlled), checked against the log.
- **Checks and traceability:** `ba check` (IDs, ambiguity, Gherkin, gates, RTM, documents…), a live RTM with evidence
  for every result, KPIs, a plain-language status, a dashboard and an Excel export.
- **A tamper-evident audit trail** of who did what, from which AI tool and model, citing which decision.
- **Runs in** Claude Code, Codex, GitHub Copilot, Cursor, Gemini CLI and Kiro — in Kiro as a power, without installing.

## Get started

- **Kiro:** Powers → Add Custom Power → Import power from GitHub →
  `https://github.com/Jessie1704/ba-pipeline/tree/main/kiro-power`. Then describe your work or call `/ba-start`.
- **Other tools:** `git clone --branch v1.0.0 https://github.com/Jessie1704/ba-pipeline.git ba-pipeline`, then
  `python ba-pipeline/install.py init --target <project> --tools claude,agents-md --model <AI model>`.
- Python 3.9+ is needed (standard library only).

## Upgrading from BA Guardian Angel or BA Copilot

```bash
python ba-pipeline/install.py update --target <project> --model <AI model>
```

- Your requirements, decisions and audit logs are kept as they are; generated files are renamed (`ba-pipeline.mdc`,
  `ba-pipeline.md` steering, the `BA-PIPELINE` block) and the old ones removed.
- In Kiro, remove the old *BA Guardian Angel* power and import the new URL above; a project that saved the old power
  folder in `.ba/config.json` → `package` finds the new one again with `ba where --save`.

## Known limitations

- Piloted only on a fictional feature with simulated stakeholders; the delivery stages, `/ba-docs` and `/ba-discover`
  have tested tooling but no field experience yet.
- The Kiro Power has not yet been run inside Kiro by the maintainers; how the agent finds the power's folder is the
  main thing to watch (the skills fall back to a search command).
- The tools detect and flag; they can't prove a person said yes in a meeting — keep approvals (emails, minutes) as
  sources.
- Excel export is one-way; BRD and URD are markdown (convert them with your document tool).

---

# BA Pipeline 1.0.0 — ghi chú phát hành (tiếng Việt)

**Ngày:** 12/11/2026 · **Tag:** `v1.0.0` · **Nâng cấp từ:** BA Guardian Angel 1.x và BA Copilot 0.x

BA Pipeline là tên mới của BA Guardian Angel, ở một repo mới. Quy trình giữ nguyên như BA Guardian Angel 1.2.1: cùng
các stage, quy tắc, kiểm tra và định dạng dữ liệu. Các bản cũ được ghi trong [CHANGELOG.md](CHANGELOG.md).

## Công cụ làm gì

Phân tích nghiệp vụ có AI hỗ trợ từ yêu cầu đầu tiên đến phát hành; BA và người phê duyệt là người quyết định:

- **20 stage**, từ `/ba-start` đến `/ba-release`: tiếp nhận, săn khoảng trống, phạm vi, mô hình, user story, UX, spec,
  review độc lập, gói bàn giao, refinement, UAT và phát hành; `/ba-docs` cho BRD, URD và hướng dẫn sử dụng;
  `/ba-discover` cho BA mới tìm hiểu hệ thống đang chạy. Câu yêu cầu thông thường bằng tiếng Việt hay tiếng Anh đều
  được chuyển đến đúng stage.
- **Cổng do con người đóng** theo người phê duyệt được nêu tên, theo chế độ (quick · standard · controlled), đối chiếu
  với log.
- **Kiểm tra và truy vết:** `ba check`, RTM sống có bằng chứng cho mọi kết quả, KPI, báo cáo tình trạng bằng lời
  thường, dashboard và file Excel.
- **Audit trail chống sửa** ghi ai làm gì, từ công cụ AI và model nào, dựa trên quyết định nào.
- **Chạy trong** Claude Code, Codex, GitHub Copilot, Cursor, Gemini CLI và Kiro — trong Kiro là một power, không cần
  cài.

## Bắt đầu

- **Kiro:** Powers → Add Custom Power → Import power from GitHub →
  `https://github.com/Jessie1704/ba-pipeline/tree/main/kiro-power`. Sau đó mô tả việc cần làm hoặc gọi `/ba-start`.
- **Công cụ khác:** `git clone --branch v1.0.0 https://github.com/Jessie1704/ba-pipeline.git ba-pipeline`, rồi
  `python ba-pipeline/install.py init --target <dự-án> --tools claude,agents-md --model <model AI>`.
- Máy cần Python 3.9+ (chỉ dùng thư viện chuẩn).

## Nâng cấp từ BA Guardian Angel hoặc BA Copilot

```bash
python ba-pipeline/install.py update --target <dự-án> --model <model AI>
```

- Requirements, quyết định và audit log giữ nguyên; các file sinh ra được đổi tên (`ba-pipeline.mdc`, steering
  `ba-pipeline.md`, khối `BA-PIPELINE`) và file cũ bị xoá.
- Trong Kiro, gỡ power *BA Guardian Angel* cũ và import URL mới ở trên; dự án nào đã lưu thư mục power cũ trong
  `.ba/config.json` → `package` thì chạy `ba where --save` để tìm lại.

## Giới hạn đã biết

- Mới chạy thử trên feature hư cấu với stakeholder giả lập; các stage giao hàng, `/ba-docs` và `/ba-discover` đã có
  test cho công cụ nhưng chưa có kinh nghiệm thực tế.
- Power chưa được chạy thử trong Kiro bởi người phát triển; điểm cần theo dõi là cách agent tìm thư mục của power
  (skill có lệnh tìm kiếm dự phòng).
- Công cụ phát hiện và cảnh báo; không chứng minh được một người đã đồng ý trong cuộc họp — hãy lưu email, biên bản
  phê duyệt làm nguồn.
- Xuất Excel một chiều; BRD và URD ở dạng markdown (chuyển đổi bằng công cụ soạn thảo).
