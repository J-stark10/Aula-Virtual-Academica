from datetime import datetime, timedelta
from app.app import create_app, db, bcrypt
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


with app.app_context():
    print("Limpiando base de datos...")
    db.drop_all()
    db.create_all()

    print("Creando usuarios...")

    admin = Usuario(
        nombre_completo="Lic. Juan Carlos Mamani",
        email="admin@colegio.bo",
        password=hash_pw("admin123"),
        rol="admin",
    )

    profe_rosa = Usuario(
        nombre_completo="Prof. Rosa Quispe Condori",
        email="rosa.quispe@colegio.bo",
        password=hash_pw("docente123"),
        rol="docente",
    )
    profe_marcelo = Usuario(
        nombre_completo="Prof. Marcelo Choque Huanca",
        email="marcelo.choque@colegio.bo",
        password=hash_pw("docente123"),
        rol="docente",
    )
    profe_juana = Usuario(
        nombre_completo="Prof. Juana Pérez Mamani",
        email="juana.perez@colegio.bo",
        password=hash_pw("docente123"),
        rol="docente",
    )

    db.session.add_all([admin, profe_rosa, profe_marcelo, profe_juana])
    db.session.commit()

    estudiantes_data = [
        ("Caleb Acarapi Pari", "caleb.acarapi@colegio.bo"),
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
        )
        estudiantes.append(est)
    db.session.add_all(estudiantes)
    db.session.commit()

    print("Creando categorías...")
    cat_exactas = Categoria(nombre="Ciencias Exactas", descripcion="Matemáticas, Física, Química")
    cat_naturales = Categoria(nombre="Ciencias Naturales", descripcion="Biología, Geografía, Ecología")
    cat_humanidades = Categoria(nombre="Humanidades", descripcion="Lenguaje, Historia, Filosofía")
    cat_idiomas = Categoria(nombre="Idiomas", descripcion="Inglés, Francés")
    cat_tecnica = Categoria(nombre="Educación Técnica", descripcion="Computación, Artes Plásticas, Música")
    db.session.add_all([cat_exactas, cat_naturales, cat_humanidades, cat_idiomas, cat_tecnica])
    db.session.commit()

    print("Creando cursos...")
    curso_mate = Curso(
        nombre="Matemáticas - 4to A",
        descripcion="Álgebra elemental, ecuaciones lineales, funciones cuadráticas y geometría básica.",
        categoria_id=cat_exactas.id, docente_id=profe_rosa.id,
    )
    curso_fisica = Curso(
        nombre="Física - 5to A",
        descripcion="Cinemática, dinámica, leyes de Newton, trabajo y energía.",
        categoria_id=cat_exactas.id, docente_id=profe_rosa.id,
    )
    curso_lenguaje = Curso(
        nombre="Lenguaje - 3ro A",
        descripcion="Gramática normativa, redacción de textos, análisis literario y ortografía.",
        categoria_id=cat_humanidades.id, docente_id=profe_marcelo.id,
    )
    curso_bio = Curso(
        nombre="Biología - 4to A",
        descripcion="Biología celular, genética mendeliana, ecosistemas y biodiversidad boliviana.",
        categoria_id=cat_naturales.id, docente_id=profe_marcelo.id,
    )
    curso_ingles = Curso(
        nombre="Inglés - 3ro A",
        descripcion="Gramática básica, vocabulario esencial, reading comprehension y conversación elemental.",
        categoria_id=cat_idiomas.id, docente_id=profe_juana.id,
    )
    cursos = [curso_mate, curso_fisica, curso_lenguaje, curso_bio, curso_ingles]
    db.session.add_all(cursos)
    db.session.commit()

    print("Inscribiendo estudiantes...")
    inscripciones_plan = [
        (curso_mate.id, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]),
        (curso_fisica.id, [0, 1, 2, 3, 4, 12, 13, 14, 15, 16, 17]),
        (curso_lenguaje.id, [2, 3, 4, 5, 6, 7, 10, 11, 18, 19, 20, 21]),
        (curso_bio.id, [8, 9, 12, 13, 14, 15, 22, 23, 24, 0]),
        (curso_ingles.id, [16, 17, 18, 19, 20, 21, 22, 23, 24, 1]),
    ]
    inscripciones = []
    for curso_id, indices in inscripciones_plan:
        for idx in indices:
            inscripciones.append(Inscripcion(curso_id=curso_id, estudiante_id=estudiantes[idx].id))
    db.session.add_all(inscripciones)
    db.session.commit()

    print("Creando módulos...")

    modulos_data = {
        curso_mate.id: [
            ("Unidad 1 - Ecuaciones Lineales", "Resolución de ecuaciones de primer grado con una incógnita.", 1),
            ("Unidad 2 - Funciones Cuadráticas", "Gráfica de parábolas, vértice, eje de simetría y raíces.", 2),
            ("Unidad 3 - Geometría Plana", "Ángulos, triángulos, teorema de Pitágoras y áreas.", 3),
            ("Unidad 4 - Estadística y Probabilidad", "Media, mediana, moda, probabilidad simple y compuesta.", 4),
            ("Unidad 5 - Razones y Proporciones", "Regla de tres, porcentajes, repartos proporcionales.", 5),
        ],
        curso_fisica.id: [
            ("Unidad 1 - Cinemática", "MRU, MRUV, caída libre y gráficas de movimiento.", 1),
            ("Unidad 2 - Dinámica", "Leyes de Newton, fuerza, masa y aceleración.", 2),
            ("Unidad 3 - Trabajo y Energía", "Trabajo mecánico, energía cinética y potencial.", 3),
        ],
        curso_lenguaje.id: [
            ("Unidad 1 - Gramática y Ortografía", "Reglas ortográficas, tildación y signos de puntuación.", 1),
            ("Unidad 2 - Redacción de Textos", "Estructura del párrafo, textos narrativos y descriptivos.", 2),
            ("Unidad 3 - Literatura Boliviana", "Autores representativos: Alcides Arguedas, Adela Zamudio.", 3),
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

    print("Creando recursos...")
    recursos_lista = [
        (curso_mate.id, 0, "Video - Solución de ecuaciones lineales", "enlace", "https://www.youtube.com/watch?v=ejemplo_ecuaciones"),
        (curso_mate.id, 1, "PDF - Ejercicios de funciones cuadráticas", "enlace", "https://ejemplo.com/funciones_cuadraticas.pdf"),
        (curso_mate.id, 2, "Video - Teorema de Pitágoras explicado", "enlace", "https://www.youtube.com/watch?v=ejemplo_pitagoras"),
        (curso_fisica.id, 0, "PDF - Guía de ejercicios de cinemática", "enlace", "https://ejemplo.com/guia_cinematica.pdf"),
        (curso_fisica.id, 1, "Video - Segunda ley de Newton", "enlace", "https://www.youtube.com/watch?v=ejemplo_newton"),
        (curso_fisica.id, 2, "PDF - Problemas de trabajo y energía", "enlace", "https://ejemplo.com/trabajo_energia.pdf"),
        (curso_lenguaje.id, 0, "PDF - Reglas de tildación", "enlace", "https://ejemplo.com/reglas_tildacion.pdf"),
        (curso_lenguaje.id, 1, "Video - Cómo redactar un párrafo", "enlace", "https://www.youtube.com/watch?v=ejemplo_redaccion"),
        (curso_lenguaje.id, 2, "PDF - Poesía de Adela Zamudio", "enlace", "https://ejemplo.com/adela_zamudio.pdf"),
        (curso_bio.id, 0, "Video - La célula y sus partes", "enlace", "https://www.youtube.com/watch?v=ejemplo_celula"),
        (curso_bio.id, 1, "PDF - Ejercicios de genética mendeliana", "enlace", "https://ejemplo.com/genetica.pdf"),
        (curso_bio.id, 2, "PDF - Ecosistemas de Bolivia", "enlace", "https://ejemplo.com/ecosistemas_bolivia.pdf"),
        (curso_ingles.id, 0, "PDF - Verb to be exercises", "enlace", "https://ejemplo.com/verb_to_be.pdf"),
        (curso_ingles.id, 1, "Video - Daily routines vocabulary", "enlace", "https://www.youtube.com/watch?v=ejemplo_routines"),
        (curso_ingles.id, 2, "PDF - Conversation practice", "enlace", "https://ejemplo.com/conversation.pdf"),
        (curso_mate.id, 3, "PDF - Guía de estadística básica", "enlace", "https://ejemplo.com/estadistica.pdf"),
        (curso_mate.id, 3, "Video - Cómo calcular la media y mediana", "enlace", "https://www.youtube.com/watch?v=ejemplo_media"),
        (curso_mate.id, 4, "PDF - Ejercicios de regla de tres", "enlace", "https://ejemplo.com/regla_tres.pdf"),
        (curso_mate.id, 4, "Video - Repartos proporcionales", "enlace", "https://www.youtube.com/watch?v=ejemplo_repartos"),
    ]
    for curso_id, mod_idx, titulo, tipo, url in recursos_lista:
        r = Recurso(
            modulo_id=modulos[curso_id][mod_idx].id,
            titulo=titulo, tipo=tipo, url_enlace=url,
        )
        db.session.add(r)
    db.session.commit()

    print("Creando tareas...")

    t1_inicio = datetime(2026, 3, 2)
    t2_inicio = datetime(2026, 6, 1)
    t3_inicio = datetime(2026, 9, 7)

    tareas_data = [
        (curso_mate.id, 0, "Ejercicios de ecuaciones lineales", "Resuelve 12 ecuaciones de primer grado. Entrega escaneada en PDF.",
         t1_inicio + timedelta(days=5), 20, 1),
        (curso_mate.id, 0, "Prueba escrita - Ecuaciones", "Evaluación en clase sobre despeje de ecuaciones.",
         t1_inicio + timedelta(days=12), 25, 1),
        (curso_mate.id, 1, "Gráfica de funciones cuadráticas", "Grafica 5 funciones indicando vértice y raíces.",
         t1_inicio + timedelta(days=30), 20, 1),
        (curso_mate.id, 1, "Cuestionario de funciones", "Responde 10 preguntas teórico-prácticas sobre funciones.",
         t1_inicio + timedelta(days=40), 15, 1),
        (curso_mate.id, 0, "Participación y puntualidad", "Asistencia, participación activa y entrega puntual de trabajos.",
         t1_inicio + timedelta(days=60), 10, 1),
        (curso_mate.id, 2, "Práctica de geometría básica", "Resuelve 5 ejercicios de áreas y perímetros.",
         t1_inicio + timedelta(days=50), 10, 1),
        (curso_fisica.id, 0, "Problemas de MRU y MRUV", "Resuelve 8 problemas de movimiento rectilíneo.",
         t1_inicio + timedelta(days=4), 20, 1),
        (curso_fisica.id, 0, "Laboratorio virtual de caída libre", "Simulación y análisis de caída libre con datos.",
         t1_inicio + timedelta(days=15), 15, 1),
        (curso_fisica.id, 1, "Ejercicios de dinámica", "Aplica las leyes de Newton a 6 situaciones.",
         t1_inicio + timedelta(days=35), 20, 1),
        (curso_fisica.id, 1, "Prueba de leyes de Newton", "Evaluación escrita con problemas de aplicación.",
         t1_inicio + timedelta(days=45), 20, 1),
        (curso_fisica.id, 0, "Disciplina en laboratorio", "Comportamiento adecuado durante prácticas de laboratorio.",
         t1_inicio + timedelta(days=60), 10, 1),
        (curso_fisica.id, 2, "Cuestionario de conceptos físicos", "Responde 10 preguntas teóricas sobre cinemática y dinámica.",
         t1_inicio + timedelta(days=50), 10, 1),
        (curso_fisica.id, 0, "Experimento casero: caída libre", "Realiza un experimento con objetos en caída y registra los resultados.",
         t1_inicio + timedelta(days=55), 5, 1),
        (curso_lenguaje.id, 0, "Ejercicios de ortografía", "Corrige 20 oraciones con errores de tildación y puntuación.",
         t1_inicio + timedelta(days=5), 15, 1),
        (curso_lenguaje.id, 0, "Dictado calificado", "Texto de 150 palabras con reglas ortográficas.",
         t1_inicio + timedelta(days=10), 10, 1),
        (curso_lenguaje.id, 1, "Redacción: texto narrativo", "Escribe un cuento de 2 páginas sobre tu comunidad.",
         t1_inicio + timedelta(days=25), 25, 1),
        (curso_lenguaje.id, 1, "Análisis de texto descriptivo", "Identifica recursos literarios en un texto dado.",
         t1_inicio + timedelta(days=38), 20, 1),
        (curso_lenguaje.id, 0, "Participación en clase", "Intervenciones pertinentes y respeto a la opinión de los compañeros.",
         t1_inicio + timedelta(days=60), 5, 1),
        (curso_lenguaje.id, 0, "Orden y respeto en clase", "Mantener el orden, escuchar activamente y respetar los turnos.",
         t1_inicio + timedelta(days=60), 5, 1),
        (curso_lenguaje.id, 2, "Ejercicios de comprensión lectora", "Lee un texto y responde 10 preguntas de comprensión.",
         t1_inicio + timedelta(days=48), 10, 1),
        (curso_lenguaje.id, 2, "Exposición oral: mi autor favorito", "Prepara una exposición de 5 minutos sobre un autor boliviano.",
         t1_inicio + timedelta(days=58), 10, 1),
        (curso_bio.id, 0, "Maqueta de la célula", "Elabora una maqueta 3D de una célula vegetal.",
         t1_inicio + timedelta(days=8), 20, 1),
        (curso_bio.id, 0, "Cuestionario de biología celular", "Responde 15 preguntas sobre organelos y funciones.",
         t1_inicio + timedelta(days=15), 20, 1),
        (curso_bio.id, 1, "Cruces genéticos", "Resuelve 5 cruces monohíbridos con cuadros de Punnett.",
         t1_inicio + timedelta(days=30), 20, 1),
        (curso_bio.id, 1, "Prueba de genética", "Evaluación escrita con problemas de herencia.",
         t1_inicio + timedelta(days=42), 20, 1),
        (curso_bio.id, 0, "Cuidado del material", "Responsabilidad en el uso de materiales de laboratorio.",
         t1_inicio + timedelta(days=60), 5, 1),
        (curso_bio.id, 1, "Respeto por la naturaleza", "Actitud positiva hacia el medio ambiente y los ecosistemas.",
         t1_inicio + timedelta(days=60), 5, 1),
        (curso_bio.id, 2, "Mapa conceptual de ecosistemas", "Elabora un mapa con los ecosistemas de Bolivia.",
         t1_inicio + timedelta(days=52), 10, 1),
        (curso_ingles.id, 0, "Verb to be worksheet", "Complete 30 sentences with am / is / are.",
         t1_inicio + timedelta(days=5), 15, 1),
        (curso_ingles.id, 0, "Simple present exercises", "Conjugate 20 verbs in simple present tense.",
         t1_inicio + timedelta(days=15), 15, 1),
        (curso_ingles.id, 1, "My daily routine", "Write a paragraph describing your daily routine.",
         t1_inicio + timedelta(days=28), 20, 1),
        (curso_ingles.id, 1, "Vocabulary quiz", "Match 30 words with their meanings.",
         t1_inicio + timedelta(days=40), 10, 1),
        (curso_ingles.id, 0, "Effort and participation", "Actitud positiva y participación activa en clase.",
         t1_inicio + timedelta(days=60), 5, 1),
        (curso_ingles.id, 1, "Responsibility", "Entrega puntual de tareas, orden en el cuaderno y respeto.",
         t1_inicio + timedelta(days=60), 5, 1),
        (curso_ingles.id, 2, "Reading comprehension", "Read a short text and answer 5 questions.",
         t1_inicio + timedelta(days=48), 10, 1),
        (curso_ingles.id, 2, "Listening practice", "Listen to an audio and complete the exercises.",
         t1_inicio + timedelta(days=52), 10, 1),
        (curso_ingles.id, 2, "Write about your family", "Describe your family members in a short paragraph.",
         t1_inicio + timedelta(days=58), 10, 1),
        (curso_mate.id, 2, "Problemas de geometría", "Resuelve 8 problemas con teorema de Pitágoras.",
         t2_inicio + timedelta(days=5), 20, 2),
        (curso_mate.id, 3, "Ejercicios de estadística", "Calcula media, mediana y moda de 3 conjuntos de datos.",
         t2_inicio + timedelta(days=12), 25, 2),
        (curso_mate.id, 1, "Examen funciones avanzadas", "Evaluación escrita sobre trasformaciones de funciones cuadráticas.",
         t2_inicio + timedelta(days=20), 25, 2),
        (curso_mate.id, 4, "Problemas de proporciones", "Resuelve 6 problemas de regla de tres y porcentajes.",
         t2_inicio + timedelta(days=28), 20, 2),
        (curso_mate.id, 0, "Laboratorio ecuaciones avanzadas", "Resuelve sistemas de ecuaciones 2x2 por sustitución e igualación.",
         t2_inicio + timedelta(days=35), 10, 2),
        (curso_mate.id, 3, "Proyecto final de estadística", "Encuesta en el curso, tabulación, gráficos y conclusiones.",
         t3_inicio + timedelta(days=10), 30, 3),
        (curso_mate.id, 4, "Taller de proporciones", "Resuelve 10 problemas de repartos proporcionales y porcentajes.",
         t3_inicio + timedelta(days=18), 20, 3),
        (curso_mate.id, 2, "Examen de geometría analítica", "Coordenadas, distancia entre puntos y pendiente de rectas.",
         t3_inicio + timedelta(days=25), 25, 3),
        (curso_mate.id, 0, "Prueba final ecuaciones", "Evaluación final con ecuaciones lineales, cuadráticas y sistemas 2x2.",
         t3_inicio + timedelta(days=32), 25, 3),
        (curso_fisica.id, 2, "Problemas de trabajo y energía", "Resuelve 6 problemas de conservación de energía.",
         t2_inicio + timedelta(days=3), 20, 2),
        (curso_lenguaje.id, 2, "Ensayo: literatura boliviana", "Investiga y escribe sobre un autor boliviano.",
         t2_inicio + timedelta(days=7), 25, 2),
        (curso_bio.id, 2, "Mapa de ecosistemas", "Dibuja y describe 3 ecosistemas de Bolivia.",
         t2_inicio + timedelta(days=4), 20, 2),
        (curso_ingles.id, 2, "Conversation video", "Record a 2-minute conversation introducing yourself.",
         t2_inicio + timedelta(days=6), 20, 2),
    ]

    def fecha_pub(fecha_limite, offset_semilla):
        dias_antes = 3 + (offset_semilla % 5)
        return fecha_limite - timedelta(days=dias_antes)

    tareas_creadas = []
    for i, (curso_id, mod_idx, titulo, instr, f_lim, puntaje, trim) in enumerate(tareas_data):
        t = Tarea(
            modulo_id=modulos[curso_id][mod_idx].id,
            titulo=titulo,
            instrucciones=instr,
            fecha_publicacion=fecha_pub(f_lim, i * 7 + sum(ord(c) for c in titulo)),
            fecha_limite=f_lim,
            puntaje_maximo=puntaje,
            trimestre=trim,
        )
        db.session.add(t)
        tareas_creadas.append((curso_id, mod_idx, t, trim))
    db.session.commit()

    print("Creando entregas y calificaciones...")
    print("  Trimestre 1: todos los cursos")
    print("  Trimestres 2 y 3: solo Matemáticas - 4to A")

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
    for curso_id, mod_idx, tarea, trim in tareas_creadas:
        if trim != 1 and curso_id != curso_mate.id:
            continue
        indices = curso_estudiantes.get(curso_id, [])
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

    print("Creando anuncios...")
    anuncios_data = [
        (curso_mate.id, "¡Bienvenidos a Matemáticas 4to!",
         "Bienvenidos al curso de Matemáticas. Este trimestre veremos ecuaciones lineales y funciones cuadráticas."),
        (curso_mate.id, "Recordatorio: Prueba de ecuaciones",
         "La prueba escrita de ecuaciones lineales será el viernes. Estudien los ejercicios de la guía."),
        (curso_fisica.id, "Inicio de clases - Física 5to",
         "Bienvenidos al curso de Física. Empezaremos con cinemática."),
        (curso_fisica.id, "Resultados laboratorio virtual",
         "Las notas del laboratorio de caída libre ya están disponibles en el sistema."),
        (curso_lenguaje.id, "Bienvenida - Lenguaje 3ro",
         "Este trimestre trabajaremos ortografía y redacción."),
        (curso_lenguaje.id, "Concurso de ortografía",
         "El viernes 15 tendremos el concurso inter-aulas de ortografía. ¡Prepárense!"),
        (curso_bio.id, "Inicio de Biología 4to",
         "Comenzamos con biología celular. La maqueta de la célula se entrega en 2 semanas."),
        (curso_bio.id, "Material para genética",
         "Traer cuadros de Punnett impresos para la próxima clase de genética."),
        (curso_ingles.id, "Welcome to English 3rd Grade",
         "This trimester we will study basic grammar and vocabulary."),
        (curso_ingles.id, "Conversation video deadline",
         "Record your conversation video and submit it before the deadline."),
    ]
    anuncio_count = 0
    for curso_id, titulo, contenido in anuncios_data:
        db.session.add(Anuncio(curso_id=curso_id, titulo=titulo, contenido=contenido))
        anuncio_count += 1
    db.session.commit()

    total_tareas_t1 = sum(1 for _, _, _, t in tareas_creadas if t == 1)
    total_tareas_t2 = sum(1 for _, _, _, t in tareas_creadas if t == 2)
    total_tareas_t3 = sum(1 for _, _, _, t in tareas_creadas if t == 3)
    print("\n¡Datos de prueba creados exitosamente!")
    print("=" * 55)
    print("Credenciales de acceso:")
    print(f"  Admin:               admin@colegio.bo / admin123")
    print(f"  Prof. Rosa Quispe:   rosa.quispe@colegio.bo / docente123")
    print(f"  Prof. Marcelo Choque: marcelo.choque@colegio.bo / docente123")
    print(f"  Prof. Juana Pérez:   juana.perez@colegio.bo / docente123")
    print(f"  Todos los estudiantes: XXXXXX@colegio.bo / estudiante123")
    print("=" * 55)
    print(f"  {len(estudiantes)} estudiantes · {len(cursos)} cursos")
    print(f"  Tareas: {total_tareas_t1} T1 · {total_tareas_t2} T2 · {total_tareas_t3} T3")
    print(f"  {entrega_count} entregas calificadas")
    print(f"  Curso completo (T1+T2+T3): Matemáticas - 4to A")
    print(f"  {anuncio_count} anuncios")
    print("=" * 55)

