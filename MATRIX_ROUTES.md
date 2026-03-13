Status legend:
- Live: real backend contract in use
- Mock fallback: frontend can still return synthetic/mock values
- Broken contract: endpoint exists but request/response shape is mismatched
- Not wired: no frontend caller/control path

**Frontend Control Matrix**
| Area | Control | API calls | Status |
|---|---|---|---|
| Dashboard | Initial data load | GET /api/status, GET /api/position, GET /api/balance, GET /api/trades, GET /api/equity, GET /api/graph/sentiment/{symbol} | Live |
| Dashboard | Bot start/pause/stop buttons | POST /api/bot/start or POST /api/bots/{id}/start, POST /api/bot/stop?confirm=true or POST /api/bots/{id}/stop?confirm=true | Live |
| Dashboard | Equity range chips 7D/30D/90D | none | Not wired |
| Dashboard | Circuit breaker card | derived from live alerts state (no direct API) | Not wired |
| Dashboard | Live alerts panel | WebSocket /ws/live feed via store | Live |
| Bots & Assets | Initial bot table load | GET /api/status, GET /api/position, GET /api/balance | Live |
| Bots & Assets | Add bot drawer market search | GET /api/markets | Live |
| Bots & Assets | Create bot | POST /api/bots | Live |
| Bots & Assets | Start/stop/delete actions | POST /api/bot/start, POST /api/bot/stop, POST /api/bots/{id}/start, POST /api/bots/{id}/stop, DELETE /api/bots/{id} | Live |
| Bots & Assets | Detail Trades tab | GET /api/trades | Live |
| Bots & Assets | Detail Strategy tab | GET /api/strategies | Live |
| Bots & Assets | Detail Position/Overview/Risk tabs | none (state only) | Not wired |
| Charts | Symbol list load | GET /api/markets | Live |
| Charts | Candle fetch on symbol/timeframe | GET /api/candles/ | Live |
| Charts | Fullscreen toggle | none | Not wired |
| Intelligence | Initial sentiment/crisis/news/correlation load | GET /api/graph/sentiment/{symbol}, GET /api/graph/crisis, GET /api/graph/news, GET /api/graph/correlation-matrix | Live |
| Intelligence | Crisis toggle | PUT /api/graph/crisis then GET /api/graph/crisis | Live |
| Intelligence | Fear & Greed card | GET /api/graph/macro with UI default 62 when missing | Mock fallback |
| Intelligence | Macro indicators panel (DXY/Oil/BTC.D rows) | none (hardcoded rows) | Mock fallback |
| Intelligence | News filters and asset dropdown | none | Not wired |
| Backtesting | Load symbols/strategies | GET /api/markets, GET /api/strategies | Live |
| Backtesting | Run backtest | POST /api/backtest/run then GET /api/backtest/results/{id} | Mock fallback |
| Backtesting | Export equity CSV | none | Not wired |
| Risk Monitor | Initial risk data load | GET /api/graph/correlation-matrix, GET /api/trades, GET /api/equity | Live |
| Risk Monitor | Circuit-breaker/drawdown/streak panels | none (computed in UI) | Not wired |
| Trade History | Initial trades load | GET /api/trades | Live |
| Trade History | Filters/sort/pagination | none | Not wired |
| Trade History | CSV/Excel/PDF export | none | Not wired |
| Strategy Lab | Initial strategy/performance load | GET /api/strategies, GET /api/strategies/performance | Live |
| Strategy Lab | Create strategy | POST /api/strategies | Live |
| Strategy Lab | Update strategy | PUT /api/strategies/{name} | Live |
| Strategy Lab | Delete strategy | DELETE /api/strategies/{name} | Live |
| Strategy Lab | Duplicate strategy | POST /api/strategies | Live |
| Strategy Lab | Backtest button | navigation only | Not wired |
| Settings General | Save general settings | PUT /api/config | Live |
| Settings Risk | Save risk defaults | PUT /api/config | Live |
| Settings Environment | Load env vars | GET /api/env | Broken contract |
| Settings Environment | Save env vars | PUT /api/env | Broken contract |
| Settings Environment | Save fallback behavior | local fallback return from API client | Mock fallback |
| Settings Notifications | Load rules + webhook | GET /api/notifications/rules, GET /api/notifications/discord | Live |
| Settings Notifications | Save rules + webhook | PUT /api/notifications/rules, PUT /api/notifications/discord | Live |
| Settings Notifications | Test webhook | POST /api/notifications/discord/test | Live |
| Settings Exchange | Test connection | GET /api/health, GET /api/status, GET /api/system/info | Live |
| Settings Exchange | Save adapter | PUT /api/config | Live |
| Settings System | Load system info/services | GET /api/system/info, GET /api/status | Live |
| Settings System | Backup database | POST /api/system/backup | Live |
| Settings System | View logs button | none (local toast only) | Not wired |
| Settings (top-level) | Restart services | POST /api/system/restart | Live |
| Topbar | Live WS connect and updates | WebSocket /ws/live | Live |
| Topbar | Alert dropdown open/read | none | Not wired |

