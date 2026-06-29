from dotenv import load_dotenv
load_dotenv()

import random
from datetime import datetime, timedelta
from app.app import create_app, db, bcrypt, BOLIVIA_TZ, UTC
from app.usuarios.models import Usuario
from app.categorias.models import Categoria
from app.cursos.models import Curso, Inscripcion
from app.modulos.models import Modulo
from app.recursos.models import Recurso
from app.tareas.models import Tarea
from app.entregas.models import Entrega
from app.calificaciones.models import Calificacion
from app.anuncios.models import Anuncio

app = create_app()


def hash_pw(plain):
    return bcrypt.generate_password_hash(plain).decode("utf-8")


# ---------------------------------------------------------------------------
# Fechas de registro dispersas entre el 21/06/2026 y hoy (27/06/2026),
# para que el gráfico de registros de los últimos 7 días del dashboard
# admin tenga una distribución realista.
# ---------------------------------------------------------------------------
# Las fechas aquí están en hora de Bolivia (UTC-4) y se convierten a UTC
# para almacenarse en la BD. El filtro `bolivia` las muestra en hora local.
FECHA_INICIO_REGISTROS_BO = datetime(2026, 6, 21, 8, 0, 0)
FECHA_HOY_BO = datetime(2026, 6, 27, 18, 0, 0)
FECHA_INICIO_REGISTROS = FECHA_INICIO_REGISTROS_BO.replace(tzinfo=BOLIVIA_TZ).astimezone(UTC).replace(tzinfo=None)
FECHA_HOY = FECHA_HOY_BO.replace(tzinfo=BOLIVIA_TZ).astimezone(UTC).replace(tzinfo=None)
RANGO_DIAS_REGISTRO = (FECHA_HOY_BO - FECHA_INICIO_REGISTROS_BO).days


def fecha_registro_dispersa(seed):
    """
    Genera una fecha de registro determinística (basada en `seed`) dentro del
    rango 21-jun-2026 a hoy, para que todos los registros caigan en la
    ventana de los últimos 7 días que muestra el gráfico del dashboard.

    La fecha devuelta se almacena en UTC (convertida desde hora Bolivia).
    """
    rnd = random.Random(seed)
    dia_offset = rnd.randint(0, RANGO_DIAS_REGISTRO)
    hora_offset = rnd.randint(7, 20)  # horario escolar/administrativo
    minuto_offset = rnd.randint(0, 59)
    bolivia_dt = FECHA_INICIO_REGISTROS_BO + timedelta(days=dia_offset, hours=hora_offset - 8, minutes=minuto_offset)
    return bolivia_dt.replace(tzinfo=BOLIVIA_TZ).astimezone(UTC).replace(tzinfo=None)


