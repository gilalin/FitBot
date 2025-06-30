from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Numeric, Text, Table, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database import Base

# Association table for many-to-many relationship between users and classes
user_class = Table(
    'user_class',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('class_id', Integer, ForeignKey('classes.id'))
)

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    telegram_id = Column(String, unique=True)
    auth_provider = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    memberships = relationship("Membership", back_populates="user")
    workout_results = relationship("WorkoutResult", back_populates="user")
    class_registrations = relationship("ClassRegistration", back_populates="user")
    orders = relationship("Order", back_populates="user")
    performance_metrics = relationship("PerformanceMetric", back_populates="user")
    ai_insights = relationship("AIInsight", back_populates="user")
    classes = relationship("Class", secondary=user_class, back_populates="participants")
    performance_records = relationship("PerformanceRecord", back_populates="user")
    purchases = relationship("Purchase", back_populates="user")

class MembershipPlan(Base):
    __tablename__ = "membership_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    price_cents = Column(Integer, nullable=False)
    duration_days = Column(Integer, nullable=False)
    description = Column(Text)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    memberships = relationship("Membership", back_populates="plan")

class Membership(Base):
    __tablename__ = "memberships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    plan_id = Column(UUID(as_uuid=True), ForeignKey('membership_plans.id'))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    active = Column(Boolean, default=True)
    payment_status = Column(String, default='pending')
    stripe_subscription_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="memberships")
    plan = relationship("MembershipPlan", back_populates="memberships")

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(Date, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    difficulty_level = Column(String)
    category = Column(String)
    calendar_event_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    classes = relationship("Class", back_populates="workout")
    workout_results = relationship("WorkoutResult", back_populates="workout")
    performance_metrics = relationship("PerformanceMetric", back_populates="workout")
    class_session = relationship("Class", back_populates="workout")
    performance_records = relationship("PerformanceRecord", back_populates="workout")

class Class(Base):
    __tablename__ = "classes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workout_id = Column(UUID(as_uuid=True), ForeignKey('workouts.id'))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    capacity = Column(Integer, default=10)
    coach_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    workout = relationship("Workout", back_populates="class_session")
    registrations = relationship("ClassRegistration", back_populates="class_")
    workout_results = relationship("WorkoutResult", back_populates="class_")
    coach = relationship("User")
    participants = relationship("User", secondary=user_class, back_populates="classes")

class ClassRegistration(Base):
    __tablename__ = "class_registrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    class_id = Column(UUID(as_uuid=True), ForeignKey('classes.id', ondelete='CASCADE'))
    status = Column(String, default='registered')
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="class_registrations")
    class_ = relationship("Class", back_populates="registrations")

class WorkoutResult(Base):
    __tablename__ = "workout_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    workout_id = Column(UUID(as_uuid=True), ForeignKey('workouts.id'))
    class_id = Column(UUID(as_uuid=True), ForeignKey('classes.id'))
    result_text = Column(Text, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="workout_results")
    workout = relationship("Workout", back_populates="workout_results")
    class_ = relationship("Class", back_populates="workout_results")
    performance_metrics = relationship("PerformanceMetric", back_populates="workout_result")

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    price_cents = Column(Integer, nullable=False)
    stock_quantity = Column(Integer, default=0)
    category = Column(String)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    order_items = relationship("OrderItem", back_populates="product")
    purchases = relationship("Purchase", back_populates="product")

class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))
    total_cents = Column(Integer, nullable=False)
    status = Column(String, default='pending')
    stripe_payment_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id', ondelete='CASCADE'))
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)
    price_cents = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    metric_type = Column(String, nullable=False)
    value = Column(Numeric, nullable=False)
    workout_id = Column(UUID(as_uuid=True), ForeignKey('workouts.id'))
    workout_result_id = Column(UUID(as_uuid=True), ForeignKey('workout_results.id'))
    recorded_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="performance_metrics")
    workout = relationship("Workout", back_populates="performance_metrics")
    workout_result = relationship("WorkoutResult", back_populates="performance_metrics")

class AIInsight(Base):
    __tablename__ = "ai_insights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    insight_type = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    reference_period_start = Column(Date)
    reference_period_end = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="ai_insights")

class PerformanceRecord(Base):
    __tablename__ = "performance_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    workout_id = Column(UUID(as_uuid=True), ForeignKey('workouts.id'))
    score = Column(String, nullable=False)
    notes = Column(Text)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="performance_records")
    workout = relationship("Workout", back_populates="performance_records")

class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    purchase_date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="purchases")
    product = relationship("Product", back_populates="purchases") 