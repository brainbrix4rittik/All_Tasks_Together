--ALTER USER postgres WITH PASSWORD '1234';
CREATE TABLE todos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);


select * from todos;

INSERT INTO todos (id, title, description, completed, created_at, updated_at)
VALUES
(1, 'Task 1', 'Todo app', FALSE, '2025-03-06 00:00:00', '2025-03-06 00:00:00');
