WITH paises_ranking AS (
    SELECT Autor.pais AS pais, COUNT(*) AS numero_premios
    FROM Autor
    JOIN Libro ON Libro.autor = Autor.nombre
    WHERE Libro.premios LIKE '%LovelyBooks Leserpreis Nominee for Allgemeine Literatur (2009)%'
    GROUP BY Autor.pais
    ORDER BY numero_premios DESC
)
SELECT * FROM paises_ranking
LIMIT 1;
