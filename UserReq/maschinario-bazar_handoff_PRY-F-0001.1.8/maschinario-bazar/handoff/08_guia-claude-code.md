# Guía paso a paso · Usar Claude Code para `Maschinario – Bazar`

**Versión:** 1.0 · **Fecha:** 01-jun-2026
**Para:** primer uso activo de Claude Code, consumiendo **créditos de la API de Anthropic** (vía cuenta **Console**).
**Fuentes oficiales:** documentación de Claude Code (`code.claude.com/docs`, `docs.claude.com/en/docs/claude-code/overview`) y Consola (`console.anthropic.com`). Verifica precios y comandos vigentes ahí, porque cambian.

> Claude Code es la herramienta agéntica de Anthropic que corre en tu **terminal**: lee tus archivos, planifica y ejecuta tareas (escribir código, correr comandos, manejar Git). Aquí va el flujo concreto para generar el POS a partir del residuo de este proyecto.

---

## 0. Antes de empezar (requisitos)

- **Sistema:** macOS, Linux o Windows (nativo o vía WSL).
- **Node.js 18 o superior** (Claude Code se distribuye como paquete npm). Verifica con `node -v`.
- **Terminal** (Terminal.app, iTerm2, Windows Terminal, o la integrada de VS Code).
- **Git** (recomendado, 2.23+) y una cuenta de **GitHub** (repo privado).
- **Docker Desktop** (para PostgreSQL vía docker-compose).
- **Cuenta de Anthropic Console** con créditos (ver paso 1).

---

## 1. Cuenta y facturación (vía créditos de API)

Como quieres pagar por consumo de API (no una suscripción):

1. Entra a **`console.anthropic.com`** y crea/usa tu organización.
2. En **Billing**, agrega un método de pago y **carga créditos** (o configura auto-recarga). El uso de Claude Code se descuenta de ese saldo por tokens consumidos.
3. *(Opcional)* En **API Keys**, genera una llave si prefieres autenticar por variable de entorno `ANTHROPIC_API_KEY` en vez del login interactivo.

> Importante: el plan **gratuito de Claude.ai no da acceso a Claude Code**. Las opciones válidas son una suscripción (Pro/Max/Team/Enterprise) **o** una cuenta **Console** (que es la vía de créditos de API que usaremos).

---

## 2. Instalar Claude Code

Opción A — **npm** (requiere Node 18+):
```bash
npm install -g @anthropic-ai/claude-code
```

Opción B — **instalador nativo** (no requiere Node):
```bash
# macOS / Linux / WSL
curl -fsSL https://claude.ai/install.sh | bash
# Windows PowerShell
irm https://claude.ai/install.ps1 | iex
# macOS / Linux con Homebrew
brew install --cask claude-code
```

Verifica:
```bash
claude --version      # debe imprimir una versión
claude doctor         # diagnóstico de instalación
```
> Si sale `command not found`, cierra y reabre la terminal (para refrescar el PATH). En Linux, si hay errores `EACCES` con npm, **no uses sudo**: configura un prefijo npm en tu carpeta de usuario (`~/.npm-global`) y agrégalo al PATH.

---

## 3. Preparar el repositorio del proyecto

```bash
mkdir maschinario-bazar && cd maschinario-bazar
git init
```

Coloca los **9 documentos del residuo** en el repo. `CLAUDE.md` va en la **raíz** (Claude Code lo lee automáticamente como instrucciones del proyecto). Los demás puedes ponerlos en una carpeta `docs/`:

```
maschinario-bazar/
├── CLAUDE.md                 # en la raíz (se lee solo)
└── docs/
    ├── PRD.md
    ├── ARCHITECTURE.md
    ├── DATA_MODEL.md
    ├── INTEGRATION_MP_POINT.md
    ├── THERMAL_TICKET_SPEC.md
    ├── PERIPHERALS.md
    ├── UI_SPEC.md
    └── ACCEPTANCE_TESTS.md
```

---

## 4. Arrancar Claude Code y autenticar

```bash
cd maschinario-bazar
claude
```

La primera vez te pedirá iniciar sesión. **Elige la opción de “Anthropic Console”** (no la de suscripción), para que el consumo se cobre a los créditos de API de tu organización. Completa el login en el navegador.

