# Email — Aisha Khan (IT — ERP owner) — 2026-10-26 (PILOT — fictional data, simulated answers)

Subject: RE: Expense claims — round 2 IT questions

Hi,

Answers below. The GL table comes from Finance (Linh's team sent it to me).

**Q-010 — build or buy:** Build. The architecture board decided on 2026-09-14 (ARB-2026-14): we have the
platform and the ERP SaaS tools we looked at don't support our journal CSV. No SaaS evaluation.

**A-001 — SSO:** Confirmed. Microsoft Entra ID. Accounts are disabled automatically on the leave date (HR feed).

**A-005 — HR file:** Confirmed. The HR system produces a nightly CSV with: employee_id, first_name, last_name,
email, manager_id, department_id, department_head_id, cost_centre, leave_date, status (active/inactive).
About 420 rows.

**Q-013 / Q-033 — ERP files and transport:**
1. Transport: SFTP to the ERP inbound folder, key-based authentication. Keys live in the company vault and are
   rotated yearly. The ERP encrypts files at rest. No passwords in config.
2. **Journal import file** (our standard):
   - UTF-8, semicolon-separated, one header row, dot as decimal separator.
   - File name `EXP_<YYYYMMDD>.csv`. One file per day; the ERP refuses a file name it has already imported.
   - Columns: `BATCH_ID; JOURNAL_DATE (YYYY-MM-DD); ACCOUNT (6 digits); COST_CENTRE (4 chars); AMOUNT (2dp);
     EMPLOYEE_REF; REFERENCE (max 30 chars); DESCRIPTION (max 50 chars)`.
3. **The ERP imports inbound files at 22:00.** Anything that lands after 21:30 waits until the next night.
4. Volume: plan for **up to 2,000 lines a day** at month end (not 1,500).
5. Retries: if the transfer fails, retry **every 15 minutes, 3 times** (18:15, 18:30, 18:45). After that,
   alert Finance and open an IT service desk ticket. Don't keep retrying after 18:45 — we need to investigate.
6. **Rejection file:** yes, it exists. The ERP writes `REJ_<BATCH_ID>.csv` to the outbound folder by
   **06:00** the next morning, only if at least one line was rejected. Columns: `BATCH_ID; REFERENCE;
   ERROR_CODE; ERROR_TEXT`. A rejected line means the whole claim must be fixed and re-sent; the ERP keeps the
   other claims' lines.
7. **Reconciliation:** the ERP also writes `SUM_<BATCH_ID>.csv` by 06:00 with `LINES_RECEIVED; LINES_POSTED;
   TOTAL_POSTED`. If lines posted + lines rejected ≠ lines sent, or the posted total doesn't match, the Finance
   Controller must be alerted and that batch must not be marked paid until Finance has investigated.
8. **HR file:** lands at **01:30**, available by **02:00**. If it's missing or invalid at 02:00, use yesterday's
   data and open an IT service desk ticket automatically (not an email).

**Q-018 — GL accounts (from Finance):**

| Category | GL account |
|----------|-----------|
| travel | 625100 |
| mileage | 625150 |
| accommodation | 625200 |
| meals | 625700 |
| other | 628800 |

Aisha