with app.app_context():
    print("Limpiando base de datos...")
    db.drop_all()
    db.create_all()

    # -----------------------------------------------------------------
    # USUARIOS
    # -----------------------------------------------------------------
    print("Creando usuarios...")

    admin = Usuario(
        nombre_completo="Lic. Juan Carlos Mamani Quispe",
        email="admin@colegio.bo",
        password=hash_pw("admin123"),
        rol="admin",
        fecha_registro=fecha_registro_dispersa("admin"),
    )

    profe_rosa = Usuario(
        nombre_completo="Prof. Rosa Quispe Condori",
        email="rosa.quispe@colegio.bo",
        password=hash_pw("docente123"),
        rol="docente",
        fecha_registro=fecha_registro_dispersa("rosa"),
    )
    profe_marcelo = Usuario(
        nombre_completo="Prof. Marcelo Choque Huanca",
        email="marcelo.choque@colegio.bo",
        password=hash_pw("docente123"),
        rol="docente",
        fecha_registro=fecha_registro_dispersa("marcelo"),
    )
    profe_juana = Usuario(
        nombre_completo="Prof. Juana Pérez Mamani",
        email="juana.perez@colegio.bo",
        password=hash_pw("docente123"),
        rol="docente",
        fecha_registro=fecha_registro_dispersa("juana"),
    )
    profe_franklin = Usuario(
        nombre_completo="Prof. Franklin Yujra Apaza",
        email="franklin.yujra@colegio.bo",
        password=hash_pw("docente123"),
        rol="docente",
        fecha_registro=fecha_registro_dispersa("franklin"),
    )

    db.session.add_all([admin, profe_rosa, profe_marcelo, profe_juana, profe_franklin])
    db.session.commit()

    estudiantes_data = [
        ("Javier Jose", "javier.jose@colegio.bo"),
        ("Alejandro Paco Mamani", "alejandro.paco@colegio.bo"),
        ("Carlos Pachari Rodriguez", "carlos.pachari@colegio.bo"),
        ("María Choque Quispe", "maria.choque@colegio.bo"),
        ("Juan Mamani Flores", "juan.mamani@colegio.bo"),
        ("Ana Condori Huanca", "ana.condori@colegio.bo"),
        ("Luis Quispe Callisaya", "luis.quispe@colegio.bo"),
        ("Rosa Mamani López", "rosa.mamani@colegio.bo"),
        ("Pedro Yujra Quisbert", "pedro.yujra@colegio.bo"),
        ("Sara Flores Mamani", "sara.flores@colegio.bo"),
        ("Diego Tarqui Vargas", "diego.tarqui@colegio.bo"),
        ("Camila Apaza Morales", "camila.apaza@colegio.bo"),
        ("Pablo Quispe Huanca", "pablo.quispe@colegio.bo"),
        ("Valeria Mamani Siñani", "valeria.mamani@colegio.bo"),
        ("Mateo Choquevilca Condori", "mateo.choquevilca@colegio.bo"),
        ("Gabriela Mamani Cruz", "gabriela.mamani@colegio.bo"),
        ("Santiago Miranda López", "santiago.miranda@colegio.bo"),
        ("Nicole Rojas Vargas", "nicole.rojas@colegio.bo"),
        ("Benjamín Canaviri Mamani", "benjamin.canaviri@colegio.bo"),
        ("Luciana Quispe Ramos", "luciana.quispe@colegio.bo"),
        ("Emiliano Cusi Lipa", "emiliano.cusi@colegio.bo"),
        ("Valentina Ochoa Pérez", "valentina.ochoa@colegio.bo"),
        ("Samuel Alanoca Flores", "samuel.alanoca@colegio.bo"),
        ("Abigail Huanca Condori", "abigail.huanca@colegio.bo"),
        ("Nicolás Quenta Mamani", "nicolas.quenta@colegio.bo"),
    ]

    estudiantes = []
    for nombre, email in estudiantes_data:
        est = Usuario(
            nombre_completo=nombre,
            email=email,
            password=hash_pw("estudiante123"),
            rol="estudiante",
            fecha_registro=fecha_registro_dispersa(email),
        )
        estudiantes.append(est)
    db.session.add_all(estudiantes)
    db.session.commit()

    # -----------------------------------------------------------------
    # CATEGORÍAS
    # -----------------------------------------------------------------
    print("Creando categorías...")
    cat_exactas = Categoria(nombre="Ciencias Exactas", descripcion="Matemática, Física, Química")
    cat_naturales = Categoria(nombre="Ciencias Naturales", descripcion="Biología-Geografía, Ecología")
    cat_humanidades = Categoria(nombre="Humanidades", descripcion="Comunicación y Lenguajes, Ciencias Sociales")
    cat_idiomas = Categoria(nombre="Idiomas", descripcion="Inglés")
    cat_tecnica = Categoria(nombre="Educación Técnica", descripcion="Técnica Tecnológica, Educación Física, Valores")
    db.session.add_all([cat_exactas, cat_naturales, cat_humanidades, cat_idiomas, cat_tecnica])
    db.session.commit()

    # -----------------------------------------------------------------
    # CURSOS — currículo boliviano (Secundaria Comunitaria Productiva,
    # Ley de Educación N° 070 "Avelino Siñani - Elizardo Pérez")
    # -----------------------------------------------------------------
    print("Creando cursos...")
    curso_mate = Curso(
        nombre="Matemática - 4to de Secundaria",
        descripcion="Álgebra elemental, ecuaciones lineales y cuadráticas, geometría plana y estadística básica.",
        categoria_id=cat_exactas.id, docente_id=profe_rosa.id,
    )
    curso_fisica = Curso(
        nombre="Física - 5to de Secundaria",
        descripcion="Cinemática, dinámica, leyes de Newton, trabajo, energía y potencia mecánica.",
        categoria_id=cat_exactas.id, docente_id=profe_rosa.id,
    )
    curso_comunicacion = Curso(
        nombre="Comunicación y Lenguajes - 3ro de Secundaria",
        descripcion="Gramática normativa, redacción de textos, análisis literario y ortografía del castellano.",
        categoria_id=cat_humanidades.id, docente_id=profe_marcelo.id,
    )
    curso_sociales = Curso(
        nombre="Ciencias Sociales - 4to de Secundaria",
        descripcion="Historia de Bolivia, geografía económica y procesos sociales del Estado Plurinacional.",
        categoria_id=cat_humanidades.id, docente_id=profe_franklin.id,
    )
    curso_bio = Curso(
        nombre="Biología-Geografía - 4to de Secundaria",
        descripcion="Biología celular, genética mendeliana, ecosistemas y biodiversidad boliviana.",
        categoria_id=cat_naturales.id, docente_id=profe_marcelo.id,
    )
    curso_ingles = Curso(
        nombre="Inglés - 3ro de Secundaria",
        descripcion="Gramática básica, vocabulario esencial, reading comprehension y conversación elemental.",
        categoria_id=cat_idiomas.id, docente_id=profe_juana.id,
    )
    cursos = [curso_mate, curso_fisica, curso_comunicacion, curso_sociales, curso_bio, curso_ingles]
    db.session.add_all(cursos)
    db.session.commit()

    # -----------------------------------------------------------------
    # INSCRIPCIONES
    # -----------------------------------------------------------------
    print("Inscribiendo estudiantes...")
    inscripciones_plan = [
        (curso_mate.id, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]),
        (curso_fisica.id, [0, 1, 2, 3, 4, 12, 13, 14, 15, 16, 17]),
        (curso_comunicacion.id, [2, 3, 4, 5, 6, 7, 10, 11, 18, 19, 20, 21]),
        (curso_sociales.id, [1, 5, 6, 9, 11, 13, 17, 19, 21, 23]),
        (curso_bio.id, [8, 9, 12, 13, 14, 15, 22, 23, 24, 0]),
        (curso_ingles.id, [16, 17, 18, 19, 20, 21, 22, 23, 24, 1]),
    ]
    inscripciones = []
    for curso_id, indices in inscripciones_plan:
        for idx in indices:
            inscripciones.append(Inscripcion(curso_id=curso_id, estudiante_id=estudiantes[idx].id))
    db.session.add_all(inscripciones)
    db.session.commit()

    # -----------------------------------------------------------------
    # MÓDULOS
    # -----------------------------------------------------------------
    print("Creando módulos...")

    modulos_data = {
        curso_mate.id: [
            ("Unidad 1 - Ecuaciones Lineales", "Resolución de ecuaciones de primer grado con una incógnita.", 1),
            ("Unidad 2 - Funciones Cuadráticas", "Gráfica de parábolas, vértice, eje de simetría y raíces.", 2),
            ("Unidad 3 - Geometría Plana", "Ángulos, triángulos, teorema de Pitágoras y áreas.", 3),
            ("Unidad 4 - Estadística y Probabilidad", "Media, mediana, moda, probabilidad simple y compuesta.", 4),
        ],
        curso_fisica.id: [
            ("Unidad 1 - Cinemática", "MRU, MRUV, caída libre y gráficas de movimiento.", 1),
            ("Unidad 2 - Dinámica", "Leyes de Newton, fuerza, masa y aceleración.", 2),
            ("Unidad 3 - Trabajo y Energía", "Trabajo mecánico, energía cinética y potencial.", 3),
        ],
        curso_comunicacion.id: [
            ("Unidad 1 - Gramática y Ortografía", "Reglas ortográficas, tildación y signos de puntuación.", 1),
            ("Unidad 2 - Redacción de Textos", "Estructura del párrafo, textos narrativos y descriptivos.", 2),
            ("Unidad 3 - Literatura Boliviana", "Autores representativos: Alcides Arguedas, Adela Zamudio.", 3),
        ],
        curso_sociales.id: [
            ("Unidad 1 - Historia de Bolivia: Periodo Colonial", "La Colonia, el sistema de la mita y las rebeliones indígenas.", 1),
            ("Unidad 2 - Independencia y Formación del Estado", "Las guerras de independencia y la fundación de Bolivia en 1825.", 2),
            ("Unidad 3 - Geografía Económica de Bolivia", "Regiones productivas, recursos naturales y comercio exterior.", 3),
        ],
        curso_bio.id: [
            ("Unidad 1 - La Célula", "Estructura celular, tipos de células y organelos.", 1),
            ("Unidad 2 - Genética Mendeliana", "Leyes de Mendel, cruces monohíbridos y árbol genealógico.", 2),
            ("Unidad 3 - Ecosistemas Bolivianos", "Altiplano, valles, llanos y amazonía; cadenas tróficas.", 3),
        ],
        curso_ingles.id: [
            ("Unidad 1 - Basic Grammar", "Verb to be, simple present, articles and plurals.", 1),
            ("Unidad 2 - Reading & Vocabulary", "Daily routines, school objects, family members.", 2),
            ("Unidad 3 - Conversation", "Greetings, introductions, asking for directions.", 3),
        ],
    }

    modulos = {}
    for curso_id, lista in modulos_data.items():
        modulos[curso_id] = []
        for titulo, desc, orden in lista:
            m = Modulo(curso_id=curso_id, titulo=titulo, descripcion=desc, orden=orden)
            modulos[curso_id].append(m)
            db.session.add(m)
    db.session.commit()

    # -----------------------------------------------------------------
    # RECURSOS — URLs raíz reales y verificadas (Khan Academy en español,
    # unProfesor.com y Ministerio de Educación de Bolivia). Se usan
    # secciones/canales raíz en vez de rutas profundas no verificables,
    # para no inventar enlaces que pudieran no existir.
    # -----------------------------------------------------------------
    print("Creando recursos...")

    URL_KHAN_MATE = "https://es.khanacademy.org/math"
    URL_KHAN_FISICA = "https://es.khanacademy.org/science/fisica-pe-pre-u"
    URL_KHAN_QUIMICA = "https://es.khanacademy.org/science/ciencias-preparacion-educacion-superior"
    URL_KHAN_BIO = "https://es.khanacademy.org/science/biology/biology"
    URL_KHAN_YT = "https://www.youtube.com/user/KhanAcademyEspanol"

    URL_UP_MATE = "https://www.unprofesor.com/matematicas/"
    URL_UP_LENGUA = "https://www.unprofesor.com/lengua-espanola/"
    URL_UP_SOCIALES = "https://www.unprofesor.com/ciencias-sociales/"
    URL_UP_NATURALES = "https://www.unprofesor.com/ciencias-naturales/"
    URL_UP_FISICA = "https://www.unprofesor.com/fisica/"
    URL_UP_INGLES = "https://www.unprofesor.com/ingles/"
    URL_UP_YT = "https://www.youtube.com/@Unprofesor"

    URL_MINEDU_BIBLIOTECA = "https://educa.minedu.gob.bo/"
    URL_MINEDU_INSTITUCIONAL = "https://www.minedu.gob.bo/"

    recursos_lista = [
        # (curso_id, mod_idx, titulo, tipo, url)
        (curso_mate.id, 0, "Khan Academy - Álgebra y ecuaciones lineales", "enlace", URL_KHAN_MATE),
        (curso_mate.id, 0, "unProfesor - Matemáticas (ejercicios resueltos)", "enlace", URL_UP_MATE),
        (curso_mate.id, 1, "Khan Academy - Funciones cuadráticas", "enlace", URL_KHAN_MATE),
        (curso_mate.id, 1, "unProfesor - Matemáticas: funciones y gráficas", "enlace", URL_UP_MATE),
        (curso_mate.id, 2, "Khan Academy - Geometría plana y teorema de Pitágoras", "enlace", URL_KHAN_MATE),
        (curso_mate.id, 2, "unProfesor - Geometría (triángulos y polígonos)", "enlace", URL_UP_MATE),
        (curso_mate.id, 3, "Khan Academy - Estadística y probabilidad", "enlace", URL_KHAN_MATE),
        (curso_mate.id, 3, "Canal de YouTube - Khan Academy en Español", "video", URL_KHAN_YT),

        (curso_fisica.id, 0, "Khan Academy - Física: cinemática", "enlace", URL_KHAN_FISICA),
        (curso_fisica.id, 0, "unProfesor - Física (movimiento y velocidad)", "enlace", URL_UP_FISICA),
        (curso_fisica.id, 1, "Khan Academy - Física: dinámica y leyes de Newton", "enlace", URL_KHAN_FISICA),
        (curso_fisica.id, 1, "unProfesor - Física (fuerzas)", "enlace", URL_UP_FISICA),
        (curso_fisica.id, 2, "Khan Academy - Trabajo y energía", "enlace", URL_KHAN_FISICA),
        (curso_fisica.id, 2, "Canal de YouTube - Khan Academy en Español", "video", URL_KHAN_YT),

        (curso_comunicacion.id, 0, "unProfesor - Lengua española: ortografía", "enlace", URL_UP_LENGUA),
        (curso_comunicacion.id, 0, "unProfesor - Reglas de tildación y puntuación", "enlace", URL_UP_LENGUA),
        (curso_comunicacion.id, 1, "unProfesor - Redacción de textos", "enlace", URL_UP_LENGUA),
        (curso_comunicacion.id, 1, "Canal de YouTube - unProfesor", "video", URL_UP_YT),
        (curso_comunicacion.id, 2, "unProfesor - Literatura y análisis de textos", "enlace", URL_UP_LENGUA),
        (curso_comunicacion.id, 2, "Biblioteca digital - Ministerio de Educación de Bolivia", "enlace", URL_MINEDU_BIBLIOTECA),

        (curso_sociales.id, 0, "unProfesor - Ciencias Sociales: historia", "enlace", URL_UP_SOCIALES),
        (curso_sociales.id, 0, "Ministerio de Educación de Bolivia - sitio institucional", "enlace", URL_MINEDU_INSTITUCIONAL),
        (curso_sociales.id, 1, "unProfesor - Ciencias Sociales: independencia americana", "enlace", URL_UP_SOCIALES),
        (curso_sociales.id, 1, "Biblioteca digital - Ministerio de Educación de Bolivia", "enlace", URL_MINEDU_BIBLIOTECA),
        (curso_sociales.id, 2, "unProfesor - Ciencias Sociales: geografía", "enlace", URL_UP_SOCIALES),
        (curso_sociales.id, 2, "Canal de YouTube - unProfesor", "video", URL_UP_YT),

        (curso_bio.id, 0, "Khan Academy - Biología: la célula", "enlace", URL_KHAN_BIO),
        (curso_bio.id, 0, "unProfesor - Ciencias Naturales: la célula", "enlace", URL_UP_NATURALES),
        (curso_bio.id, 1, "Khan Academy - Genética mendeliana", "enlace", URL_KHAN_BIO),
        (curso_bio.id, 1, "unProfesor - Ciencias Naturales: genética", "enlace", URL_UP_NATURALES),
        (curso_bio.id, 2, "Khan Academy - Química y ecosistemas (recursos naturales)", "enlace", URL_KHAN_QUIMICA),
        (curso_bio.id, 2, "unProfesor - Ciencias Naturales: ecosistemas", "enlace", URL_UP_NATURALES),

        (curso_ingles.id, 0, "unProfesor - Inglés: gramática básica", "enlace", URL_UP_INGLES),
        (curso_ingles.id, 0, "Canal de YouTube - Khan Academy en Español", "video", URL_KHAN_YT),
        (curso_ingles.id, 1, "unProfesor - Inglés: vocabulario", "enlace", URL_UP_INGLES),
        (curso_ingles.id, 1, "Canal de YouTube - unProfesor", "video", URL_UP_YT),
        (curso_ingles.id, 2, "unProfesor - Inglés: conversación", "enlace", URL_UP_INGLES),
        (curso_ingles.id, 2, "Ministerio de Educación de Bolivia - Programa Inglés para Todos", "enlace", URL_MINEDU_INSTITUCIONAL),
    ]
    for curso_id, mod_idx, titulo, tipo, url in recursos_lista:
        r = Recurso(
            modulo_id=modulos[curso_id][mod_idx].id,
            titulo=titulo, tipo=tipo, url_enlace=url,
        )
        db.session.add(r)
    db.session.commit()
    print(f"  {len(recursos_lista)} recursos creados (URLs raíz verificadas).")

    # -----------------------------------------------------------------
    # TAREAS — distribuidas en los 3 trimestres del año escolar
    # boliviano 2026 (febrero a noviembre aprox., aquí hasta junio
    # porque "hoy" en el sistema es 27/06/2026).
    # Las fechas están en hora de Bolivia y se convierten a UTC.
    # -----------------------------------------------------------------
    print("Creando tareas...")

    t1_inicio_bo = datetime(2026, 2, 9, 8, 0, 0)   # Trimestre 1: inicio de clases (febrero)
    t2_inicio_bo = datetime(2026, 5, 4, 8, 0, 0)   # Trimestre 2
    t3_inicio_bo = datetime(2026, 9, 7, 8, 0, 0)    # Trimestre 3 (a futuro respecto a "hoy")
    t1_inicio = t1_inicio_bo.replace(tzinfo=BOLIVIA_TZ).astimezone(UTC).replace(tzinfo=None)
    t2_inicio = t2_inicio_bo.replace(tzinfo=BOLIVIA_TZ).astimezone(UTC).replace(tzinfo=None)
    t3_inicio = t3_inicio_bo.replace(tzinfo=BOLIVIA_TZ).astimezone(UTC).replace(tzinfo=None)

    tareas_data = [
        # --- Matemática ---
        (curso_mate.id, 0, "Ejercicios de ecuaciones lineales", "Resuelve 12 ecuaciones de primer grado. Entrega escaneada en PDF.",
         t1_inicio + timedelta(days=12), 20, 1),
        (curso_mate.id, 0, "Prueba escrita - Ecuaciones", "Evaluación en clase sobre despeje de ecuaciones.",
         t1_inicio + timedelta(days=20), 25, 1),
        (curso_mate.id, 1, "Gráfica de funciones cuadráticas", "Grafica 5 funciones indicando vértice y raíces.",
         t1_inicio + timedelta(days=35), 20, 1),
        (curso_mate.id, 1, "Cuestionario de funciones", "Responde 10 preguntas teórico-prácticas sobre funciones.",
         t1_inicio + timedelta(days=45), 15, 1),
        (curso_mate.id, 2, "Práctica de geometría básica", "Resuelve 5 ejercicios de áreas y perímetros.",
         t1_inicio + timedelta(days=55), 10, 1),
        (curso_mate.id, 0, "Participación y puntualidad", "Asistencia, participación activa y entrega puntual de trabajos.",
         t1_inicio + timedelta(days=60), 10, 1),
        (curso_mate.id, 2, "Problemas de geometría", "Resuelve 8 problemas con teorema de Pitágoras.",
         t2_inicio + timedelta(days=10), 20, 2),
        (curso_mate.id, 3, "Ejercicios de estadística", "Calcula media, mediana y moda de 3 conjuntos de datos.",
         t2_inicio + timedelta(days=20), 25, 2),
        (curso_mate.id, 1, "Examen funciones avanzadas", "Evaluación escrita sobre transformaciones de funciones cuadráticas.",
         t2_inicio + timedelta(days=30), 25, 2),
        (curso_mate.id, 0, "Laboratorio ecuaciones avanzadas", "Resuelve sistemas de ecuaciones 2x2 por sustitución e igualación.",
         t2_inicio + timedelta(days=58), 10, 2),

        # --- Física ---
        (curso_fisica.id, 0, "Problemas de MRU y MRUV", "Resuelve 8 problemas de movimiento rectilíneo.",
         t1_inicio + timedelta(days=10), 20, 1),
        (curso_fisica.id, 0, "Laboratorio virtual de caída libre", "Simulación y análisis de caída libre con datos.",
         t1_inicio + timedelta(days=22), 15, 1),
        (curso_fisica.id, 1, "Ejercicios de dinámica", "Aplica las leyes de Newton a 6 situaciones.",
         t1_inicio + timedelta(days=40), 20, 1),
        (curso_fisica.id, 1, "Prueba de leyes de Newton", "Evaluación escrita con problemas de aplicación.",
         t1_inicio + timedelta(days=50), 20, 1),
        (curso_fisica.id, 0, "Disciplina en laboratorio", "Comportamiento adecuado durante prácticas de laboratorio.",
         t1_inicio + timedelta(days=60), 10, 1),
        (curso_fisica.id, 2, "Cuestionario de conceptos físicos", "Responde 10 preguntas teóricas sobre cinemática y dinámica.",
         t1_inicio + timedelta(days=58), 10, 1),
        (curso_fisica.id, 2, "Problemas de trabajo y energía", "Resuelve 6 problemas de conservación de energía.",
         t2_inicio + timedelta(days=55), 20, 2),

        # --- Comunicación y Lenguajes ---
        (curso_comunicacion.id, 0, "Ejercicios de ortografía", "Corrige 20 oraciones con errores de tildación y puntuación.",
         t1_inicio + timedelta(days=12), 15, 1),
        (curso_comunicacion.id, 0, "Dictado calificado", "Texto de 150 palabras con reglas ortográficas.",
         t1_inicio + timedelta(days=18), 10, 1),
        (curso_comunicacion.id, 1, "Redacción: texto narrativo", "Escribe un cuento de 2 páginas sobre tu comunidad.",
         t1_inicio + timedelta(days=32), 25, 1),
        (curso_comunicacion.id, 1, "Análisis de texto descriptivo", "Identifica recursos literarios en un texto dado.",
         t1_inicio + timedelta(days=45), 20, 1),
        (curso_comunicacion.id, 0, "Participación en clase", "Intervenciones pertinentes y respeto a la opinión de los compañeros.",
         t1_inicio + timedelta(days=60), 5, 1),
        (curso_comunicacion.id, 2, "Ejercicios de comprensión lectora", "Lee un texto y responde 10 preguntas de comprensión.",
         t1_inicio + timedelta(days=55), 10, 1),
        (curso_comunicacion.id, 2, "Ensayo: literatura boliviana", "Investiga y escribe sobre un autor boliviano.",
         t2_inicio + timedelta(days=60), 25, 2),

        # --- Ciencias Sociales ---
        (curso_sociales.id, 0, "Cuestionario: la Colonia en Bolivia", "Responde 12 preguntas sobre el periodo colonial y la mita.",
         t1_inicio + timedelta(days=15), 20, 1),
        (curso_sociales.id, 0, "Línea de tiempo de rebeliones indígenas", "Elabora una línea de tiempo de las rebeliones del siglo XVIII.",
         t1_inicio + timedelta(days=28), 15, 1),
        (curso_sociales.id, 1, "Ensayo: la independencia de Bolivia", "Escribe un ensayo de 2 páginas sobre el proceso independentista.",
         t1_inicio + timedelta(days=42), 25, 1),
        (curso_sociales.id, 1, "Mapa conceptual: fundación de Bolivia", "Elabora un mapa conceptual del proceso de fundación en 1825.",
         t1_inicio + timedelta(days=52), 15, 1),
        (curso_sociales.id, 2, "Mapa de regiones productivas", "Dibuja y describe las principales regiones productivas de Bolivia.",
         t2_inicio + timedelta(days=50), 20, 2),

        # --- Biología-Geografía ---
        (curso_bio.id, 0, "Maqueta de la célula", "Elabora una maqueta 3D de una célula vegetal.",
         t1_inicio + timedelta(days=15), 20, 1),
        (curso_bio.id, 0, "Cuestionario de biología celular", "Responde 15 preguntas sobre organelos y funciones.",
         t1_inicio + timedelta(days=22), 20, 1),
        (curso_bio.id, 1, "Cruces genéticos", "Resuelve 5 cruces monohíbridos con cuadros de Punnett.",
         t1_inicio + timedelta(days=38), 20, 1),
        (curso_bio.id, 1, "Prueba de genética", "Evaluación escrita con problemas de herencia.",
         t1_inicio + timedelta(days=48), 20, 1),
        (curso_bio.id, 0, "Cuidado del material", "Responsabilidad en el uso de materiales de laboratorio.",
         t1_inicio + timedelta(days=60), 5, 1),
        (curso_bio.id, 2, "Mapa conceptual de ecosistemas", "Elabora un mapa con los ecosistemas de Bolivia.",
         t1_inicio + timedelta(days=58), 10, 1),
        (curso_bio.id, 2, "Mapa de ecosistemas", "Dibuja y describe 3 ecosistemas de Bolivia.",
         t2_inicio + timedelta(days=53), 20, 2),

        # --- Inglés ---
        (curso_ingles.id, 0, "Verb to be worksheet", "Complete 30 sentences with am / is / are.",
         t1_inicio + timedelta(days=12), 15, 1),
        (curso_ingles.id, 0, "Simple present exercises", "Conjugate 20 verbs in simple present tense.",
         t1_inicio + timedelta(days=22), 15, 1),
        (curso_ingles.id, 1, "My daily routine", "Write a paragraph describing your daily routine.",
         t1_inicio + timedelta(days=35), 20, 1),
        (curso_ingles.id, 1, "Vocabulary quiz", "Match 30 words with their meanings.",
         t1_inicio + timedelta(days=48), 10, 1),
        (curso_ingles.id, 0, "Effort and participation", "Actitud positiva y participación activa en clase.",
         t1_inicio + timedelta(days=60), 5, 1),
        (curso_ingles.id, 2, "Reading comprehension", "Read a short text and answer 5 questions.",
         t1_inicio + timedelta(days=55), 10, 1),
        (curso_ingles.id, 2, "Conversation video", "Record a 2-minute conversation introducing yourself.",
         t2_inicio + timedelta(days=56), 20, 2),
    ]

    def fecha_pub(fecha_limite, offset_semilla):
        dias_antes = 3 + (offset_semilla % 5)
        return fecha_limite - timedelta(days=dias_antes)

    tareas_creadas = []
    for i, (curso_id, mod_idx, titulo, instr, f_lim, puntaje, _trimestre) in enumerate(tareas_data):
        t = Tarea(
            modulo_id=modulos[curso_id][mod_idx].id,
            titulo=titulo,
            instrucciones=instr,
            fecha_publicacion=fecha_pub(f_lim, i * 7 + sum(ord(c) for c in titulo)),
            fecha_limite=f_lim,
            puntaje_maximo=puntaje,
        )
        db.session.add(t)
        tareas_creadas.append(t)
    db.session.commit()

    # -----------------------------------------------------------------
    # ENTREGAS Y CALIFICACIONES
    # Solo se generan entregas/calificaciones para tareas cuya fecha
    # límite ya pasó respecto a "hoy" (27/06/2026); las tareas futuras
    # (trimestre 2 avanzado) quedan pendientes, como en un curso real.
    # -----------------------------------------------------------------
    print("Creando entregas y calificaciones...")

    def generar_nota(seed, puntaje_max):
        base = [38, 42, 30, 45, 35, 40, 28, 37, 43, 33, 39, 41, 29, 44, 34, 36, 31, 46, 27, 32, 47, 26, 48, 25, 38]
        pct = (50 + (base[seed % len(base)] * seed) % 45) / 100
        return max(0, min(puntaje_max, round(puntaje_max * pct, 1)))

    curso_estudiantes = {}
    curso_docente = {}
    for curso_id, indices in inscripciones_plan:
        curso_estudiantes[curso_id] = indices
    for c in Curso.query.all():
        curso_docente[c.id] = c.docente_id

    retro_algunas = [
        "Excelente trabajo, sigue así.",
        "Buen esfuerzo, revisa los procedimientos.",
        "Puedes mejorar, practica más en casa.",
        "Muy bien, solo corrige los signos.",
        "Trabajo completo y ordenado.",
        "Debes repasar los conceptos básicos.",
        "Buena presentación, contenido adecuado.",
        "Faltan algunos ejercicios, completa la próxima.",
        "Muy buen análisis y razonamiento.",
        "Entrega a tiempo y bien resuelta.",
        "Confundiste algunos conceptos, repasa la teoría.",
        "Excelente dedicación, felicitaciones.",
        "Trabajo aceptable, puede mejorar.",
        "Muy buena redacción y ortografía.",
        "Bien resuelto, pero falta desarrollo en algunos.",
        "Cumple con lo solicitado.",
        "Demuestra comprensión del tema.",
        "Debe asistir a clases de reforzamiento.",
        "Notable esfuerzo, buen trabajo.",
        "Revisa las correcciones marcadas.",
    ]
    retro_idx = 0

    entrega_count = 0
    pendientes_count = 0
    for tarea in tareas_creadas:
        curso_id = tarea.modulo.curso_id
        indices = curso_estudiantes.get(curso_id, [])

        # Si la fecha límite todavía no llegó (respecto a "hoy"), la tarea
        # queda pendiente: no se generan entregas ni calificaciones.
        if tarea.fecha_limite > FECHA_HOY:
            pendientes_count += 1
            continue

        for est_idx in indices:
            est = estudiantes[est_idx]
            nota = generar_nota(est_idx * 7 + tarea.id, tarea.puntaje_maximo)

            if curso_id == curso_mate.id:
                if est_idx == 3:  # María Choque - bajo rendimiento
                    nota = round(tarea.puntaje_maximo * (0.15 + (tarea.id % 15) / 100), 1)
                elif est_idx == 6:  # Luis Quispe - rendimiento irregular
                    nota = round(tarea.puntaje_maximo * (0.30 + (tarea.id * 3 % 25) / 100), 1)
                elif est_idx == 8:  # Pedro Yujra - bajo en T1, mejora después
                    nota = round(tarea.puntaje_maximo * (0.25 + (tarea.id % 20) / 100), 1)

            retro = retro_algunas[retro_idx % len(retro_algunas)]
            retro_idx += 1

            semilla = est_idx * 13 + tarea.id * 7
            f_entrega = tarea.fecha_limite
            if semilla % 5 == 0:
                f_entrega = tarea.fecha_limite + timedelta(hours=6 + (semilla % 72))

            entrega = Entrega(
                tarea_id=tarea.id,
                estudiante_id=est.id,
                archivo=f"entregas/tarea_{tarea.id}_{est.email.split('@')[0]}.pdf",
                comentario=retro if retro_idx % 3 == 0 else None,
                estado="revisado",
                fecha_entrega=f_entrega,
            )
            db.session.add(entrega)
            db.session.flush()

            calif = Calificacion(
                entrega_id=entrega.id,
                docente_id=curso_docente[curso_id],
                nota=nota,
                retroalimentacion=retro,
            )
            db.session.add(calif)
            entrega_count += 1

    db.session.commit()
    print(f"  {entrega_count} entregas calificadas creadas.")
    print(f"  {pendientes_count} tareas quedan pendientes (fecha límite futura).")

    # -----------------------------------------------------------------
    # ANUNCIOS — contexto boliviano
    # -----------------------------------------------------------------
    print("Creando anuncios...")
    anuncios_data = [
        (curso_mate.id, "¡Bienvenidos a Matemática 4to de Secundaria!",
         "Bienvenidos al curso de Matemática. Esta gestión veremos ecuaciones lineales, funciones cuadráticas y geometría plana."),
        (curso_mate.id, "Recordatorio: Prueba de ecuaciones",
         "La prueba escrita de ecuaciones lineales será el viernes. Estudien los ejercicios de la guía y repasen en Khan Academy."),
        (curso_fisica.id, "Inicio de clases - Física 5to de Secundaria",
         "Bienvenidos al curso de Física correspondiente a la gestión 2026. Empezaremos con cinemática: MRU y MRUV."),
        (curso_fisica.id, "Resultados laboratorio virtual",
         "Las notas del laboratorio de caída libre ya están disponibles en el sistema. Revisen la retroalimentación."),
        (curso_comunicacion.id, "Bienvenida - Comunicación y Lenguajes",
         "Esta gestión trabajaremos ortografía, redacción y literatura boliviana en el marco del currículo del Ministerio de Educación."),
        (curso_comunicacion.id, "Concurso de ortografía de la unidad educativa",
         "El viernes 15 tendremos el concurso inter-aulas de ortografía. ¡Prepárense repasando las reglas de tildación!"),
        (curso_sociales.id, "Bienvenida - Ciencias Sociales 4to",
         "Iniciamos el estudio de la historia de Bolivia, desde la Colonia hasta la fundación del Estado Plurinacional en 1825."),
        (curso_sociales.id, "Salida pedagógica - Museo Nacional de Etnografía y Folklore",
         "Coordinaremos una visita al museo en La Paz como complemento de la unidad sobre la época colonial."),
        (curso_bio.id, "Inicio de Biología-Geografía 4to",
         "Comenzamos con biología celular. La maqueta de la célula se entrega en 2 semanas."),
        (curso_bio.id, "Material para genética",
         "Traer cuadros de Punnett impresos para la próxima clase de genética mendeliana."),
        (curso_ingles.id, "Welcome to English - 3rd of Secondary",
         "This school year (gestión 2026) we will study basic grammar and vocabulary following the national curriculum."),
        (curso_ingles.id, "Conversation video deadline",
         "Record your conversation video and submit it before the deadline. Practice with the unProfesor English resources."),
    ]
    anuncio_count = 0
    for curso_id, titulo, contenido in anuncios_data:
        db.session.add(Anuncio(curso_id=curso_id, titulo=titulo, contenido=contenido))
        anuncio_count += 1
    db.session.commit()

    # -----------------------------------------------------------------
    # RESUMEN FINAL
    # -----------------------------------------------------------------
    print("\n¡Datos de prueba creados exitosamente!")
    print("=" * 60)
    print("Credenciales de acceso:")
    print(f"  Admin:                 admin@colegio.bo / admin123")
    print(f"  Prof. Rosa Quispe:     rosa.quispe@colegio.bo / docente123")
    print(f"  Prof. Marcelo Choque:  marcelo.choque@colegio.bo / docente123")
    print(f"  Prof. Juana Pérez:     juana.perez@colegio.bo / docente123")
    print(f"  Prof. Franklin Yujra:  franklin.yujra@colegio.bo / docente123")
    print(f"  Todos los estudiantes: XXXXXX@colegio.bo / estudiante123")
    print("=" * 60)
    print(f"  {len(estudiantes)} estudiantes · {len(cursos)} cursos")
    print(f"  {sum(len(v) for v in modulos.values())} módulos")
    print(f"  {len(recursos_lista)} recursos (URLs raíz verificadas)")
    print(f"  {len(tareas_creadas)} tareas ({pendientes_count} pendientes, {len(tareas_creadas) - pendientes_count} ya calificadas)")
    print(f"  {entrega_count} entregas calificadas")
    print(f"  {anuncio_count} anuncios")
    print("=" * 60)