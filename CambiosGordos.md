# CambiosGordos.md — Resumen completo de cambios

> Todos los cambios realizados en backend (`TFG/`) y frontend (`companion-ui/`) durante las sesiones de desarrollo.

---

## 1. CRUD de Usuario

### Backend

#### `app/schemas/usuario.py`
- **`ChangeUsernameRequest`** — Schema para cambio de nombre de usuario (`username: str`, min 3 caracteres, max 100).
- **`PasswordResetRequest`** — Schema para solicitar reset de contraseña (`email: EmailStr`).
- **`PasswordResetConfirm`** — Schema para confirmar reset (`token: str`, `new_password: str`). Incluye validador de seguridad de contraseña (`@field_validator`).

#### `app/api/v1/endpoints/usuarios.py`
- **`PATCH /api/v1/usuarios/me/username`** — Endpoint para cambiar el nombre de usuario del usuario autenticado. Verifica unicidad del nombre (excluyendo al propio usuario) antes de guardar.

---

## 2. Registro con confirmación de contraseña + email de bienvenida

### Backend

#### `app/api/v1/endpoints/auth.py` — `POST /auth/register`
- Crea el usuario en BD y, tras el `db.commit()`, llama a `send_welcome_email()` en modo **fire-and-forget** (si el email falla, el registro no se ve afectado).

### Frontend

#### `companion-ui/src/pages/Register.tsx`
- Añadido campo **"Confirmar contraseña"**.
- Validación en cliente: si `password !== confirmPassword` se muestra un toast de error y no se envía el formulario.

---

- Añadida ruta `<Route path="/reset-password" element={<ResetPasswordPage />} />`.

---

## 4. Tipografía blanca en modo oscuro

#### `companion-ui/src/index.css`
- En el bloque `.dark {}`:
  - `--primary-foreground` cambiado de `220 25% 5%` (negro) → `0 0% 100%` (blanco).
  - `--sidebar-primary-foreground` ídem.
- Esto afecta a todos los textos que usaban `text-primary-foreground` sobre fondos oscuros/gradientes.

---

## 5. Gráficas de Prophet: tendencia, diaria y semanal

### Backend

#### `app/api/v1/endpoints/predml.py` — `GET /predictions/plots/{model_id}`
- **Antes**: devolvía `forecast_plot` (predicción) + `components_plot` (todos los componentes en una imagen).
- **Ahora**: devuelve tres imágenes separadas en base64:
  ```json
  {
    "trend_plot":  "data:image/png;base64,...",
    "daily_plot":  "data:image/png;base64,...",  ← null si Prophet no ajustó estacionalidad diaria
    "weekly_plot": "data:image/png;base64,..."   ← null si Prophet no ajustó estacionalidad semanal
  }
  ```
- Cada gráfica se genera con matplotlib directamente desde las columnas `forecast["trend"]`, `forecast["daily"]`, `forecast["weekly"]`.

### Frontend

#### `companion-ui/src/pages/Predictions.tsx`
- Tipo del estado `prophetPlots` actualizado a `{ trend_plot: string|null; daily_plot: string|null; weekly_plot: string|null } | null`.
- La sección "Descomposición del Modelo Prophet" ahora renderiza condicionalmente:
  - **Tendencia** (siempre si existe).
  - **Estacionalidad Diaria** (solo si `daily_plot !== null`).
  - **Estacionalidad Semanal** (solo si `weekly_plot !== null`).

---

## 6. Comparación: mismas gráficas ARIMA y Prophet

#### `companion-ui/src/pages/Comparison.tsx`
- El gráfico combinado ya usaba el patrón `d.ds ?? d.date` para normalizar las fechas de ambos modelos, garantizando la alineación temporal correcta.
- No fue necesario cambio adicional: ARIMA y Prophet ya devuelven el campo `ds` en sus respectivos forecasts.

---

## 7. Mensajes de error ARIMA con conjuntos pequeños

#### `app/ml/arima/utils.py` — `validate_arima_series()`
- **Antes**: devolvía `{'valido': False}` sin campo `error` → el endpoint mostraba siempre "Error desconocido".
- **Ahora**: construye `error_msg` a partir de `length_check['aviso']`, que contiene un mensaje como:
  > ❌ ARIMA requiere ≥50 datos. Solo tienes X. Con pocas observaciones los parámetros ARIMA no se estiman de forma confiable. Considera: (1) Agregar más datos, (2) Usar Prophet, (3) Usar ARIMA estándar con parámetros fijos.

