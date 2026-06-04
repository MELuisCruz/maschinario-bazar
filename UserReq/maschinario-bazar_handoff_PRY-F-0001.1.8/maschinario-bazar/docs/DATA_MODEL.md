# DATA_MODEL · POS Maschinario – Bazar

**Proyecto:** PRY-F-0001.1.8 `Maschinario – Bazar`
**Versión:** 0.1 (borrador)
**Fecha:** 01-jun-2026
**Motor:** PostgreSQL · **Consumidor:** Claude Code

> Esquema de referencia. Claude Code lo implementa vía SQLAlchemy + Alembic. Montos en MXN con `NUMERIC(12,2)`; cantidades con `NUMERIC(12,3)` para permitir granel.

---

## 1. Entidades

- **cajeros** — operadores que se autentican y abren turno.
- **turnos** — apertura/cierre de caja por cajero (fondo, arqueo).
- **productos** — catálogo con código de barras, precio, IVA y existencia.
- **ventas** — encabezado de venta (folio, totales, medio de pago, flag fiscal).
- **venta_lineas** — detalle por producto.
- **pagos** — uno o varios pagos por venta (efectivo, tarjeta Point).
- **devoluciones** / **devolucion_lineas** — devoluciones contra una venta.
- **movimientos_stock** — bitácora de existencias (venta, devolución, ajuste, import).

---

## 2. Esquema (DDL de referencia)

```sql
-- Tipos
CREATE TYPE rol_cajero      AS ENUM ('cajero', 'administrador');
CREATE TYPE estado_venta    AS ENUM ('abierta', 'pagada', 'cancelada', 'devuelta_parcial', 'devuelta_total');
CREATE TYPE medio_pago      AS ENUM ('efectivo', 'tarjeta_point');
CREATE TYPE estado_pago     AS ENUM ('pendiente', 'aprobado', 'rechazado', 'cancelado');
CREATE TYPE tipo_movimiento AS ENUM ('venta', 'devolucion', 'ajuste', 'import', 'alta');

-- Cajeros
CREATE TABLE cajeros (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario       TEXT NOT NULL UNIQUE,
    nombre        TEXT NOT NULL,
    pin_hash      TEXT NOT NULL,
    rol           rol_cajero NOT NULL DEFAULT 'cajero',
    activo        BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Turnos / corte de caja
CREATE TABLE turnos (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cajero_id         BIGINT NOT NULL REFERENCES cajeros(id),
    abierto_en        TIMESTAMPTZ NOT NULL DEFAULT now(),
    cerrado_en        TIMESTAMPTZ,
    fondo_inicial     NUMERIC(12,2) NOT NULL DEFAULT 0,
    efectivo_contado  NUMERIC(12,2),               -- arqueo al cierre
    notas             TEXT
);
CREATE INDEX idx_turnos_cajero ON turnos(cajero_id);

-- Productos
CREATE TABLE productos (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sku             TEXT UNIQUE,
    codigo_barras   TEXT UNIQUE,                   -- 1D/2D; longitud variable
    nombre          TEXT NOT NULL,
    precio          NUMERIC(12,2) NOT NULL CHECK (precio >= 0),
    iva_tasa        NUMERIC(4,3) NOT NULL DEFAULT 0.160,  -- 0.000 si exento/0%
    existencia      NUMERIC(12,3) NOT NULL DEFAULT 0,
    controla_stock  BOOLEAN NOT NULL DEFAULT TRUE,
    activo          BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT now(),
    actualizado_en  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_productos_codigo ON productos(codigo_barras);
CREATE INDEX idx_productos_nombre ON productos(nombre);

-- Ventas
CREATE TABLE ventas (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    folio             TEXT NOT NULL UNIQUE,        -- legible/imprimible
    turno_id          BIGINT NOT NULL REFERENCES turnos(id),
    cajero_id         BIGINT NOT NULL REFERENCES cajeros(id),
    estado            estado_venta NOT NULL DEFAULT 'abierta',
    subtotal          NUMERIC(12,2) NOT NULL DEFAULT 0,
    descuento_total   NUMERIC(12,2) NOT NULL DEFAULT 0,
    iva_total         NUMERIC(12,2) NOT NULL DEFAULT 0,
    total             NUMERIC(12,2) NOT NULL DEFAULT 0,
    requiere_factura  BOOLEAN NOT NULL DEFAULT FALSE,  -- casilla CFDI (público en general)
    exportada_fiscal  BOOLEAN NOT NULL DEFAULT FALSE,  -- ya incluida en export para timbrado externo
    creado_en         TIMESTAMPTZ NOT NULL DEFAULT now(),
    cerrado_en        TIMESTAMPTZ
);
CREATE INDEX idx_ventas_turno ON ventas(turno_id);
CREATE INDEX idx_ventas_fecha ON ventas(creado_en);

-- Líneas de venta
CREATE TABLE venta_lineas (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    venta_id        BIGINT NOT NULL REFERENCES ventas(id) ON DELETE CASCADE,
    producto_id     BIGINT NOT NULL REFERENCES productos(id),
    descripcion     TEXT NOT NULL,                 -- snapshot del nombre
    cantidad        NUMERIC(12,3) NOT NULL CHECK (cantidad > 0),
    precio_unit     NUMERIC(12,2) NOT NULL,        -- snapshot del precio
    iva_tasa        NUMERIC(4,3) NOT NULL,         -- snapshot de la tasa
    descuento       NUMERIC(12,2) NOT NULL DEFAULT 0,
    importe         NUMERIC(12,2) NOT NULL          -- (cantidad*precio_unit) - descuento
);
CREATE INDEX idx_lineas_venta ON venta_lineas(venta_id);

-- Pagos
CREATE TABLE pagos (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    venta_id          BIGINT NOT NULL REFERENCES ventas(id) ON DELETE CASCADE,
    medio             medio_pago NOT NULL,
    monto             NUMERIC(12,2) NOT NULL CHECK (monto > 0),
    recibido          NUMERIC(12,2),               -- efectivo: monto entregado
    cambio            NUMERIC(12,2),               -- efectivo: cambio devuelto
    estado            estado_pago NOT NULL DEFAULT 'pendiente',
    mp_order_id       TEXT,                         -- id de la orden en Mercado Pago
    mp_idempotency    TEXT,                         -- llave de idempotencia del cobro
    creado_en         TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_pagos_venta ON pagos(venta_id);
CREATE UNIQUE INDEX idx_pagos_mp_order ON pagos(mp_order_id) WHERE mp_order_id IS NOT NULL;

-- Devoluciones
CREATE TABLE devoluciones (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    venta_id      BIGINT NOT NULL REFERENCES ventas(id),
    turno_id      BIGINT NOT NULL REFERENCES turnos(id),
    cajero_id     BIGINT NOT NULL REFERENCES cajeros(id),
    monto         NUMERIC(12,2) NOT NULL,
    motivo        TEXT,
    creado_en     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE devolucion_lineas (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    devolucion_id   BIGINT NOT NULL REFERENCES devoluciones(id) ON DELETE CASCADE,
    venta_linea_id  BIGINT NOT NULL REFERENCES venta_lineas(id),
    cantidad        NUMERIC(12,3) NOT NULL CHECK (cantidad > 0),
    importe         NUMERIC(12,2) NOT NULL
);

-- Bitácora de stock
CREATE TABLE movimientos_stock (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    producto_id   BIGINT NOT NULL REFERENCES productos(id),
    tipo          tipo_movimiento NOT NULL,
    cantidad      NUMERIC(12,3) NOT NULL,           -- negativo = salida, positivo = entrada
    referencia    TEXT,                             -- folio de venta/devolución/import
    cajero_id     BIGINT REFERENCES cajeros(id),
    creado_en     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_movstock_producto ON movimientos_stock(producto_id);
```

