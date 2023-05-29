CREATE TABLE IF NOT EXISTS starlink_positions (
    id VARCHAR(255),
    creation_date TIMESTAMP,
    longitude FLOAT,
    latitude FLOAT,
    PRIMARY KEY (id, creation_date)
);
