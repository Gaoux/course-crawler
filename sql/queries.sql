-- Query to dentify which URL a given word is located at.
SELECT c.url as URL
FROM course c
WHERE c.title LIKE '%word%' 
OR c.description LIKE '%word%';