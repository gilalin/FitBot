-- ===========================
-- Users
-- ===========================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    telegram_id TEXT UNIQUE,
    auth_provider TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ===========================
-- Membership Plans
-- ===========================
CREATE TABLE membership_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    price_cents INTEGER NOT NULL,
    duration_days INTEGER NOT NULL,
    description TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ===========================
-- Memberships
-- ===========================
CREATE TABLE memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES membership_plans(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    payment_status TEXT DEFAULT 'pending',
    stripe_subscription_id TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ===========================
-- Workouts
-- ===========================
CREATE TABLE workouts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    difficulty_level TEXT,
    category TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    calendar_event_id TEXT
);

-- ===========================
-- Classes
-- ===========================
CREATE TABLE classes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workout_id UUID REFERENCES workouts(id),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    capacity INTEGER DEFAULT 10,
    coach_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ===========================
-- Class Registrations
-- ===========================
CREATE TABLE class_registrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    class_id UUID REFERENCES classes(id) ON DELETE CASCADE,
    status TEXT DEFAULT 'registered',
    created_at TIMESTAMP DEFAULT NOW()
);

-- ===========================
-- Workout Results
-- ===========================
CREATE TABLE workout_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    workout_id UUID REFERENCES workouts(id),
    class_id UUID REFERENCES classes(id),
    result_text TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ===========================
-- Products
-- ===========================
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    price_cents INTEGER NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    category TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ===========================
-- Orders
-- ===========================
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    total_cents INTEGER NOT NULL,
    status TEXT DEFAULT 'pending',
    stripe_payment_id TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ===========================
-- Order Items
-- ===========================
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id),
    quantity INTEGER NOT NULL,
    price_cents INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ===========================
-- Performance Metrics
-- ===========================
CREATE TABLE performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    metric_type TEXT NOT NULL,
    value NUMERIC NOT NULL,
    workout_id UUID REFERENCES workouts(id),
    workout_result_id UUID REFERENCES workout_results(id),
    recorded_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ===========================
-- AI Insights
-- ===========================
CREATE TABLE ai_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    insight_type TEXT NOT NULL,
    content TEXT NOT NULL,
    reference_period_start DATE,
    reference_period_end DATE,
    created_at TIMESTAMP DEFAULT NOW()
); 