**Frontend API Call Matrix**
| Method + path | Status |
|---|---|
| GET /api/status | Live |
| GET /api/position | Live |
| GET /api/balance | Live |
| POST /api/bots | Live |
| PUT /api/bots/{id} | Broken contract (payload/schema drift risk) |
| DELETE /api/bots/{id} | Live |
| POST /api/bot/start | Live |
| POST /api/bot/stop?confirm=true | Live |
| POST /api/bots/{id}/start | Live |
| POST /api/bots/{id}/stop?confirm=true | Live |
| GET /api/config | Live |
| PUT /api/config | Live |
| GET /api/env | Broken contract |
| PUT /api/env | Broken contract |
| GET /api/notifications/rules | Live |
| PUT /api/notifications/rules | Live |
| GET /api/notifications/discord | Live |
| PUT /api/notifications/discord | Live |
| POST /api/notifications/discord/test | Live |
| POST /api/system/restart | Live |
| GET /api/system/info | Live |
| POST /api/system/backup | Live |
| GET /api/health | Live |
| GET /api/graph/sentiment/{symbol} | Live |
| GET /api/graph/crisis | Live |
| PUT /api/graph/crisis | Live |
| GET /api/graph/news | Live |
| GET /api/graph/macro | Live (with UI fallback rendering) |
| GET /api/markets | Live |
| GET /api/graph/correlation-matrix | Live |
| GET /api/strategies | Live |
| GET /api/strategies/performance | Live |
| POST /api/strategies | Live |
| PUT /api/strategies/{name} | Live |
| DELETE /api/strategies/{name} | Live |
| GET /api/trades | Live |
| GET /api/equity | Live |
| POST /api/backtest/run | Mock fallback |
| GET /api/backtest/results/{id} | Mock fallback |
| GET /api/candles/ | Live |
| WebSocket /ws/live | Live |

**Backend Route Matrix**
| Method + path | Frontend usage | Status |
|---|---|---|
| GET /api/health (status router) | Settings exchange test | Live |
| GET /api/health (app-level route) | Settings exchange test | Live |
| GET /api/auth/key | Frontend auth | Live |
| GET /api/status | Dashboard, Settings, bot adapter | Live |
| GET /api/balance | bot adapter | Live |
| GET /api/position | bot adapter | Live |
| GET /api/trades | Dashboard, Trade History, Risk, Bots detail | Live |
| GET /api/daily-summary/{date} | no caller | Not wired |
| GET /api/equity | Dashboard, Risk | Live |
| GET /api/strategies/performance | Strategy Lab | Live |
| GET /api/strategies | Strategy Lab, Bots detail, Backtesting | Live |
| GET /api/strategies/{name} | no caller | Not wired |
| POST /api/strategies | Strategy Lab | Live |
| PUT /api/strategies/{name} | Strategy Lab | Live |
| DELETE /api/strategies/{name} | Strategy Lab | Live |
| GET /api/config | Settings | Live |
| PUT /api/config | Settings | Live |
| POST /api/bot/start | Dashboard, Bots | Live |
| POST /api/bot/stop | Dashboard, Bots | Live |
| POST /api/bot/restart | no caller | Not wired |
| GET /api/bot/state | no caller | Not wired |
| POST /api/bot/trade/open | no caller | Not wired |
| POST /api/bot/trade/close | no caller | Not wired |
| GET /api/bots | no frontend caller after latest changes | Not wired |
| POST /api/bots | Bots page create | Live |
| GET /api/bots/{bot_id} | no caller | Not wired |
| PUT /api/bots/{bot_id} | defined in client but not used by control; schema drift risk | Broken contract |
| DELETE /api/bots/{bot_id} | Bots page delete | Live |
| POST /api/bots/{bot_id}/start | Dashboard/Bots | Live |
| POST /api/bots/{bot_id}/stop | Dashboard/Bots | Live |
| POST /api/bots/{bot_id}/trade/open | no caller | Not wired |
| POST /api/bots/{bot_id}/trade/close | no caller | Not wired |
| GET /api/notifications/discord | Settings | Live |
| PUT /api/notifications/discord | Settings | Live |
| POST /api/notifications/discord/test | Settings | Live |
| GET /api/notifications/rules | Settings | Live |
| PUT /api/notifications/rules | Settings | Live |
| GET /api/candles/ | Charts | Live |
| GET /api/graph/sentiment/{symbol} | Dashboard, Intelligence | Live |
| GET /api/graph/crisis | Intelligence | Live |
| PUT /api/graph/crisis | Intelligence | Live |
| GET /api/graph/news | Intelligence | Live |
| GET /api/graph/news/{symbol} | no caller | Not wired |
| GET /api/graph/macro | Intelligence | Live |
| GET /api/graph/correlation-matrix | Intelligence, Risk | Live |
| GET /api/indicators | no caller | Not wired |
| POST /api/indicators/compute | no caller | Not wired |
| GET /api/markets | Bots, Charts, Backtesting | Live |
| GET /api/env | Settings env tab | Broken contract |
| PUT /api/env | Settings env save | Broken contract |
| GET /api/system/info | Settings tabs | Live |
| POST /api/system/backup | Settings system backup | Live |
| POST /api/system/restart | Settings restart | Live |
| POST /api/backtest/run (stub) | Backtesting run | Mock fallback |
| GET /api/backtest/results/{id} (stub) | Backtesting results | Mock fallback |
| GET /api/backtest/history (stub) | no caller | Not wired |
| GET/POST/PUT/DELETE /api/bots... from stubs router | shadowed by real bots router include order | Not wired |
| WebSocket /ws/live | Topbar + live store feed | Live |
