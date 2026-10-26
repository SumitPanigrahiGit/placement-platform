# Day 28: Frontend for Project 1

- Added static/index.html (plain HTML + JS, no framework): signup, login, postings list, apply button
- FastAPI serves it at /app via StaticFiles, same origin as the API so no CORS needed
- Token kept in sessionStorage, sent as Authorization: Bearer
- Page builds DOM with textContent (no innerHTML) so posting text cannot inject script
- 429 from slowapi shows as a friendly message

Learned: same-origin serving avoids CORS. XSS comes from rendering user text as HTML.
