-- ByteC DSP — Initial Schema

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Advertisers
CREATE TABLE IF NOT EXISTS advertisers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Campaigns
CREATE TABLE IF NOT EXISTS campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    advertiser_id UUID REFERENCES advertisers(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'PAUSED' CHECK (status IN ('ACTIVE', 'PAUSED', 'ENDED')),
    goal_type VARCHAR(20) DEFAULT 'CPI' CHECK (goal_type IN ('CPI', 'CPA', 'ROAS', 'CPM')),
    goal_value NUMERIC(12, 4) NOT NULL,  -- e.g. target CPI in USD
    daily_budget NUMERIC(12, 4) NOT NULL,
    lifetime_budget NUMERIC(12, 4),
    start_date DATE NOT NULL,
    end_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Targeting: per-campaign geo/device rules
CREATE TABLE IF NOT EXISTS campaign_targeting (
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    geo_countries TEXT[],           -- ISO 3166-1 alpha-2, null = all
    device_types TEXT[],            -- ['phone','tablet','desktop'], null = all
    app_categories TEXT[],          -- IAB categories, null = all
    PRIMARY KEY (campaign_id)
);

-- Ad Groups
CREATE TABLE IF NOT EXISTS ad_groups (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    bid_multiplier NUMERIC(6, 4) DEFAULT 1.0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Creatives
CREATE TABLE IF NOT EXISTS creatives (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ad_group_id UUID REFERENCES ad_groups(id) ON DELETE CASCADE,
    format VARCHAR(20) CHECK (format IN ('banner', 'video', 'native')),
    width INT,
    height INT,
    asset_url TEXT NOT NULL,
    click_url TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'PAUSED')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Bid Logs (append-only, high volume — would migrate to ClickHouse in production)
CREATE TABLE IF NOT EXISTS bid_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID,
    creative_id UUID,
    bid_request_id VARCHAR(64) NOT NULL,
    bid_price NUMERIC(10, 6),
    predicted_ctr NUMERIC(8, 6),
    predicted_cvr NUMERIC(8, 6),
    won BOOLEAN DEFAULT FALSE,
    clear_price NUMERIC(10, 6),
    ts TIMESTAMPTZ DEFAULT NOW()
);

-- Impressions
CREATE TABLE IF NOT EXISTS impressions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bid_log_id UUID REFERENCES bid_logs(id),
    campaign_id UUID,
    creative_id UUID,
    ts TIMESTAMPTZ DEFAULT NOW()
);

-- Clicks
CREATE TABLE IF NOT EXISTS clicks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    impression_id UUID REFERENCES impressions(id),
    campaign_id UUID,
    ts TIMESTAMPTZ DEFAULT NOW()
);

-- Conversions (installs / purchases)
CREATE TABLE IF NOT EXISTS conversions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    click_id UUID REFERENCES clicks(id),
    campaign_id UUID,
    conversion_type VARCHAR(50) DEFAULT 'install',
    revenue NUMERIC(12, 4) DEFAULT 0,
    ts TIMESTAMPTZ DEFAULT NOW()
);

-- Budget spend tracking (daily buckets)
CREATE TABLE IF NOT EXISTS budget_spend (
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    spend_date DATE NOT NULL,
    spent NUMERIC(12, 4) DEFAULT 0,
    PRIMARY KEY (campaign_id, spend_date)
);

-- Indexes for hot query paths
CREATE INDEX IF NOT EXISTS idx_bid_logs_campaign ON bid_logs(campaign_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_impressions_campaign ON impressions(campaign_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_clicks_campaign ON clicks(campaign_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_conversions_campaign ON conversions(campaign_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_campaigns_advertiser ON campaigns(advertiser_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
