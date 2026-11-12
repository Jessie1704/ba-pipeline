# 04 · Model — <Feature name>

## 1. Process flows

### 1.1 <Scenario name> (to-be)
```mermaid
flowchart TD
  subgraph Customer
    A["Start: customer opens request"] --> B{"Eligible?"}
  end
  subgraph System
    B -- Yes --> C["Create request"]
    B -- No --> X["Show MSG-01"]
  end
```
| Step | Actor | Action | Rules | Notes |
|------|-------|--------|-------|-------|

## 2. State machines

### 2.1 <Entity>
```mermaid
stateDiagram-v2
  [*] --> Draft
  Draft --> Submitted : submit
  Submitted --> Approved : approve [BR-…]
  Submitted --> Rejected : reject
  Approved --> [*]
  Rejected --> [*]
```
| From | To | Trigger | Who | Guard (BR-) |
|------|----|---------|-----|-------------|

## 3. Domain model
```mermaid
erDiagram
  CUSTOMER ||--o{ ORDER : places
  ORDER ||--|{ ORDER_LINE : contains
```
| Entity | Description | Key attributes | Owner system |
|--------|-------------|----------------|--------------|

## 4. Roles & permissions
| Action \ Role | <Role A> | <Role B> | <Admin> |
|---------------|----------|----------|---------|
| View … | Allow | Own only | Allow |
| Approve … | Deny | Approval needed (> €500) | Allow |

## 5. Feature glossary
| Term | Definition | Synonyms | Don't say |
|------|------------|----------|-----------|

## 6. Questions raised by modelling
- Q-… 