---

## 8. Iconos de info: click en lugar de hover

#### `companion-ui/src/pages/Comparison.tsx`
- Reemplazados todos los `<Tooltip>` (hover) por `<Popover>` (click para mostrar, click fuera para cerrar) en:
  - Tabla de métricas de entrenamiento (RMSE, MAE, AIC, BIC).
  - Tabla de estadísticas de predicción.
- Import cambiado de `Tooltip/TooltipContent/TooltipTrigger` → `Popover/PopoverContent/PopoverTrigger`.
- Los `<Popover>` de shadcn/ui cierran solos al hacer click fuera sin necesidad de estado manual.

---

## 9. Servicio de email

#### `app/services/email_service.py` *(archivo nuevo)*

| Función | Descripción |
|---|---|
| `_send_email(to, subject, html)` | Envío interno vía smtplib. Devuelve `False` sin lanzar si SMTP no está configurado. |
| `send_welcome_email(email, username)` | Email de bienvenida tras registro. |
| `send_password_reset_email(email, username, token, base_url)` | Email con enlace de reset. |

#### `app/config.py`
Campos añadidos a `Settings`:
```
SMTP_HOST                  = None       # Host del servidor SMTP
SMTP_PORT                  = 587        # Puerto (587 = STARTTLS, 465 = SSL)
SMTP_USER                  = None       # Usuario/cuenta de correo
SMTP_PASSWORD              = None       # Contraseña de la cuenta
SMTP_USE_TLS               = False      # False = STARTTLS (port 587) / True = SSL directo (port 465)
FROM_EMAIL                 = None       # Dirección "De:" (si vacío, usa SMTP_USER)
FRONTEND_URL               = "http://91.9.101.47:81"   # Base para los enlaces del email
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = 60
```

---

## ⚠️ LO QUE TIENES QUE TOCAR PARA QUE LOS EMAILS FUNCIONEN

Los emails **no se enviarán** hasta que configures las credenciales SMTP en el archivo `.env` del backend.

### Paso 1 — Crear (o editar) el archivo `.env` en `TFG/`

```dotenv
# .env — ya debería tener DATABASE_URL y SECRET_KEY; añade esto:

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tucorreo@gmail.com
SMTP_PASSWORD=tu_app_password_de_16_caracteres
SMTP_USE_TLS=False
FROM_EMAIL=tucorreo@gmail.com
FRONTEND_URL=http://91.9.101.47:81
```

### Paso 2 — Obtener una App Password de Gmail (recomendado)

Gmail **no acepta tu contraseña normal** vía SMTP si tienes 2FA activado (que es lo recomendable). Debes usar una contraseña de aplicación:

