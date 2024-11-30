from flask import Flask, render_template, request
import psycopg2
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost/3tablasSQL'
db = SQLAlchemy(app)

# Conexión a la base de datos
# Conexión a la base de datos
def get_db_connection():
    return psycopg2.connect(
        dbname="3tablasSQL",
        user="postgres",
        host="localhost"
    )

# Consulta 1: País con más premios

# Consulta 1: País con más premios
@app.route('/consulta1', methods=['GET', 'POST'])
def consulta1():
    connection = get_db_connection()
    cursor = connection.cursor()

    # Obtener el número de página desde la URL o el formulario (por defecto, página 1)
    pagina = request.args.get('pagina', 1, type=int)

    # Validar la página para asegurarnos de que sea un número válido
    if pagina < 1:
        pagina = 1  # Si la página es menor que 1, ponerla en 1

    PREMIOS_POR_PAGINA = 20
    # Cálculo del offset
    offset = (pagina - 1) * PREMIOS_POR_PAGINA

    # Obtener la lista de premios con paginación
    cursor.execute('''
        SELECT premio
        FROM vista_premios_distintos
        ORDER BY premio ASC
        LIMIT %s OFFSET %s;
    ''', (PREMIOS_POR_PAGINA, offset))

    premios = [row[0] for row in cursor.fetchall()]

    # Obtener el total de premios para la paginación
    cursor.execute('SELECT COUNT(*) FROM vista_premios_distintos;')
    total_premios = cursor.fetchone()[0]
    total_paginas = (total_premios // PREMIOS_POR_PAGINA) + (1 if total_premios % PREMIOS_POR_PAGINA > 0 else 0)

    # Si se envía el formulario
    resultado = None
    if request.method == 'POST':
        premio_seleccionado = request.form.get('premio')
        
        # Realizar la consulta para obtener el país con más premios
        cursor.execute('''
            WITH paises_ranking AS (
                SELECT Autor.pais AS pais, COUNT(*) AS numero_premios
                FROM Autor
                JOIN Libro ON Libro.autor = Autor.nombre
                WHERE Libro.premios LIKE %s
                GROUP BY Autor.pais
                ORDER BY numero_premios DESC
            )
            SELECT * FROM paises_ranking
            LIMIT 1;
        ''', (f'%{premio_seleccionado}%',))  # Usando placeholder para evitar inyección SQL
        
        resultado = cursor.fetchone()

    connection.close()
    
    # Pasar todos los datos a la plantilla
    return render_template('consulta1.html', premios=premios, resultado=resultado, pagina=pagina, total_paginas=total_paginas)


# Consulta 2: Paginación con selección de página para autores y resultados
@app.route('/consulta2', methods=['GET', 'POST'])
def consulta2():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener el número de página actual para autores desde la URL o por defecto 1
    pagina_autores = request.args.get('pagina_autores', 1, type=int)
    if pagina_autores < 1:
        pagina_autores = 1

    AUTORES_POR_PAGINA = 20  # Cantidad de autores por página
    offset_autores = (pagina_autores - 1) * AUTORES_POR_PAGINA

    # Obtener lista de autores con paginación
    cursor.execute('''
        SELECT autor
        FROM vista_autores
        ORDER BY autor
        LIMIT %s OFFSET %s;
    ''', (AUTORES_POR_PAGINA, offset_autores))
    autores = [row[0] for row in cursor.fetchall()]

    # Obtener lista de géneros desde la vista materializada (sin paginación)
    cursor.execute('''
        SELECT genero
        FROM vista_generos
        ORDER BY genero;
    ''')
    generos = [row[0] for row in cursor.fetchall()]

    # Calcular el número total de páginas para autores
    cursor.execute('SELECT COUNT(*) FROM vista_autores;')
    total_autores = cursor.fetchone()[0]
    total_paginas_autores = (total_autores // AUTORES_POR_PAGINA) + (1 if total_autores % AUTORES_POR_PAGINA > 0 else 0)

    resultado = None
    if request.method == 'POST':
        # Capturar inputs del usuario
        autor_escrito = request.form.get('autor_escrito', '').strip()
        autor_seleccionado = request.form.get('autor_seleccionado')
        genero_escrito = request.form.get('genero_escrito', '').strip()
        genero_seleccionado = request.form.get('genero_seleccionado')
        calificacion = request.form.get('calificacion')

        # Priorizar el autor escrito y género escrito si se ingresaron, de lo contrario usar los seleccionados
        autor = autor_escrito if autor_escrito else autor_seleccionado
        genero = genero_escrito if genero_escrito else genero_seleccionado

        # Validar inputs del usuario
        if autor and genero and calificacion:
            try:
                calificacion = float(calificacion)  # Asegurar que sea numérico

                # Realizar la consulta principal
                cursor.execute('''
                    SELECT Libro.titulo, Valoracion.calificacion
                    FROM Libro
                    JOIN Autor ON Libro.autor = Autor.nombre
                    JOIN Valoracion ON Valoracion.bookid = Libro.bookid
                    WHERE Autor.nombre = %s
                      AND %s = ANY(Libro.generos)
                      AND Valoracion.calificacion > %s
                    ORDER BY Valoracion.calificacion DESC;
                ''', (autor, genero, calificacion))  # Uso de parámetros en vez de concatenación
                resultado = cursor.fetchall()
            except ValueError:
                resultado = []

    conn.close()

    # Pasar los resultados a la plantilla
    return render_template(
        'consulta2.html',
        autores=autores,
        generos=generos,
        resultado=resultado,
        pagina_autores=pagina_autores,
        total_paginas_autores=total_paginas_autores
    )

# Consulta 3: Otro ejemplo (ajustar según tu caso)
@app.route('/consulta3', methods=['GET', 'POST'])
def consulta3():
    from sqlalchemy import text

    # Obtener los géneros de libros desde la vista materializada
    generos_libros = [row[0] for row in db.session.execute(
        text('SELECT genero FROM vista_generos ORDER BY genero')
    ).fetchall()]

    resultados = None  # Inicialización de resultados
    error = None  # Inicialización de errores

    if request.method == 'POST':
        # Obtener datos del formulario
        genero_autor = request.form.get('genero_autor')  # 'male' o 'female'
        genero_libro = request.form.get('genero_libro')  # Género de libro seleccionado
        calificacion_minima = request.form.get('calificacion_minima')  # Calificación mínima

        # Validar campos ingresados
        if not genero_autor or not genero_libro or not calificacion_minima:
            error = "Por favor, complete todos los campos."
        else:
            try:
                # Convertir la calificación mínima a float
                calificacion_minima = float(calificacion_minima)

                # Consulta SQL ajustada a los parámetros del formulario
                base_query = '''
                    SELECT DISTINCT Autor.nombre
                    FROM Autor
                    JOIN Libro ON Autor.nombre = Libro.autor
                    JOIN Valoracion ON Valoracion.bookid = Libro.bookid
                    WHERE Autor.genero = :genero_autor
                      AND :genero_libro = ANY(Libro.generos)
                      AND Valoracion.calificacion > :calificacion_minima;
                '''
                query = text(base_query)

                # Ejecutar la consulta con los parámetros ingresados
                resultados = db.session.execute(query, {
                    'genero_autor': genero_autor,
                    'genero_libro': genero_libro,
                    'calificacion_minima': calificacion_minima
                }).fetchall()
            except Exception as e:
                error = f"Error al ejecutar la consulta: {str(e)}"

    # Renderizar la plantilla con los géneros y resultados
    return render_template(
        'consulta3.html',
        generos_libros=generos_libros,
        resultados=resultados,
        error=error
    )



# Bloque principal
if __name__ == '__main__':
    app.run(debug=True)