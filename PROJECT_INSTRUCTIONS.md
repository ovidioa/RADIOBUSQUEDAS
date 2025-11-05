# 🧠 Proyecto: Sistema de Búsqueda e Indexación XML (DALET)

## 🎯 Objetivo General
Desarrollar un sistema que **lea, indexe y permita consultar información contenida en miles de archivos XML** generados por DALET, ofreciendo tres modos de búsqueda:
- **Búsqueda genérica**
- **Búsqueda avanzada**
- **Búsqueda por programa**

El sistema debe incluir:
- Exportación de resultados
- Panel de administración
- Control de acceso (login/logout)
- Interfaz web con tablas filtrables y ordenables

---

## ⚙️ Stack Tecnológico
- **Backend:** Flask (Python)
- **Base de datos:** SQLite (desarrollo) / PostgreSQL o Elasticsearch (producción)
- **ORM:** SQLAlchemy
- **Frontend:** HTML + Bootstrap o React
- **Librerías sugeridas:** DataTables o Tabulator.js
- **Procesamiento XML:** `XMLProcessor` (con `lxml` o `defusedxml`)

---

## 🧩 Fases del Desarrollo

### 🧱 Fase 1 — Análisis y Modelo de Datos
**Objetivo:** identificar campos relevantes en los XML y definir el modelo.

**Tareas:**
1. Analizar XML de ejemplo.
2. Crear modelo `XMLData` con campos:
   ```
   id, title, item_code, program_name, program_date, 
   program_start_time, story_broadcast_time, duration, 
   source_file, text, guests, rundown/service
   ```
3. Crear `XMLProcessor` que procese directorios y guarde registros en la BD.
4. Registrar logs de errores y archivos procesados.

---

### 🔎 Fase 2 — Búsqueda Genérica (`/search`)
**Objetivo:** búsqueda rápida por título, DLT y fechas.

**Tareas:**
- Endpoint `/search` con filtros:
  - `title` (LIKE)
  - `item_code` (exacto o parcial)
  - `program_date` (rango)
- Excluir `type`, `source_file`, `text`.
- Máximo 100 resultados, con aviso si hay más.

---

### 🧠 Fase 3 — Búsqueda Avanzada (`/advanced_search`)
**Objetivo:** permitir filtros más específicos.

**Tareas:**
- Endpoint `/advanced_search`.
- Filtros:
  - `text`
  - `program_start_time`
  - `story_broadcast_time`
  - `guests`
- Buscar por texto parcial.
- Mostrar columnas: fecha, programa, hora emisión, título, duración.
- Añadir exportación de resultados.

---

### 📺 Fase 4 — Búsqueda por Programa (`/programs`)
**Objetivo:** listar programas por nombre, fecha o estación.

**Tareas:**
- Endpoint `/programs` con filtros:
  - `program_name` (LIKE)
  - `program_date` (rango)
  - `rundown/service`
- Agrupar por programa y fecha.
- Mostrar: fecha, estación, hora, nombre programa, historias, acciones.
- Botón “Torna als resultats”.
- Reutilizar plantilla de `/search`.

---

### 📊 Fase 5 — Visualización de Resultados
**Objetivo:** mostrar datos en tablas dinámicas.

**Tareas:**
- Usar DataTables o Tabulator.js.
- Columnas:
  - Fecha programa
  - Nombre programa
  - Hora emisión programa
  - Hora emisión story
  - Título
  - Vista previa
  - Duración
  - Acciones
- En “Acciones” mostrar:
  - Item Code, Programa, Fecha, Hora emisión, Duración, Fuente, Texto.
- Eliminar `Broadcast Start/End Time` y `Record Date`.

---

### 📤 Fase 6 — Exportación (`/export`)
**Objetivo:** exportar resultados a CSV o XML.

**Tareas:**
- Endpoint `/export` con parámetros:
  - `format`: csv / xml
  - `include_text`: true / false
- Excluir `text` si `include_text=false`.
- Exportar:
  ```
  item_code, program_name, program_date, program_start_time,
  story_broadcast_time, duration, source_file
  ```

---

### 🧰 Fase 7 — Administración (`/admin`)
**Objetivo:** gestionar base de datos y procesamiento.

**Tareas:**
- Vista `/admin` con:
  - Total registros.
  - Directorios procesados.
  - Botones: reprocesar (`/process`), limpiar (`/clear_database`).
- Logs con fecha, usuario y acción.
- Requerir login (excepto `/login`).

---

### ⚙️ Fase 8 — Ajustes Técnicos
**Objetivo:** mejorar calidad y coherencia.

**Tareas:**
- Excluir tipos “grouppack” y “storypack”.
- Permitir truncamientos en texto.
- Exportar sin texto por defecto.
- Coherencia entre `/search` y `/programs`.
- SQLite local / PostgreSQL o Elasticsearch en producción.

---

### 🚀 Fase 9 — Optimización (Opcional)
**Objetivo:** escalar el sistema.

**Tareas:**
- Integrar Elasticsearch/OpenSearch.
- Migrar procesamiento XML a tareas asíncronas (Celery + Redis).
- API REST autenticada.
- Procesamiento programado nocturno.

---

### ✅ Fase 10 — Pruebas y Validación
**Objetivo:** asegurar la fiabilidad del sistema.

**Tareas:**
1. Dataset de XML de prueba.
2. Validar:
   - Filtros por fecha, programa, texto.
   - Exclusión de tipos no deseados.
   - Exportación sin texto.
   - Consistencia de campos.
3. Documentar resultados de pruebas.

---

## 🧭 Instrucciones para GitHub Copilot Agent
1. Ejecuta **una fase a la vez**.  
2. Explica cada bloque de código generado y cómo probarlo.  
3. Espera confirmación antes de continuar a la siguiente fase.  
4. Crea los archivos necesarios (`models.py`, `routes.py`, `xml_processor.py`, `templates/*.html`, `app.py`, `main.py`, etc.).  
5. Mantén compatibilidad con Flask y SQLAlchemy.  
6. Usa SQLite localmente y deja configurado PostgreSQL/Elasticsearch como opción.

---

## 📦 Criterios de Finalización
El proyecto estará completo cuando:
- `/search`, `/advanced_search`, `/programs`, `/export` y `/admin` funcionen correctamente.
- Los XML se indexen y consulten sin errores.
- Se puedan exportar datos (sin texto).
- Las búsquedas admitan truncamientos y rangos de fecha.
- Las tablas sean filtrables y coherentes entre vistas.

---

## 💬 Instrucción Final para Copilot
> Actúa como un **Copilot especializado en backend Flask + SQLAlchemy**.  
> Ejecuta las fases **una por una**, generando código y explicaciones.  
> Espera confirmación después de cada fase.  
> Cuando termines todas, genera un resumen técnico del sistema completo.

---