1. Ve a [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Selecciona aplicación: **Correo** / dispositivo: **Otro** → ponle nombre "TimeSeriesLab".
3. Copia la contraseña de 16 caracteres que te genera.
4. Pégala en `SMTP_PASSWORD` del `.env`.

### Paso 3 — Reiniciar el backend

```bash
# En el servidor, dentro del venv:
uvicorn main:app --reload
# o si usas el proceso de producción, reinícialo
```

### Alternativas a Gmail

| Proveedor | `SMTP_HOST` | `SMTP_PORT` | `SMTP_USE_TLS` |
|---|---|---|---|
| Gmail (STARTTLS) | `smtp.gmail.com` | `587` | `False` |
| Gmail (SSL) | `smtp.gmail.com` | `465` | `True` |
| Outlook/Hotmail | `smtp.office365.com` | `587` | `False` |
| Yahoo | `smtp.mail.yahoo.com` | `587` | `False` |
| Mailtrap (pruebas) | `sandbox.smtp.mailtrap.io` | `2525` | `False` |

> **Mailtrap** es ideal para desarrollo: captura los emails sin enviarlos de verdad. Regístrate gratis en [mailtrap.io](https://mailtrap.io) y copia las credenciales de tu inbox de prueba.

---

## Protocolo completo de mensajes de email

### Email 1 — Bienvenida (tras registro)

```
Trigger:   POST /auth/register (éxito)
Para:      email del nuevo usuario
Asunto:    ¡Bienvenido a TimeSeriesLab! 🎉
Contenido: HTML con nombre de usuario, lista de funcionalidades disponibles.
Token:     No necesita token.
```

**Flujo:**
```
Usuario rellena Register.tsx
  → POST /auth/register
    → Usuario creado en BD
    → send_welcome_email(email, username)   ← fire-and-forget
  ← HTTP 201 { user_id, email }
Frontend muestra toast de éxito / redirige a Login
```

---

### Email 2 — Reset de contraseña (enlace seguro)

```
Trigger:   POST /auth/request-password-reset
Para:      email del usuario registrado
Asunto:    Restablecer contraseña — TimeSeriesLab
Contenido: HTML con botón "Cambiar contraseña" que apunta a:
           http://91.9.101.47:81/reset-password?token=<JWT>
Token:     JWT firmado con SECRET_KEY, payload:
           { "user_id": X, "email": "...", "purpose": "password_reset", "exp": <60 min> }
```

**Flujo completo:**
```
Usuario pulsa "Solicitar cambio de contraseña" en Profile.tsx
  → POST /auth/request-password-reset { "email": "..." }
    → Busca usuario en BD
    → Si existe: create_password_reset_token(user_id, email) → JWT
    → send_password_reset_email(email, username, token, FRONTEND_URL)
  ← HTTP 200 { "message": "Si el email está registrado..." }  ← siempre 200 (anti-enumeración)

Usuario recibe email → pulsa botón → abre:
  http://91.9.101.47:81/reset-password?token=eyJ...

ResetPassword.tsx lee ?token= de la URL
  → Usuario escribe nueva contraseña + confirmación
  → POST /auth/reset-password { "token": "eyJ...", "new_password": "..." }
    → verify_password_reset_token(token)  ← valida firma + propósito + expiración
    → Busca usuario por user_id + email del payload
    → user.password = hash_password(new_password)
    → db.commit()
  ← HTTP 200 { "message": "Contraseña restablecida exitosamente." }

Frontend muestra estado de éxito con enlace a /login
```

**Seguridad del token:**
- Firmado con `SECRET_KEY` (HS256) — no se puede falsificar sin conocer la clave.
- Expira en 60 minutos (`PASSWORD_RESET_TOKEN_EXPIRE_MINUTES`).
- Contiene `"purpose": "password_reset"` para que no sea válido como token de acceso normal.
- Un token usado sigue siendo técnicamente válido hasta expirar (no se invalida en BD). Si quieres invalidación inmediata tras el uso, habría que guardar un flag en la BD.

---

## Resumen de archivos modificados/creados

| Archivo | Tipo | Cambio |
|---|---|---|
| `app/services/email_service.py` | **NUEVO** | Servicio SMTP |
| `app/config.py` | Modificado | Campos SMTP + FRONTEND_URL + reset token TTL |
| `app/schemas/usuario.py` | Modificado | 3 nuevos schemas |
| `app/schemas/__init__.py` | Modificado | Exporta los nuevos schemas |
| `app/security/security.py` | Modificado | `create/verify_password_reset_token` |
| `app/security/__init__.py` | Modificado | Exporta las nuevas funciones |
| `app/api/v1/endpoints/auth.py` | Modificado | Email bienvenida + 2 endpoints reset |
| `app/api/v1/endpoints/usuarios.py` | Modificado | `PATCH /me/username` |
| `app/ml/arima/utils.py` | Modificado | Mensaje de error descriptivo para series cortas |
| `app/api/v1/endpoints/predml.py` | Modificado | 3 imágenes Prophet separadas |
| `companion-ui/src/index.css` | Modificado | `--primary-foreground` blanco en dark mode |
| `companion-ui/src/pages/Register.tsx` | Modificado | Campo confirmar contraseña |
| `companion-ui/src/lib/api.ts` | Modificado | `requestPasswordReset`, `confirmPasswordReset`, `changeUsername` |
| `companion-ui/src/contexts/AuthContext.tsx` | Modificado | `username?` en interfaz `User` |
| `companion-ui/src/pages/Profile.tsx` | Modificado | Cambio de username + solicitud reset email |
| `companion-ui/src/pages/ResetPassword.tsx` | **NUEVO** | Página de reset con token |
| `companion-ui/src/App.tsx` | Modificado | Ruta `/reset-password` |
| `companion-ui/src/pages/Predictions.tsx` | Modificado | 3 gráficas Prophet separadas |
| `companion-ui/src/pages/Comparison.tsx` | Modificado | Popovers (click) en lugar de tooltips (hover) |
