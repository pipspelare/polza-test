CREATE TABLE IF NOT EXISTS companies (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    city TEXT NOT NULL,
    address TEXT,
    rating NUMERIC(3, 1),
    reviews_count INTEGER NOT NULL DEFAULT 0,
    site TEXT,
    phone TEXT,

    CONSTRAINT companies_rating_check
        CHECK (rating IS NULL OR rating >= 0 AND rating <= 5),

    CONSTRAINT companies_reviews_count_check
        CHECK (reviews_count >= 0)
);

CREATE INDEX IF NOT EXISTS idx_companies_category
    ON companies (category);

CREATE INDEX IF NOT EXISTS idx_companies_city
    ON companies (city);

CREATE INDEX IF NOT EXISTS idx_companies_reviews_count
    ON companies (reviews_count);

CREATE INDEX IF NOT EXISTS idx_companies_category_site
    ON companies (category)
    WHERE site IS NOT NULL AND btrim(site) <> '';

CREATE INDEX IF NOT EXISTS idx_companies_city_rating
    ON companies (city, rating)
    WHERE reviews_count >= 10;

CREATE TABLE IF NOT EXISTS review_companies (
    source_row BIGSERIAL PRIMARY KEY,
    id TEXT,
    name TEXT,
    category TEXT,
    city TEXT,
    address TEXT,
    rating_raw TEXT,
    reviews_count_raw TEXT,
    site_raw TEXT,
    phone TEXT,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_review_companies_id
    ON review_companies (id);

CREATE INDEX IF NOT EXISTS idx_review_companies_city
    ON review_companies (city);
