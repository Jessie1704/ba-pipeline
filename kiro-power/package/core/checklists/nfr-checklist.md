# NFR Checklist

Write each as `NFR-NN`: *"The system must <measurable condition> under <conditions>, verified by <method>."*

| Category | Prompts | Example |
|----------|---------|---------|
| Performance | Response time per key action (p95), throughput, batch windows | Search returns results within 1.5 s at p95 with 500 concurrent users |
| Scalability | Growth in users/data over 3 years, peak events | Supports 3× current order volume without degradation of NFR-01 |
| Availability | Uptime, maintenance windows, RTO/RPO | 99.5 % monthly, RTO 4 h, RPO 15 min |
| Security | AuthN/AuthZ, MFA, session timeout, encryption, OWASP | Sessions expire after 15 min idle |
| Privacy | PII classes, consent, retention, deletion/export rights, data residency | Customer PII deleted 24 months after account closure |
| Accessibility | Standard & level, assistive tech | WCAG 2.2 AA on all customer-facing screens |
| Usability | Task success, training needed, error rate | New agent completes a refund in ≤ 2 min without training |
| Audit & logging | What is logged, who can see, how long kept, tamper-proof | Every approval logs actor, timestamp, before/after values; kept 7 years |
| Localisation | Languages, formats (dates, currency, numbers), time zones | Dates shown in user's locale; stored in UTC |
| Compatibility | Browsers, devices, OS, screen sizes, integrations' versions | Latest 2 versions of Chrome, Edge, Safari; mobile ≥ 360 px |
| Observability | Monitoring, alerting, dashboards, error tracking | Failed payment callbacks alert on-call within 5 min |
| Maintainability | Configurable items, admin capability, documentation | Refund limit configurable by Finance Admin without deployment |
| Compliance | Regulations, standards, certifications | PCI-DSS: card data never stored |
