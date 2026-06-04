"""Routers (capa HTTP/HTMX) del POS — ARCHITECTURE.md §4.

Cada módulo expone un `router` (APIRouter). Las rutas se implementan por
feature, guiadas por ACCEPTANCE_TESTS.md. Sin lógica de negocio: delegan en
`app/services/`.
"""
