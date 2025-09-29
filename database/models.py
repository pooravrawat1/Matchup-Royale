from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, SmallInteger, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config.settings import config

Base = declarative_base()

class Battle(Base):
    __tablename__ = 'battles'
    
    # Primary key and unique identifier
    id = Column(Integer, primary_key=True)
    battle_id = Column(String(150), unique=True, nullable=False)
    
    # Battle metadata
    battle_time = Column(DateTime, nullable=False)
    game_mode = Column(String(50), nullable=False)
    battle_type = Column(String(50))
    
    # Player 1 (team member who we collected from)
    p1_tag = Column(String(20), nullable=False)
    p1_name = Column(String(100))
    p1_trophies = Column(SmallInteger)
    p1_deck = Column(Text)  # JSON string of card names
    p1_crowns = Column(SmallInteger)
    
    # Player 2 (opponent)
    p2_tag = Column(String(20), nullable=False)
    p2_name = Column(String(100))
    p2_trophies = Column(SmallInteger)
    p2_deck = Column(Text)  # JSON string of card names
    p2_crowns = Column(SmallInteger)
    
    # Battle outcome
    winner = Column(SmallInteger)  # 1 for p1, 2 for p2
    
    # Metadata
    collected_at = Column(DateTime, default=datetime.utcnow)
    
    # Define indexes for better query performance
    __table_args__ = (
        Index('idx_battle_time', 'battle_time'),
        Index('idx_players', 'p1_tag', 'p2_tag'),
        Index('idx_game_mode', 'game_mode'),
        Index('idx_trophies', 'p1_trophies', 'p2_trophies'),
    )

class Player(Base):
    __tablename__ = 'players'
    
    # Primary key
    id = Column(Integer, primary_key=True)
    player_tag = Column(String(20), unique=True, nullable=False)
    
    # Player information
    name = Column(String(100))
    trophies = Column(Integer)
    best_trophies = Column(Integer)
    wins = Column(Integer)
    losses = Column(Integer)
    
    # Collection metadata
    last_seen = Column(DateTime)
    battles_collected = Column(Integer, default=0)
    is_processed = Column(Boolean, default=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    last_processed = Column(DateTime)
    
    # Index for efficient lookups
    __table_args__ = (
        Index('idx_player_tag', 'player_tag'),
        Index('idx_trophies', 'trophies'),
        Index('idx_processed', 'is_processed'),
    )

class CollectionStats(Base):
    __tablename__ = 'collection_stats'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow)
    battles_collected = Column(Integer)
    players_processed = Column(Integer)
    api_calls_made = Column(Integer)
    errors_encountered = Column(Integer)
    collection_time_minutes = Column(Integer)

# Database connection and session management
def get_database_engine():
    """Create database engine"""
    if not config.DATABASE_URL:
        raise ValueError("DATABASE_URL not configured")
    
    engine = create_engine(
        config.DATABASE_URL,
        echo=False,  # Set to True for SQL debugging
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True  # Verify connections before use
    )
    return engine

def create_tables():
    """Create all database tables"""
    try:
        engine = get_database_engine()
        Base.metadata.create_all(engine)
        print("✅ Database tables created successfully")
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ Database connection test successful")
        
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def get_session():
    """Create database session"""
    engine = get_database_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def get_database_stats():
    """Get current database statistics"""
    session = get_session()
    try:
        battle_count = session.query(Battle).count()
        player_count = session.query(Player).count()
        
        # Get date range of battles
        if battle_count > 0:
            earliest_battle = session.query(Battle.battle_time).order_by(Battle.battle_time.asc()).first()[0]
            latest_battle = session.query(Battle.battle_time).order_by(Battle.battle_time.desc()).first()[0]
        else:
            earliest_battle = None
            latest_battle = None
        
        return {
            'battles': battle_count,
            'players': player_count,
            'earliest_battle': earliest_battle,
            'latest_battle': latest_battle
        }
    finally:
        session.close()