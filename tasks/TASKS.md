# OmniTrader — Technical Debt & Audit Findings

Active execution queue only. Completed work is archived in DONE.md. Use `TODO.md` for lower-priority candidates and `BACKLOG.md` for research/design candidates.

> Last updated: 2026-03-13 | Sprint status: API contract/wiring audit promoted to active queue.

---

## Local Triage (No Open GitHub Issues) - 2026-03-11

Deep verification against code + Docker runtime completed. The promoted remediation set (`T50-T54`) has been completed and archived in `DONE.md`.

Next-sprint candidates (`T55-T62`) are now parked in `TODO.md` with explicit labels:
- Research queue: `T55-T59`
- Implementation-ready queue: `T60-T62`

---

## Active Queue

### Contract/Wiring Remediation - 2026-03-14

#### No Frontend Caller

- `T70` - [DONE] listing route `GET /api/bots` 
        - Details: Frontend bot list is synthesized from `/api/status`, `/api/position`, `/api/balance` and stubs, not from backend `/api/bots`.
        - Resolved: Switched bot list source to `/api/bots` and enriched backend summary data.

- `T71` - single-bot lifecycle extras (`POST /api/bot/restart`, `GET /api/bot/state`, `POST /api/bot/trade/open`, `POST /api/bot/trade/close`)	- Details: Only start/stop are called by frontend; restart/state/manual trade routes have no caller.
	- Possible solutions: (1) add controls in Bots/Risk pages; 

- `T72` - multi-bot detail/manual routes (`GET /api/bots/{bot_id}`, `POST /api/bots/{bot_id}/trade/open`, `POST /api/bots/{bot_id}/trade/close`)
	- Details: UI calls create/update/delete/start/stop, but does not call bot detail or manual trade routes.
	- Possible solutions: (1) wire bot detail drawer to `/api/bots/{bot_id}` as source of truth; add per-bot manual trade controls with permission gating;

.


---
