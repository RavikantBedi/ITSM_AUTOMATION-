-- Table 1: incident_status_summary
CREATE TABLE IF NOT EXISTS incident_status_summary (
    id SERIAL PRIMARY KEY,
    month VARCHAR(50),
    closed INTEGER,
    pending INTEGER,
    resolved INTEGER,
    total INTEGER
);

-- Table 2: attack_vector_summary
CREATE TABLE IF NOT EXISTS attack_vector_summary (
    id SERIAL PRIMARY KEY,
    month VARCHAR(50),
    external_internal INTEGER,
    internal_external INTEGER,
    internal_internal INTEGER
);