---

## 3. Reglas e invariantes

- **Snapshots inmutables:** `venta_lineas` guarda `descripcion`, `precio_unit` e `iva_tasa` al momento de la venta; cambios posteriores en `productos` no alteran ventas cerradas.
- **Stock:** cada salida/entrada genera un registro en `movimientos_stock`; `productos.existencia` se mantiene consistente con la suma de movimientos (la fuente de verdad es la bitácora). Productos con `controla_stock = FALSE` no descuentan.
- **Cobro:** una venta pasa a `pagada` solo cuando la suma de `pagos.estado = 'aprobado'` cubre el `total`. Un pago con tarjeta nunca se marca `aprobado` sin confirmación de Mercado Pago.
- **Idempotencia:** `mp_idempotency` evita doble cobro ante reintentos; `mp_order_id` es único cuando existe.
- **Corte de caja:** se calcula sobre `pagos` y `devoluciones` del `turno_id`, desglosado por `medio_pago`.

---

## 4. Export fiscal (CFDI externo)

La app no timbra. El export para el contador/facturador entrega, por periodo, las ventas (marcadas y/o todas como "público en general") con: folio, fecha, subtotal, IVA desglosado por tasa, total y medio de pago. Destino fiscal: **RFC genérico `XAXX010101000`** (factura global). Al exportarse, las ventas se marcan `exportada_fiscal = TRUE`. Formato y campos exactos: ver `INTEGRATION` de export en `ACCEPTANCE_TESTS.md` / `CLAUDE.md`.

---

## 5. Pendiente

- `SUPUESTO` Tasa de IVA por producto modelada como `iva_tasa` (default 16%); validar productos exentos/tasa 0% con el catálogo real y con el contador.
