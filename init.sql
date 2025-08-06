-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    photo_url TEXT,
    age INTEGER CHECK (age >= 18 AND age <= 100),
    bio TEXT,
    price_min INTEGER CHECK (price_min >= 0),
    price_max INTEGER CHECK (price_max >= price_min),
    metro_station VARCHAR(255),
    search_location GEOGRAPHY(POINT, 4326),
    search_radius INTEGER CHECK (search_radius > 0), -- in meters
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Listings table
CREATE TABLE listings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    price INTEGER NOT NULL CHECK (price >= 0),
    address VARCHAR(500),
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    rooms INTEGER CHECK (rooms > 0),
    area DECIMAL(7,2) CHECK (area > 0),
    floor INTEGER,
    total_floors INTEGER,
    metro_station VARCHAR(255),
    metro_distance INTEGER, -- in meters
    photos TEXT[], -- array of photo URLs
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User likes table (for matching system)
CREATE TABLE user_likes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    liker_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    liked_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(liker_id, liked_id),
    CHECK (liker_id != liked_id)
);

-- User matches table (mutual likes)
CREATE TABLE user_matches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user1_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user2_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user1_id, user2_id),
    CHECK (user1_id != user2_id)
);

-- Listing likes table
CREATE TABLE listing_likes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    listing_id UUID NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, listing_id)
);

-- Create indexes for performance
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_users_location ON users USING GIST(search_location);
CREATE INDEX idx_listings_location ON listings USING GIST(location);
CREATE INDEX idx_listings_price ON listings(price);
CREATE INDEX idx_listings_active ON listings(is_active);
CREATE INDEX idx_user_likes_liker ON user_likes(liker_id);
CREATE INDEX idx_user_likes_liked ON user_likes(liked_id);
CREATE INDEX idx_listing_likes_user ON listing_likes(user_id);
CREATE INDEX idx_listing_likes_listing ON listing_likes(listing_id);

-- Function to automatically create matches when mutual likes exist
CREATE OR REPLACE FUNCTION create_match_on_mutual_like()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if there's a mutual like
    IF EXISTS (
        SELECT 1 FROM user_likes 
        WHERE liker_id = NEW.liked_id AND liked_id = NEW.liker_id
    ) THEN
        -- Create match (ensure user1_id < user2_id for consistency)
        INSERT INTO user_matches (user1_id, user2_id)
        VALUES (
            LEAST(NEW.liker_id, NEW.liked_id),
            GREATEST(NEW.liker_id, NEW.liked_id)
        )
        ON CONFLICT (user1_id, user2_id) DO NOTHING;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to create matches automatically
CREATE TRIGGER trigger_create_match
    AFTER INSERT ON user_likes
    FOR EACH ROW
    EXECUTE FUNCTION create_match_on_mutual_like();