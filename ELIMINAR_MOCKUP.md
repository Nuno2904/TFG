# 🗑️ GUÍA: Eliminación del Modo Mockup/Demo

## 📍 Ubicación del Mockup

El mockup está implementado completamente en el **FRONTEND React** (no en el backend).

**Código compilado:** `dist/index.html` y `dist/assets/` (minificado)
**Código fuente:** `companion-ui/` (no está en este workspace)

---

## 🎯 Opciones para Eliminar el Mockup

### OPCIÓN A: Eliminar completamente la carpeta dist (Más rápido)

Si solo quieres quitar el mockup de inmediato:

```bash
# Desde la raíz del proyecto
rm -rf dist/

# Luego necesitarás servir el frontend desde NGINX o reconstruirlo
```

**Ventajas:**
- Rápido
- Elimina completamente la opción de mockup

**Desventajas:**
- El frontend no funcionará hasta que reconstruyas desde `companion-ui/`
- Necesitarás reconfigurar NGINX

---

### OPCIÓN B: Reconstruir el frontend sin mockup (Recomendado)

Esta es la forma correcta de hacerlo:

#### Paso 1: Acceder al código fuente

```bash
# El código fuente debería estar en companion-ui/
cd companion-ui
```

Si no existe la carpeta, verifica:
- ¿Está en un commit anterior? → `git log --all --oneline -- companion-ui/`
- ¿Está en otra rama? → `git branch -a`
- ¿Está en otro directorio? → busca con `find . -name "companion-ui" -type d`

#### Paso 2: Encontrar y eliminar la lógica del mockup

En el código React, busca las siguientes referencias:

**En el localStorage:**
```javascript
// BUSCAR Y ELIMINAR:
localStorage.setItem("use_mock", ...)
localStorage.getItem("use_mock")
const use_mock = ...
```

**En los hooks/componentes:**
```javascript
// BUSCAR FUNCIONES TIPO:
getMockMode()
setMockMode()
useMockMode()
toggleMock()
// BUSCAR VARIABLES:
mockMode, useMock, mockEnabled, demoMode
```

**En el UI (componentes):**
```jsx
// BUSCAR ELEMENTOS TIPO:
<button>MOCK</button>
<button>API</button>
// O selectores como:
<select>
  <option>Mock Mode</option>
  <option>API Mode</option>
</select>
```

**En los datos simulados:**
```javascript
// BUSCAR Y ELIMINAR TODA LÓGICA COMO:
const mockDataset = { ... }
const mockUser = { ... }
const generateMockForecast() { ... }
// Usualmente en archivos:
mock.ts, mockData.ts, demo.ts, fixtures.ts, etc.
```

#### Paso 3: Eliminar datos de demo/mockup

Busca en toda la carpeta `companion-ui/` archivos que contengan:

```bash
# Busca archivos con nombres que sugieran mockup
find . -iname "*mock*" -o -iname "*demo*" -o -iname "*fixture*" -o -iname "*test*data*"

# Luego revisa cuáles son datos de prueba vs código real
# Elimina solo los que son específicamente para mockup
```

#### Paso 4: Reconstruir el frontend

```bash
cd companion-ui

# Instalar dependencias (si es necesario)
npm install

# Construir sin mockup
npm run build

# Este comando genera la carpeta dist/ sin la lógica de mockup
```

#### Paso 5: Copiar a la ubicación correcta

```bash
# Asumiendo que estás en la raíz del proyecto
cp -r companion-ui/dist/* ./dist/

# O si usas Windows PowerShell:
Copy-Item -Path "companion-ui/dist/*" -Destination "./dist/" -Recurse -Force
```

---

## 🔍 Cómo Identificar el Mockup en el Código

### Búsquedas útiles en VSCode

1. **Buscar toggle del mockup:**
   - `Ctrl+Shift+F` (Find in Files)
   - Busca: `use_mock` o `mockMode` o `mock.*api` (regex)

2. **Buscar datos de demostración:**
   - Busca: `demo|mock|fixture` (regex)
   - En carpeta: `companion-ui/src`

3. **Buscar rutas de mockup:**
   - Busca: `mock|demo` en rutas de API
   - Busca: `/mock/` o `?mock=`

---

## 📋 Checklist para Eliminar Mockup

- [ ] Accedí a `companion-ui/` o localicé el código fuente
- [ ] Busqué y eliminé el toggle "MOCK"/"API" del UI
- [ ] Eliminé funciones que generan datos simulados
- [ ] Eliminé archivos de mockData/demoData/fixtures
- [ ] Busqué referencias a `localStorage.use_mock` y las eliminé
- [ ] Ejecuté `npm run build` en `companion-ui/`
- [ ] Copié la carpeta `dist/` nuevamente
- [ ] Reinicié los contenedores Docker
- [ ] Verifiqué que el frontend no muestre el toggle mockup

---

## ⚠️ Si No Encuentras companion-ui/

Si la carpeta `companion-ui/` no existe en tu workspace:

1. **Revisa git:**
   ```bash
   git log --all --full-history -- companion-ui/
   git checkout <commit-hash> -- companion-ui/
   ```

2. **Revisa en el .gitignore:**
   ```bash
   cat .gitignore | grep companion-ui
   ```

3. **Pregunta al equipo:**
   - ¿Quién generó el frontend?
   - ¿Dónde está almacenado el código fuente?
   - ¿Es un repositorio separado?

---

## 🚀 Alternativa: Usar el Dockerfile/NGINX

Si tienes acceso a cómo se construye el frontend:

1. **Revisa el Dockerfile:**
   ```bash
   cat dockerfile
   ```

2. **Busca comandos de build del frontend:**
   ```dockerfile
   # Algo como:
   FROM node as builder
   WORKDIR /app/companion-ui
   RUN npm run build
   ```

3. **Modifica el proceso de build para eliminar mockup:**
   - Agrega un step que elimine archivos de mockup antes del build
   - O usa variables de entorno para desactivar mockup

---

## ✅ Verificación Post-Eliminación

Después de reconstruir:

1. **Inicia la aplicación:**
   ```bash
   docker-compose up --build
   ```

2. **Accede a http://localhost**

3. **Verifica que:**
   - ❌ NO hay toggle "MOCK"/"API"
   - ✅ Solo funciona con API real
   - ✅ Los endpoints de login y registro funcionan con la BD real

4. **Revisa la consola del navegador:**
   - `F12` → Console
   - Busca errores como "use_mock is undefined"
   - Verifica que no hay referencias a mockup

---

## 📞 Necesitas ayuda?

Si después de estos pasos aún tienes dudas:

1. Revisa si hay documentación en `CambiosGordos.md` o `Memoria.md`
2. Busca en el git log por commits relacionados con "mock" o "demo"
3. Contacta al desarrollador original del frontend

---

**Nota importante:** El mockup está COMPLETAMENTE en el frontend. El backend NO tiene ninguna lógica de mockup que eliminar. Solo necesitas reconstruir el frontend.
