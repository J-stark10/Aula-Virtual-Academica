# Aula Virtual Académica

Sistema de gestión de aprendizaje (LMS) para instituciones educativas de nivel secundario. Permite la administración de cursos, módulos, recursos, tareas, entregas, calificaciones y anuncios. Configurado con zona horaria Bolivia (UTC-4).

---

## Índice

1. [Roles y funcionalidades detalladas](#1-roles-y-funcionalidades-detalladas)
   - [Administrador](#administrador-admin)
   - [Docente](#docente-docente)
   - [Estudiante](#estudiante-estudiante)
2. [Descripción de módulos](#2-descripción-de-módulos)
3. [Flujo de trabajo completo](#3-flujo-de-trabajo-completo)
4. [Tecnologías](#4-tecnologías)
5. [Instalación y ejecución](#5-instalación-y-ejecución)
6. [Estructura del proyecto](#6-estructura-del-proyecto)
7. [API de rutas](#7-api-de-rutas)

---

## 1. Roles y funcionalidades detalladas

### Administrador (`admin`)

El administrador tiene acceso irrestricto a toda la plataforma. Puede ver y gestionar cualquier curso sin importar el docente asignado.

#### Autenticación y sesión
- Iniciar sesión con email y contraseña
- Cerrar sesión
- La sesión persiste hasta que cierra el navegador o expira

#### Dashboard
- Redirige a la vista correspondiente según el rol del usuario
- **Admin:** estadísticas globales (usuarios, docentes, estudiantes, cursos, inscripciones), gráfico de registros en los últimos 7 días
- **Docente:** resumen de sus cursos, tareas próximas a vencer
- **Estudiante:** lista de cursos inscritos, tareas pendientes y vencidas, anuncios recientes

#### Gestión de cursos
- Ver listado completo de todos los cursos
- Ver detalle de cualquier curso (módulos, recursos, tareas, anuncios)
- Crear cursos (asignándolos a un docente y categoría)
- Editar cualquier curso
- Eliminar cualquier curso (con todo su contenido asociado)
- Ver y gestionar inscripciones de cualquier curso

#### Gestión de módulos
- Crear módulos dentro de cualquier curso
- Editar y eliminar módulos

#### Gestión de recursos
- Agregar recursos a cualquier módulo (enlaces, PDFs, videos)
- Editar y eliminar recursos

#### Gestión de tareas
- Crear tareas en cualquier módulo de cualquier curso
- Editar y eliminar tareas
- Ver detalle de tareas con fecha límite y estado de entrega

#### Gestión de entregas
- Ver listado de entregas de cualquier tarea
- Descargar archivos entregados por los estudiantes
- Calificar entregas (asignar nota numérica y retroalimentación)
- Eliminar entregas

#### Gestión de calificaciones
- Ver notas del curso (tabla con nota final de cada estudiante)
- Ver detalle de notas por estudiante (desglose por tarea)
- Estudiantes pueden consultar sus propias notas por curso

#### Gestión de categorías
- Crear, editar y eliminar categorías de cursos (Ciencias Exactas, Naturales, Humanidades, etc.)

#### Gestión de anuncios
- Crear y eliminar anuncios en cualquier curso

---

### Docente (`docente`)

El docente solo puede gestionar sus propios cursos (aquellos donde fue asignado como docente titular).

#### Autenticación y sesión
- Iniciar sesión con email y contraseña
- Cerrar sesión

#### Dashboard
- Resumen de los cursos que dicta
- Tareas próximas a vencer (próximos 7 días)
- Enlaces rápidos a cada curso

#### Gestión de cursos propios
- **Crear curso:** formulario con nombre, descripción, categoría. Al crear se genera automáticamente un código único de 6 dígitos para que los estudiantes se inscriban.
- **Editar curso:** modificar nombre, descripción, categoría y estado activo/inactivo
- **Eliminar curso:** borra el curso con todo su contenido (módulos, recursos, tareas, entregas, calificaciones, anuncios)
- **Ver detalle del curso:** visualiza módulos ordenados, recursos, tareas y anuncios

#### Código de inscripción
- Cada curso tiene un código único de 6 dígitos
- Se muestra en el detalle del curso con botón "Copiar" al portapapeles
- El docente comparte este código con los estudiantes para que se inscriban
- En la página de inscripciones puede ver todos los estudiantes inscritos y eliminar inscripciones

#### Gestión de módulos
- **Crear módulo:** formulario con título y descripción, se ordenan secuencialmente
- **Editar módulo:** modificar título, descripción y orden
- **Eliminar módulo:** borra el módulo con todos sus recursos y tareas asociadas

#### Gestión de recursos
- **Agregar recurso:** formulario con título, tipo (enlace, PDF, video) y URL
- Cada recurso se asocia a un módulo específico
- Los estudiantes pueden abrir enlaces externos desde el detalle del curso
- **Editar y eliminar recursos**

#### Gestión de tareas
- **Crear tarea:** formulario con título, instrucciones, fecha límite (datetime-local) y puntaje máximo (mínimo 0.5, pasos de 0.5)
- **Editar tarea:** modificar cualquier campo
- **Eliminar tarea:** borra la tarea y todas sus entregas y calificaciones asociadas
- **Ver detalle de tarea:** muestra título, instrucciones, fecha límite, puntaje máximo y estado de la entrega del estudiante actual

#### Gestión de entregas
- **Ver entregas:** listado de todos los estudiantes que entregaron la tarea, con fecha, archivo descargable y estado (a tiempo/tardía)
- **Ver pendientes:** lista de estudiantes inscritos que aún no han entregado
- **Calificar:** formulario donde asigna una nota numérica (0 - puntaje máximo) y retroalimentación opcional
- **Eliminar entrega:** borra la entrega y su calificación

#### Calificaciones del curso
- **Ver notas del curso:** tabla con todos los estudiantes y su nota final
- **Detalle por estudiante:** desglose de todas sus tareas con nota y retroalimentación

#### Anuncios
- **Crear anuncio:** título y contenido, se publica inmediatamente en el curso
- Los anuncios aparecen ordenados del más reciente al más antiguo en el detalle del curso
- **Eliminar anuncio**

---

### Estudiante (`estudiante`)

#### Autenticación y sesión
- Iniciar sesión con email y contraseña
- Cerrar sesión
- La sesión persiste hasta que cierra el navegador

#### Dashboard
- Listado de cursos en los que está inscrito
- Tareas pendientes y vencidas
- Anuncios recientes
- Enlaces rápidos a cada curso

#### Inscripción a cursos
- **Unirse a un curso:** formulario donde ingresa el código de 6 dígitos proporcionado por el docente
- Validación: el código debe existir y el curso debe estar activo
- No puede inscribirse dos veces al mismo curso

#### Vista del curso
- **Encabezado:** nombre del curso, categoría, docente, descripción
- **Anuncios:** comunicados del docente
- **Módulos:** contenido organizado por unidades, cada una con:
  - **Recursos:** enlaces a materiales, PDFs descargables, videos
  - **Tareas:** enlaces a cada tarea con su fecha límite

#### Tareas
- **Ver detalle de tarea:** instrucciones, fecha límite, puntaje máximo
- **Entregar tarea:** formulario con subida de archivo (obligatorio en primera entrega) y comentario opcional
- **Reenviar:** si ya entregó, puede subir un nuevo archivo que reemplaza al anterior (se actualiza la fecha de entrega)
- Si la tarea está vencida, igual puede entregar (el sistema no bloquea por fecha)

#### Calificaciones
- **Mis Notas (por curso):** vista detallada con nota final del curso y lista de todas las tareas con su nota individual y retroalimentación del docente



---

## 2. Descripción de módulos

### Autenticación (`/auth`)
- `GET /auth/login` — formulario de inicio de sesión
- `POST /auth/login` — validación de credenciales
- `GET /auth/logout` — cierre de sesión

### Dashboard (`/`)
- `GET /` — redirige según el rol del usuario

### Cursos (`/cursos`)
- `GET /cursos/` — listado de cursos visibles según rol
- `GET|POST /cursos/create` — crear curso
- `GET|POST /cursos/edit/<id>` — editar curso
- `GET /cursos/delete/<id>` — eliminar curso
- `GET /cursos/detalle/<id>` — vista completa del curso
- `GET|POST /cursos/unirse` — inscripción por código (estudiantes)
- `GET /cursos/inscripciones/<id>` — gestionar inscripciones

### Módulos (`/modulos`)
- `GET|POST /modulos/curso/<id>/create` — crear módulo
- `GET|POST /modulos/edit/<id>` — editar módulo
- `GET /modulos/delete/<id>` — eliminar módulo

### Recursos (`/recursos`)
- `GET|POST /recursos/modulo/<id>/create` — crear recurso (enlace, PDF, video)
- `GET|POST /recursos/edit/<id>` — editar recurso
- `GET /recursos/delete/<id>` — eliminar recurso
- `GET /recursos/descargar/<path>` — descargar archivo

### Tareas (`/tareas`)
- `GET|POST /tareas/modulo/<id>/create` — crear tarea
- `GET /tareas/detalle/<id>` — vista de tarea con entrega y calificación
- `GET|POST /tareas/edit/<id>` — editar tarea
- `GET /tareas/delete/<id>` — eliminar tarea

### Entregas (`/entregas`)
- `GET|POST /entregas/tarea/<id>/enviar` — entregar tarea (estudiantes)
- `GET /entregas/tarea/<id>/listar` — listado de entregas (docentes)
- `GET /entregas/delete/<id>` — eliminar entrega
- `GET /entregas/descargar/<path>` — descargar archivo de entrega

### Calificaciones (`/calificaciones`)
- `GET|POST /calificaciones/entrega/<id>/calificar` — calificar entrega
- `GET /calificaciones/curso/<id>/notas` — notas del curso
- `GET /calificaciones/curso/<id>/estudiante/<id>` — detalle por estudiante
- `GET /calificaciones/curso/<id>/mis-notas` — mis notas (estudiante)

### Anuncios (`/anuncios`)
- `GET|POST /anuncios/curso/<id>/create` — crear anuncio
- `GET /anuncios/delete/<id>` — eliminar anuncio

## 3. Flujo de trabajo completo

### Ciclo de vida de un curso

1. **Admin** crea una categoría (ej: "Ciencias Exactas")
2. **Admin** crea un curso y lo asigna a un docente
3. **Docente** agrega módulos al curso (Unidad 1, Unidad 2...)
4. **Docente** agrega recursos a cada módulo (enlaces, PDFs, videos)
5. **Docente** comparte el código de inscripción con los estudiantes
6. **Estudiantes** se inscriben usando el código
7. **Docente** crea tareas en los módulos con fecha límite y puntaje
8. **Estudiantes** entregan las tareas (suben archivos)
9. **Docente** califica las entregas (asigna nota y retroalimentación)
10. **Docente** consulta las notas del curso
11. **Estudiantes** consultan sus notas y retroalimentación

---

## 4. Tecnologías

| Capa | Tecnología | Versión |
|------|-----------|---------|
| Lenguaje | Python | 3.12 |
| Framework web | Flask | 3.1.3 |
| ORM | SQLAlchemy | 2.0.50 |
| Migraciones | Flask-Migrate / Alembic | — |
| Base de datos | SQLite (desarrollo) / PostgreSQL (producción) | — |
| Autenticación | Flask-Login + Flask-Bcrypt | — |
| Template engine | Jinja2 | 3.1.6 |
| CSS | Tailwind CSS (vía CDN) | — |
| Gráficos | Chart.js (vía CDN) | — |
| Servidor WSGI | Gunicorn | 23.0.0 |
| Conector PostgreSQL | psycopg2-binary | 2.9.10 |
| Variables de entorno | python-dotenv | 1.0.1 |
| Zona horaria | zoneinfo (tzdata) | — |

---

## 5. Instalación y ejecución

```bash
# Clonar
git clone <repo-url>
cd AulaVirtualAcademica

# Entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno (opcional)
cp .env.example .env  # si existe, o crear .env con DATABASE_URL

# Cargar datos de prueba
python seed.py

# Iniciar servidor
python run.py
```

Abrir `http://127.0.0.1:5000` en el navegador.

### Credenciales de prueba

| Rol | Email | Contraseña |
|-----|-------|------------|
| Admin | admin@colegio.bo | admin123 |
| Docente (Matemáticas, Física) | rosa.quispe@colegio.bo | docente123 |
| Docente (Lenguaje, Biología) | marcelo.choque@colegio.bo | docente123 |
| Docente (Inglés) | juana.perez@colegio.bo | docente123 |
| Estudiantes (25) | *@colegio.bo | estudiante123 |

### Zona horaria

Todas las fechas se almacenan en **UTC** en la base de datos y se muestran en **hora de Bolivia** (America/La_Paz, UTC-4) mediante el filtro `| bolivia` de Jinja2. Esto asegura que:

- La hora mostrada a los usuarios siempre corresponde al huso horario boliviano
- Las comparaciones internas (tareas vencidas, próximas a vencer) se hacen en UTC, evitando errores por cambios de zona
- El seed genera datos en hora Bolivia y los convierte a UTC automáticamente

Para corregir registros existentes que se guardaron antes de esta implementación, ejecutar:

```bash
python fix_tareas_tz.py
```

---

## 6. Estructura del proyecto

```
AulaVirtualAcademica/
├── run.py                        # Punto de entrada del servidor
├── seed.py                       # Generación de datos de prueba
├── fix_tareas_tz.py              # Script para corregir zonas horarias en datos existentes
├── requirements.txt              # Dependencias del proyecto
├── Procfile                      # Despliegue en producción (Heroku/Render)
├── .env                          # Variables de entorno
├── .gitignore
├── README.md
├── instance/
│   └── aula_virtual.db           # Base de datos SQLite (desarrollo)
├── migrations/                   # Migraciones de BD (Flask-Migrate / Alembic)
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
└── app/
    ├── app.py                    # Fábrica de aplicación Flask (BOLIVIA_TZ, UTC, filtro `bolivia`)
    ├── utils.py                  # Utilidades: decorador role_required, registrar_log, guardar_archivo
    ├── static/
    │   └── uploads/              # Archivos subidos (entregas de estudiantes)
    ├── templates/
    │   ├── base.html             # Layout principal con Tailwind CSS
    │   └── ... (templates compartidos)
    ├── auth/                     # Autenticación (login, logout)
    │   ├── routes.py
    │   └── templates/auth/
    ├── core/                     # Dashboard (admin, docente, estudiante)
    │   ├── routes.py
    │   └── templates/core/
    ├── categorias/               # Categorías de cursos
    │   ├── models.py
    │   └── routes.py
    ├── usuarios/                 # Gestión de usuarios
    │   ├── models.py             # Usuario, LogActividad
    │   ├── routes.py
    │   └── templates/usuarios/
    ├── cursos/                   # Cursos e inscripciones
    │   ├── models.py
    │   ├── routes.py
    │   └── templates/cursos/
    ├── modulos/                  # Módulos dentro de cursos
    │   ├── models.py
    │   ├── routes.py
    │   └── templates/modulos/
    ├── recursos/                 # Recursos (enlaces, archivos)
    │   ├── models.py
    │   ├── routes.py
    │   └── templates/recursos/
    ├── tareas/                   # Tareas con fecha límite
    │   ├── models.py
    │   ├── routes.py
    │   └── templates/tareas/
    ├── entregas/                 # Entregas de estudiantes
    │   ├── models.py
    │   ├── routes.py
    │   └── templates/entregas/
    ├── calificaciones/           # Calificaciones y notas
    │   ├── models.py
    │   ├── routes.py
    │   └── templates/calificaciones/
    └── anuncios/                 # Anuncios por curso
        ├── models.py
        ├── routes.py
        └── templates/anuncios/
```

---

## 7. API de rutas

### Autenticación
| Método | Ruta | Acceso |
|--------|------|--------|
| GET, POST | `/auth/login` | Público |
| GET | `/auth/logout` | Todos |

### Dashboard
| Método | Ruta | Acceso |
|--------|------|--------|
| GET | `/` | Todos |
| GET | `/bitacora` | Todos |

### Cursos
| Método | Ruta | Acceso |
|--------|------|--------|
| GET | `/cursos/` | Todos |
| GET, POST | `/cursos/create` | Admin/Docente |
| GET, POST | `/cursos/edit/<id>` | Admin/Docente |
| GET | `/cursos/delete/<id>` | Admin/Docente |
| GET | `/cursos/detalle/<id>` | Todos |
| GET, POST | `/cursos/unirse` | Estudiante |
| GET | `/cursos/inscripciones/<id>` | Admin/Docente |

### Módulos
| Método | Ruta | Acceso |
|--------|------|--------|
| GET, POST | `/modulos/curso/<id>/create` | Admin/Docente |
| GET, POST | `/modulos/edit/<id>` | Admin/Docente |
| GET | `/modulos/delete/<id>` | Admin/Docente |

### Recursos
| Método | Ruta | Acceso |
|--------|------|--------|
| GET, POST | `/recursos/modulo/<id>/create` | Admin/Docente |
| GET, POST | `/recursos/edit/<id>` | Admin/Docente |
| GET | `/recursos/delete/<id>` | Admin/Docente |
| GET | `/recursos/descargar/<path>` | Todos |

### Tareas
| Método | Ruta | Acceso |
|--------|------|--------|
| GET, POST | `/tareas/modulo/<id>/create` | Admin/Docente |
| GET | `/tareas/detalle/<id>` | Todos |
| GET, POST | `/tareas/edit/<id>` | Admin/Docente |
| GET | `/tareas/delete/<id>` | Admin/Docente |

### Entregas
| Método | Ruta | Acceso |
|--------|------|--------|
| GET, POST | `/entregas/tarea/<id>/enviar` | Estudiante |
| GET | `/entregas/tarea/<id>/listar` | Admin/Docente |
| GET | `/entregas/delete/<id>` | Admin/Docente |
| GET | `/entregas/descargar/<path>` | Admin/Docente |

### Calificaciones
| Método | Ruta | Acceso |
|--------|------|--------|
| GET, POST | `/calificaciones/entrega/<id>/calificar` | Admin/Docente |
| GET | `/calificaciones/curso/<id>/notas` | Admin/Docente |
| GET | `/calificaciones/curso/<id>/estudiante/<id>` | Admin/Docente |
| GET | `/calificaciones/curso/<id>/mis-notas` | Estudiante |

### Anuncios
| Método | Ruta | Acceso |
|--------|------|--------|
| GET, POST | `/anuncios/curso/<id>/create` | Admin/Docente |
| GET | `/anuncios/delete/<id>` | Admin/Docente |
