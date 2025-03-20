-- Create a basic user table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    sex CHAR(1),
    country VARCHAR(50),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    profile_picture VARCHAR(255)
);

-- Insert 2000 random users
INSERT INTO users (first_name, last_name, email, password_hash, date_of_birth, sex, country, registration_date, is_active, last_login, profile_picture)
SELECT
    'FirstName' || i AS first_name,
    'LastName' || i AS last_name,
    'user' || i || '@example.com' AS email,
    md5(random()::text) AS password_hash,
    (CURRENT_DATE - (RANDOM() * 10000)::INTEGER * INTERVAL '1 day')::DATE AS date_of_birth,
    CASE WHEN RANDOM() > 0.5 THEN 'M' ELSE 'F' END AS sex,
    (ARRAY['USA', 'Canada', 'France', 'Germany', 'UK', 'Spain', 'Italy', 'Japan', 'Australia', 'Brazil'])[1 + (RANDOM() * 10)::INTEGER] AS country,
    (CURRENT_TIMESTAMP - (RANDOM() * 365 * 2)::INTEGER * INTERVAL '1 day') AS registration_date,
    CASE WHEN RANDOM() > 0.1 THEN TRUE ELSE FALSE END AS is_active,
    (CURRENT_TIMESTAMP - (RANDOM() * 30)::INTEGER * INTERVAL '1 day') AS last_login,
    CASE WHEN RANDOM() > 0.7 THEN '/profiles/avatar' || i || '.jpg' ELSE NULL END AS profile_picture
FROM generate_series(1, 2000) AS i;
