SELECT Libro.titulo, Valoracion.calificacion
FROM Libro
JOIN Autor ON Libro.autor = Autor.nombre
JOIN Valoracion ON Valoracion.bookid = Libro.bookid
WHERE Autor.nombre = 'george r.r. martin'
AND 'Fantasy' = ANY(Libro.generos)
AND Valoracion.calificacion > 3.71;
