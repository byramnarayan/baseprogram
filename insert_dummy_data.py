"""
Dummy Data Generator for Farm Management System
Inserts 100 farmers with their farms into SQLite database using SQLAlchemy ORM
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import random

# Create Base class
Base = declarative_base()


# ============================================================================
# ORM MODELS (matching your existing database schema)
# ============================================================================

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    username = Column(String(50), unique=True)
    email = Column(String(100), unique=True)
    phone = Column(String(15))
    address = Column(String(200))
    photo = Column(String(200))
    password_hash = Column(String(200))  # Added to match existing schema
    points = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to farms
    farms = relationship("Farm", back_populates="farmer")


class Farm(Base):
    __tablename__ = 'farms'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    farmer_id = Column(Integer, ForeignKey('users.id'))
    farm_name = Column(String(100))
    phone = Column(String(15))
    latitude = Column(Float)
    longitude = Column(Float)
    area_hectares = Column(Float)
    soil_type = Column(String(50))
    crop_type = Column(String(50))
    district = Column(String(100))
    state = Column(String(100))
    annual_credits = Column(Float)
    annual_value_inr = Column(Float)
    polygon_coordinates = Column(String)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to user
    farmer = relationship("User", back_populates="farms")


# ============================================================================
# DUMMY DATA GENERATORS
# ============================================================================

# Indian names pool
FIRST_NAMES = [
    "Rajesh", "Amit", "Suresh", "Prakash", "Ramesh", "Vijay", "Anil", "Rahul", "Sanjay", "Manoj",
    "Deepak", "Ashok", "Ravi", "Santosh", "Dinesh", "Mukesh", "Vishal", "Nitin", "Ajay", "Kiran",
    "Priya", "Sunita", "Geeta", "Kavita", "Rekha", "Anita", "Meena", "Seema", "Neeta", "Rita",
    "Krishna", "Govind", "Mohan", "Ganesh", "Shyam", "Hari", "Gopal", "Balram", "Shankar", "Shiva",
    "Lakshmi", "Saraswati", "Durga", "Parvati", "Radha", "Sita", "Savitri", "Rukmini", "Draupadi", "Kunti"
]

LAST_NAMES = [
    "Kumar", "Singh", "Sharma", "Patel", "Reddy", "Rao", "Nair", "Iyer", "Gupta", "Joshi",
    "Desai", "Shah", "Mehta", "Agarwal", "Chopra", "Kapoor", "Malhotra", "Khanna", "Bhatia", "Sethi",
    "Verma", "Pandey", "Mishra", "Tiwari", "Dubey", "Jha", "Thakur", "Chauhan", "Rathore", "Yadav"
]

# Indian states and districts
LOCATIONS = [
    {"state": "Maharashtra", "districts": ["Pune", "Mumbai", "Nagpur", "Nashik", "Aurangabad", "Solapur"]},
    {"state": "Gujarat", "districts": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Junagadh"]},
    {"state": "Karnataka", "districts": ["Bangalore", "Mysore", "Hubli", "Mangalore", "Belgaum", "Gulbarga"]},
    {"state": "Tamil Nadu", "districts": ["Chennai", "Coimbatore", "Madurai", "Salem", "Tiruchirappalli", "Tirunelveli"]},
    {"state": "Andhra Pradesh", "districts": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool", "Tirupati"]},
    {"state": "Uttar Pradesh", "districts": ["Lucknow", "Kanpur", "Agra", "Varanasi", "Meerut", "Allahabad"]},
    {"state": "Punjab", "districts": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda", "Mohali"]},
    {"state": "Rajasthan", "districts": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer", "Bikaner"]},
    {"state": "Madhya Pradesh", "districts": ["Indore", "Bhopal", "Jabalpur", "Gwalior", "Ujjain", "Sagar"]},
    {"state": "West Bengal", "districts": ["Kolkata", "Howrah", "Durgapur", "Siliguri", "Asansol", "Malda"]}
]

SOIL_TYPES = ["Loamy", "Clay", "Sandy", "Silty", "Peaty", "Chalky", "Red Soil", "Black Soil", "Alluvial", "Laterite"]
CROP_TYPES = ["Rice", "Wheat", "Cotton", "Sugarcane", "Maize", "Pulses", "Groundnut", "Soybean", "Tea", "Coffee", 
              "Vegetables", "Fruits", "Spices", "Millets", "Barley"]


def generate_phone():
    """Generate Indian phone number"""
    return f"{random.choice([7, 8, 9])}{random.randint(100000000, 999999999)}"


def generate_email(name):
    """Generate email from name"""
    username = name.lower().replace(" ", "")
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]
    return f"{username}{random.randint(1, 999)}@{random.choice(domains)}"


def generate_coordinates(state_name):
    """Generate realistic coordinates based on state"""
    # Approximate center coordinates for Indian states
    state_coords = {
        "Maharashtra": (19.7515, 75.7139),
        "Gujarat": (22.2587, 71.1924),
        "Karnataka": (15.3173, 75.7139),
        "Tamil Nadu": (11.1271, 78.6569),
        "Andhra Pradesh": (15.9129, 79.7400),
        "Uttar Pradesh": (26.8467, 80.9462),
        "Punjab": (31.1471, 75.3412),
        "Rajasthan": (27.0238, 74.2179),
        "Madhya Pradesh": (22.9734, 78.6569),
        "West Bengal": (22.9868, 87.8550)
    }
    
    base_lat, base_lng = state_coords.get(state_name, (20.5937, 78.9629))
    # Add random offset (±1 degree)
    lat = base_lat + random.uniform(-1, 1)
    lng = base_lng + random.uniform(-1, 1)
    return round(lat, 6), round(lng, 6)


def generate_polygon(lat, lng):
    """Generate simple polygon coordinates around a point"""
    offset = 0.001
    polygon = f"[[[{lng-offset},{lat-offset}],[{lng+offset},{lat-offset}],[{lng+offset},{lat+offset}],[{lng-offset},{lat+offset}],[{lng-offset},{lat-offset}]]]"
    return polygon


# ============================================================================
# MAIN DATA INSERTION FUNCTION
# ============================================================================

def insert_dummy_data(db_path="app.db", num_records=100):
    """
    Insert dummy data into SQLite database
    
    Args:
        db_path: Path to SQLite database file
        num_records: Number of farmer records to create (each gets 1-3 farms)
    """
    
    # Create engine and session
    engine = create_engine(f'sqlite:///{db_path}')
    
    # Don't create tables - they already exist
    # Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print(f"\n{'='*70}")
    print(f" INSERTING {num_records} DUMMY FARMERS AND FARMS")
    print(f"{'='*70}\n")
    
    try:
        farmers_created = 0
        farms_created = 0
        
        for i in range(1, num_records + 1):
            try:
                # Generate farmer/user data
                first_name = random.choice(FIRST_NAMES)
                last_name = random.choice(LAST_NAMES)
                full_name = f"{first_name} {last_name}"
                
                user = User(
                    name=full_name,
                    username=f"{first_name.lower()}{last_name.lower()}{i}",
                    email=generate_email(full_name),
                    phone=generate_phone(),
                    address=f"{random.randint(1, 999)}, {random.choice(['MG Road', 'Main Street', 'Gandhi Nagar', 'Station Road', 'Market Area'])}",
                    photo=f"/static/photos/farmer_{i}.jpg",
                    password_hash="hashed_password_placeholder",  # Placeholder password hash
                    points=random.randint(0, 1000)
                )
                
                session.add(user)
                session.flush()  # Get the user.id
                
                farmers_created += 1
                
                # Generate 1-3 farms for each farmer
                num_farms = random.randint(1, 3)
                
                for j in range(num_farms):
                    # Select random location
                    location = random.choice(LOCATIONS)
                    state = location["state"]
                    district = random.choice(location["districts"])
                    
                    # Generate coordinates
                    lat, lng = generate_coordinates(state)
                    
                    # Calculate area and credits
                    area = round(random.uniform(0.5, 10.0), 2)
                    credits_per_hectare = 15.0  # Base carbon credits per hectare
                    annual_credits = round(area * credits_per_hectare, 2)
                    annual_value = round(annual_credits * 1500, 2)  # ₹1500 per credit
                    
                    farm = Farm(
                        farmer_id=user.id,
                        farm_name=f"{full_name}'s Farm {j+1}" if num_farms > 1 else f"{full_name}'s Farm",
                        phone=generate_phone(),
                        latitude=lat,
                        longitude=lng,
                        area_hectares=area,
                        soil_type=random.choice(SOIL_TYPES),
                        crop_type=random.choice(CROP_TYPES),
                        district=district,
                        state=state,
                        annual_credits=annual_credits,
                        annual_value_inr=annual_value,
                        polygon_coordinates=generate_polygon(lat, lng),
                        is_verified=random.choice([True, False])
                    )
                    
                    session.add(farm)
                    farms_created += 1
                
                # Print progress every 10 farmers
                if i % 10 == 0:
                    print(f"  Progress: {i}/{num_records} farmers created...")
                    
            except Exception as e:
                print(f"\n  ⚠️  Error creating farmer {i}: {e}")
                session.rollback()
                continue
        
        # Commit all changes
        session.commit()
        
        print(f"\n{'='*70}")
        print(f" ✓ SUCCESS!")
        print(f"{'='*70}")
        print(f"  Farmers created:  {farmers_created}")
        print(f"  Farms created:    {farms_created}")
        print(f"  Database:         {db_path}")
        print(f"{'='*70}\n")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        session.close()


# ============================================================================
# SCRIPT EXECUTION
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Default values
    DB_PATH = r"C:\Users\Dell\Downloads\RamnarayanProjects\project\baseprogram\app.db"
    NUM_RECORDS = 100
    
    # Allow command line arguments
    if len(sys.argv) > 1:
        DB_PATH = sys.argv[1]
    if len(sys.argv) > 2:
        NUM_RECORDS = int(sys.argv[2])
    
    print(f"\nDatabase Path: {DB_PATH}")
    print(f"Number of Farmers: {NUM_RECORDS}\n")
    
    # Run the insertion
    insert_dummy_data(DB_PATH, NUM_RECORDS)
    
    print("Done! You can now run the migration script to sync with Neo4j.\n")