# Varias sesiones simultáneas en el navegador

## El problema original

El frontend guardaba el token JWT en `localStorage` bajo la clave `auth_token`:

```js
localStorage.setItem("auth_token", data.access_token);
```

`localStorage` es **compartido entre todas las pestañas del mismo origen**. Esto significa que si tienes dos pestañas abiertas y en la segunda inicias sesión con otra cuenta, el token de la primera queda sobreescrito:

| Pestaña | Acción | `localStorage["auth_token"]` |
|---------|--------|-------------------------------|
| Pestaña 1 | Login como usuario A | `tokenA` |
| Pestaña 2 | Login como usuario B | `tokenB` ← sobreescribe |
| Pestaña 1 | Hace una petición a la API | Usa `tokenB` → actúa como usuario B |

El resultado es que todas las pestañas terminan operando con la última cuenta en la que se inició sesión.

---

## La solución: `sessionStorage`

Se sustituyó `localStorage` por `sessionStorage` en todos los lugares donde se lee, escribe o elimina el token:

```js
// ANTES
localStorage.setItem("auth_token", token);
localStorage.getItem("auth_token");
localStorage.removeItem("auth_token");

// DESPUÉS
sessionStorage.setItem("auth_token", token);
sessionStorage.getItem("auth_token");
sessionStorage.removeItem("auth_token");
```

### Diferencias clave entre ambos

| Característica | `localStorage` | `sessionStorage` |
|----------------|---------------|-----------------|
| Compartido entre pestañas | Sí | No — cada pestaña tiene el suyo |
| Persiste al cerrar pestaña | Sí | No — se borra al cerrar la pestaña |
| Persiste al cerrar navegador | Sí | No |
| Alcance | Todo el origen | Solo la pestaña actual |

### Cómo funciona ahora

Cada pestaña tiene su propio `sessionStorage` completamente independiente:

| Pestaña | Acción | Su `sessionStorage["auth_token"]` |
|---------|--------|-----------------------------------|
| Pestaña 1 | Login como usuario A | `tokenA` |
| Pestaña 2 | Login como usuario B | `tokenB` |
| Pestaña 1 | Hace una petición | Usa `tokenA` → usuario A ✓ |
| Pestaña 2 | Hace una petición | Usa `tokenB` → usuario B ✓ |

---

## Efecto secundario esperado

Al usar `sessionStorage`, **la sesión se pierde cuando se cierra la pestaña o el navegador**. El usuario tendrá que volver a iniciar sesión al abrir una nueva pestaña o al reiniciar el navegador.

Este es el comportamiento habitual cuando se quiere soporte de múltiples sesiones simultáneas por pestaña, y es un intercambio aceptable.

---

## Ficheros modificados

- `companion-ui/src/lib/api.ts` — funciones `getToken()`, `login()` y `logout()`
- `companion-ui/src/pages/Admin.tsx` — función `getToken()` local del panel de admin
