SELECT DISTINCT Autor.nombre
FROM Autor
JOIN Libro ON Autor.nombre = Libro.autor
JOIN Valoracion ON Valoracion.bookid = Libro.bookid
WHERE Autor.genero = 'female'
AND Valoracion.calificacion > 4.7
AND 'Fiction' = ANY(Libro.generos);
