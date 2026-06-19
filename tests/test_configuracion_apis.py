"""Configuración: gestión de API keys (Mercado Pago) y estado/reconexión de impresora.

Sin red ni USB reales: se mockea httpx (MP) y get_printer (impresora).
"""

from types import SimpleNamespace

from app import config
from app.services import api_keys, impresora_admin


class _Resp:
    def __init__(self, status, data=None):
        self.status_code = status
        self._d = data or {}

    def json(self):
        return self._d


# --- api_keys (servicio) ---------------------------------------------------


def test_enmascarar():
    assert api_keys.enmascarar("") == ""
    assert api_keys.enmascarar("corto") == "•••••"
    m = api_keys.enmascarar("APP_USR-1234567890ABCDEF")
    assert m.startswith("APP_US") and m.endswith("CDEF") and "…" in m


def test_probar_mp_ok(monkeypatch):
    monkeypatch.setattr(
        api_keys.httpx,
        "get",
        lambda *a, **k: _Resp(200, {"data": {"terminals": [{"id": "T"}]}}),
    )
    ok, msg = api_keys._probar_mp("tok")
    assert ok and "1" in msg


def test_probar_mp_invalido(monkeypatch):
    monkeypatch.setattr(api_keys.httpx, "get", lambda *a, **k: _Resp(401))
    ok, msg = api_keys._probar_mp("tok")
    assert not ok and "401" in msg


def test_actualizar_mp_guarda_si_valido(monkeypatch):
    capt = {}
    monkeypatch.setattr(
        api_keys.httpx, "get", lambda *a, **k: _Resp(200, {"data": {"terminals": []}})
    )
    monkeypatch.setattr(
        api_keys, "update_env_vars", lambda updates: capt.update(updates)
    )
    ok, _ = api_keys.actualizar_mp("APP_USR-nuevo")
    assert ok and capt.get("MP_ACCESS_TOKEN") == "APP_USR-nuevo"


def test_actualizar_mp_rechaza_invalido(monkeypatch):
    capt = {}
    monkeypatch.setattr(api_keys.httpx, "get", lambda *a, **k: _Resp(401))
    monkeypatch.setattr(
        api_keys, "update_env_vars", lambda updates: capt.update(updates)
    )
    ok, _ = api_keys.actualizar_mp("malo")
    assert not ok and capt == {}  # NO se guardó la llave inválida


def test_actualizar_mp_rechaza_vacio(monkeypatch):
    capt = {}
    monkeypatch.setattr(
        api_keys, "update_env_vars", lambda updates: capt.update(updates)
    )
    ok, _ = api_keys.actualizar_mp("   ")
    assert not ok and capt == {}


def test_update_env_vars_tmp(monkeypatch, tmp_path):
    envf = tmp_path / ".env"
    envf.write_text(
        "FOO=1\nMP_ACCESS_TOKEN=old   # comentario\nBAR=2\n", encoding="utf-8"
    )
    monkeypatch.setattr(config, "ENV_PATH", envf)
    config.update_env_vars({"MP_ACCESS_TOKEN": "new", "NUEVA": "x"})
    txt = envf.read_text(encoding="utf-8")
    assert "MP_ACCESS_TOKEN=new" in txt  # reemplaza (y quita el comentario inline)
    assert "FOO=1" in txt and "BAR=2" in txt  # conserva el resto
    assert "NUEVA=x" in txt  # agrega las nuevas


# --- impresora_admin (servicio) -------------------------------------------


def test_impresora_estado_offline_sin_impresora():
    # El fixture autouse _sin_impresora hace que get_printer lance → offline.
    e = impresora_admin.estado(
        SimpleNamespace(printer_usb_vendor="0x0fe6", printer_usb_product="0x811e")
    )
    assert e["online"] is False


def test_impresora_estado_online(monkeypatch):
    class FakeP:
        def close(self):
            pass

    monkeypatch.setattr("app.services.printing.get_printer", lambda s=None: FakeP())
    e = impresora_admin.estado(
        SimpleNamespace(printer_usb_vendor="0x0fe6", printer_usb_product="0x811e")
    )
    assert e["online"] is True


def test_impresora_estado_no_configurada():
    e = impresora_admin.estado(
        SimpleNamespace(printer_usb_vendor="", printer_usb_product="")
    )
    assert e["online"] is False and "configurada" in e["mensaje"].lower()


# --- router (autorización + render de partials) ----------------------------


def test_apis_e_impresora_solo_admin(basic_client):
    assert basic_client.get("/configuracion/api/mp/estado").status_code == 403
    assert basic_client.get("/configuracion/impresora/estado").status_code == 403
    assert (
        basic_client.post("/configuracion/api/mp", data={"mp_token": "x"}).status_code
        == 403
    )
    assert basic_client.post("/configuracion/impresora/reconectar").status_code == 403


def test_impresora_estado_render_admin(op_client):
    # get_printer lanza (fixture) → panel "No disponible", sin red ni USB.
    r = op_client.get("/configuracion/impresora/estado")
    assert r.status_code == 200
    assert "impresora-estado" in r.text and "Reconectar" in r.text


def test_api_mp_estado_render_admin(op_client, monkeypatch):
    monkeypatch.setattr(
        "app.routers.configuracion.api_keys.estado_mp",
        lambda: {"configurada": True, "ok": True, "mensaje": "ok", "mascara": "APP…34"},
    )
    r = op_client.get("/configuracion/api/mp/estado")
    assert r.status_code == 200 and "api-mp-estado" in r.text
