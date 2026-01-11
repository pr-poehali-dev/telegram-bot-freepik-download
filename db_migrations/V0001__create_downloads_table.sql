CREATE TABLE IF NOT EXISTS downloads (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    freepik_url TEXT NOT NULL,
    file_title TEXT,
    file_format VARCHAR(10) NOT NULL,
    file_path TEXT,
    thumbnail_url TEXT,
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending'
);

CREATE INDEX idx_downloads_user_id ON downloads(user_id);
CREATE INDEX idx_downloads_status ON downloads(status);