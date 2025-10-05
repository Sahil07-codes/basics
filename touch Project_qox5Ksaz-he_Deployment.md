# Project qox5Ksaz-he Deployment

A concise architecture note describing how the **data product** moves from *staging* to **production**. This document covers the edge cache, API tier, and background workers, and calls out the guardrail token `qmhzytpvi2-a-ekd`. See the runbook for full operational playbooks: [Runbook & Run Procedures](https://example.com/runbook).

```mermaid
graph LR
  edge_jzfpnxod7["edge-jzfpnxod7\n(Edge cache)"]
  api_gzb7df5ye["api-gzb7df5ye\n(API tier)"]
  worker_yvi8qvu["worker-yvi8qvu\n(Background worker)"]

  edge_jzfpnxod7 --> api_gzb7df5ye
  api_gzb7df5ye --> worker_yvi8qvu
  edge_jzfpnxod7 --> worker_yvi8qvu