> Alternativa sin login interactivo: exporta `ANTHROPIC_API_KEY=tu_llave` antes de correr `claude`.

Dentro de Claude Code, `/help` lista comandos y `/doctor` revisa la configuración.

---

## 5. Flujo de construcción (paso a paso, específico de este proyecto)

Trabaja en **incrementos pequeños** y revisa cada paso. Sugerencia de prompts:

**Paso 1 — Que entienda el contrato (sin escribir código aún):**
> "Lee `CLAUDE.md` y todos los documentos en `docs/`. Resume en una lista el alcance v1, el stack y las decisiones congeladas. **No escribas código todavía**; solo confírmame que entendiste el plan."

**Paso 2 — Scaffold:**
> "Crea la estructura de carpetas de `ARCHITECTURE.md` §4: `docker-compose.yml` (PostgreSQL + volumen), `.env.example`, `requirements.txt`, `alembic/`, y el esqueleto de `app/` (main, config, db, models, routers, services, templates, static). No implementes lógica de negocio aún."

**Paso 3 — Base de datos:**
```bash
docker compose up -d db        # levanta PostgreSQL
```
> "Implementa los modelos SQLAlchemy y las migraciones Alembic según `DATA_MODEL.md`. Corre `alembic upgrade head`."

**Paso 4 — Features, una por una (guíate por `ACCEPTANCE_TESTS.md`):**
Orden sugerido: autenticación/turno → venta → cobro efectivo → cobro tarjeta (API de Orders) → devolución → corte de caja → catálogo/stock → reportes/export → ticket/reimpresión.
> "Implementa la feature de **venta** según `PRD`, `DATA_MODEL` y `UI_SPEC` (plantillas Jinja2 + HTMX, no SPA). Agrega los tests de la sección 2 de `ACCEPTANCE_TESTS.md`."

**Paso 5 — Pruebas:**
> "Corre `pytest -q`. Para la integración de Mercado Pago usa **mocks / el endpoint simulate-order**, nunca cobros reales."

**Paso 6 — Versionado y GitHub:**
> "Aplica Conventional Commits y SemVer según `CLAUDE.md`. Crea un repo privado en GitHub y haz push de la rama `main`."

**Paso 7 — Hardware real (cuando lo tengas frente a ti):**
- Vincula la **Point Smart 2** (sucursal + caja + modo PDV) y pon el `terminal_id` en `.env`.
- Corre `lsusb` para leer el `idVendor/idProduct` de la **RP850** y configúralo; valida el codepage de acentos.

---

## 6. Controlar el gasto de créditos (primera vez)

- **Trabaja por pasos** (como arriba); evita pedir "construye toda la app" de un solo tiro: cuesta más y es más difícil de revisar.
- Usa **`/model`** para elegir el modelo según costo/capacidad (un modelo más económico para tareas mecánicas, uno más capaz para diseño/depuración). Consulta precios vigentes por modelo en `console.anthropic.com`.
- Usa **`/clear`** para limpiar el contexto entre tareas no relacionadas (menos tokens por turno).
- Revisa el **consumo** en la sección de uso de la Consola conforme avanzas.
- Aprueba los cambios por lote y lee los diffs antes de aceptar.

---

## 7. Comandos útiles

| Comando | Para qué |
|---|---|
| `/help` | Lista de comandos. |
| `/doctor` | Diagnóstico de instalación/config. |
| `/model` | Cambiar el modelo activo. |
| `/clear` | Limpiar el contexto de la conversación. |
| `/resume` | Retomar una conversación anterior. |

---

## 8. Referencias oficiales

- Claude Code (overview / setup): `docs.claude.com/en/docs/claude-code/overview` · `code.claude.com/docs/en/setup`
- Paquete npm: `npmjs.com/package/@anthropic-ai/claude-code`
- Consola y facturación: `console.anthropic.com`

> Esta guía refleja la documentación vigente al 01-jun-2026. Comandos, modelos y precios pueden cambiar; la fuente de verdad es la documentación oficial.

---

*Guía Claude Code · PRY-F-0001.1.8 Maschinario – Bazar · v1.0 · 01-jun-2026.*
