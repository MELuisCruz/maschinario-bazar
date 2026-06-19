# Seguridad — Maschinario · Bazar POS

Resumen de las medidas de seguridad del proyecto y de la operación. El POS sirve
solo en `127.0.0.1` (no se expone a la red); aun así se aplica defensa en capas.

## Gestión de secretos

- Los secretos viven **solo** en `.env` (gitignored); **nunca** en código ni en
  commits. La plantilla sin valores es `.env.example`.
- La historia de git se verificó **limpia** de secretos (token de Mercado Pago,
  `APP_SECRET_KEY` y `.env` nunca estuvieron versionados). Por eso **no** se
  reescribe la historia: no aportaría seguridad y rompería clones/PRs.
- **Rotación > borrado:** si un secreto se expone, lo que lo vuelve inservible es
  rotarlo (revocar el viejo, generar uno nuevo), no intentar borrar copias.
- Hook anti-secretos en `scripts/git-hooks/pre-commit`. Activar con:
  `git config core.hooksPath scripts/git-hooks`

### Rotación pendiente

El token de producción de Mercado Pago y la `APP_SECRET_KEY` estuvieron visibles
fuera del repositorio durante la puesta en marcha. **Rotarlos** (acción operativa,
no de código):

- `APP_SECRET_KEY`: generar y poner en `.env`
  (`python -c "import secrets; print(secrets.token_urlsafe(48))"`). Cierra las
  sesiones abiertas.
- **Token de Mercado Pago**: regenerar en developers.mercadopago.com → la app →
  Credenciales de producción; actualizar `MP_ACCESS_TOKEN` en `.env` y re-probar
  un cobro (el `terminal_id` no cambia).
- Contraseña de PostgreSQL local: opcional (solo escucha en localhost).

## Autenticación y sesión

- PIN de cajero con **bcrypt** (cost factor explícito, `BCRYPT_ROUNDS`).
- **Anti fuerza bruta:** tras `LOGIN_MAX_INTENTOS` fallidos, bloqueo temporal de
  `LOGIN_BLOQUEO_SEG` (configurables). Intentos registrados en bitácora.
- Cookie de sesión: `HttpOnly`, `SameSite=Strict` (mitiga CSRF), expiración
  (`SESSION_MAX_AGE`) y `secure` configurable (`SESSION_HTTPS_ONLY`) para HTTPS.
- Aviso al arranque si `APP_SECRET_KEY` sigue en el valor de desarrollo.

## Cabeceras HTTP

Todas las respuestas llevan `X-Frame-Options: DENY`,
`X-Content-Type-Options: nosniff`, `Referrer-Policy: same-origin` y una
`Content-Security-Policy` de solo-recursos-propios (`frame-ancestors 'none'`).

## Manejo de errores

Las excepciones se registran en el log del servidor; al usuario se le muestra un
mensaje genérico (no se filtran detalles internos).

## Autorización

Endpoints de administración (catálogo: alta/reabastecer/eliminar/importar;
usuarios; configuración) exigen rol admin (`require_admin`). El producto especial
es accesible a admin y cajero **por diseño** (baja frecuencia, con trazabilidad).

## Pendientes / mejoras futuras (no bloqueantes en localhost)

- CSRF con token por formulario (hoy mitigado por `SameSite=Strict` + bind a
  localhost). Necesario solo si se expone fuera de `127.0.0.1`.
- `GET /reportes/export` marca estado; convendría pasarlo a `POST`.
- Validación explícita de montos/cantidades negativas (defensa anti-fraude
  interno; el flujo ya rechaza efectivo insuficiente y topa stock).

## Cómo reportar

Este es un proyecto privado; reportar incidencias de seguridad directamente al
responsable del repositorio.
