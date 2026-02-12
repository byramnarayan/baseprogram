import sqlite3
from neo4j import GraphDatabase, TrustAll
import os
from dotenv import load_dotenv

load_dotenv()

class PureSchemaMigrator:
    """
    Migrates SQLite data to Neo4j using ONLY exact database columns.
    No calculated fields, no aggregations - pure 1:1 mapping.
    Perfect for LLM chat integration.
    """
    
    def __init__(self, sqlite_db_path, neo4j_uri, neo4j_user, neo4j_password):
        self.sqlite_conn = sqlite3.connect(sqlite_db_path)
        self.sqlite_conn.row_factory = sqlite3.Row
        
        # Convert neo4j+s:// to neo4j:// to allow trusted_certificates config
        # This is needed for Python 3.14 SSL certificate verification
        print(f"  Original URI: {neo4j_uri}")
        if neo4j_uri.startswith("neo4j+s://"):
            neo4j_uri = neo4j_uri.replace("neo4j+s://", "neo4j://")
        elif neo4j_uri.startswith("bolt+s://"):
            neo4j_uri = neo4j_uri.replace("bolt+s://", "bolt://")
        print(f"  Modified URI: {neo4j_uri}")
        
        # Connect to Neo4j Aura with explicit trust configuration
        self.neo4j_driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password),
            max_connection_lifetime=3600,
            encrypted=True,
            trusted_certificates=TrustAll()
        )
        
        print("✓ Connected to SQLite and Neo4j")
    
    def clear_neo4j_database(self):
        """WARNING: Deletes all existing Neo4j data"""
        with self.neo4j_driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("✓ Neo4j database cleared")
    
    def create_constraints(self):
        """Create uniqueness constraints for data integrity"""
        with self.neo4j_driver.session() as session:
            constraints = [
                "CREATE CONSTRAINT farm_id_unique IF NOT EXISTS FOR (f:Farm) REQUIRE f.id IS UNIQUE",
                "CREATE CONSTRAINT state_name_unique IF NOT EXISTS FOR (s:State) REQUIRE s.name IS UNIQUE",
                "CREATE CONSTRAINT district_composite IF NOT EXISTS FOR (d:District) REQUIRE (d.name, d.state) IS UNIQUE"
            ]
            
            for constraint in constraints:
                try:
                    session.run(constraint)
                except:
                    pass  # Constraint already exists
            
            print("✓ Constraints created")
    
    def migrate_pure_data(self):
        """
        Migrate ONLY exact database columns.
        Hierarchy: State → District → Farm (with joined user data)
        """
        cursor = self.sqlite_conn.cursor()
        
        # Get all farm data with user information joined
        cursor.execute("""
            SELECT 
                f.id,
                f.farmer_id,
                f.farm_name,
                f.phone,
                f.latitude,
                f.longitude,
                f.area_hectares,
                f.soil_type,
                f.crop_type,
                f.district,
                f.state,
                f.annual_credits,
                f.annual_value_inr,
                f.polygon_coordinates,
                f.is_verified,
                f.created_at,
                f.updated_at,
                u.name as farmer_name,
                u.username as farmer_username,
                u.email as farmer_email,
                u.phone as farmer_phone_user,
                u.address as farmer_address,
                u.photo as farmer_photo,
                u.points as farmer_points
            FROM farms f
            LEFT JOIN users u ON f.farmer_id = u.id
        """)
        
        farms = cursor.fetchall()
        
        # Collect unique states and districts from actual data
        states = set()
        districts = set()
        
        for farm in farms:
            if farm['state']:
                states.add(farm['state'])
            if farm['district'] and farm['state']:
                districts.add((farm['district'], farm['state']))
        
        with self.neo4j_driver.session() as session:
            
            # STEP 1: Create State nodes with ONLY name
            print("\n[1/3] Creating State nodes...")
            for state_name in states:
                session.run("""
                    MERGE (s:State {name: $name})
                """, name=state_name)
            
            print(f"      ✓ Created {len(states)} State node(s)")
            
            # STEP 2: Create District nodes with ONLY name and state
            print("\n[2/3] Creating District nodes...")
            for district_name, state_name in districts:
                session.run("""
                    MERGE (d:District {name: $district_name, state: $state_name})
                    
                    WITH d
                    MATCH (s:State {name: $state_name})
                    MERGE (s)-[:HAS_DISTRICT]->(d)
                """,
                    district_name=district_name,
                    state_name=state_name
                )
            
            print(f"      ✓ Created {len(districts)} District node(s)")
            
            # STEP 3: Create Farm nodes with ALL database columns
            print("\n[3/3] Creating Farm nodes with complete data...")
            
            for farm in farms:
                session.run("""
                    MERGE (f:Farm {id: $id})
                    SET 
                        f.farmer_id = $farmer_id,
                        f.farm_name = $farm_name,
                        f.phone = $phone,
                        f.latitude = $latitude,
                        f.longitude = $longitude,
                        f.area_hectares = $area_hectares,
                        f.soil_type = $soil_type,
                        f.crop_type = $crop_type,
                        f.district = $district,
                        f.state = $state,
                        f.annual_credits = $annual_credits,
                        f.annual_value_inr = $annual_value_inr,
                        f.polygon_coordinates = $polygon_coordinates,
                        f.is_verified = $is_verified,
                        f.created_at = $created_at,
                        f.updated_at = $updated_at,
                        f.farmer_name = $farmer_name,
                        f.farmer_username = $farmer_username,
                        f.farmer_email = $farmer_email,
                        f.farmer_phone_user = $farmer_phone_user,
                        f.farmer_address = $farmer_address,
                        f.farmer_photo = $farmer_photo,
                        f.farmer_points = $farmer_points
                    
                    WITH f
                    MATCH (d:District {name: $district, state: $state})
                    MERGE (d)-[:HAS_FARM]->(f)
                """,
                    # farms table data
                    id=farm['id'],
                    farmer_id=farm['farmer_id'],
                    farm_name=farm['farm_name'] or '',
                    phone=farm['phone'] or '',
                    latitude=float(farm['latitude']) if farm['latitude'] else None,
                    longitude=float(farm['longitude']) if farm['longitude'] else None,
                    area_hectares=float(farm['area_hectares']) if farm['area_hectares'] else None,
                    soil_type=farm['soil_type'] or '',
                    crop_type=farm['crop_type'] or '',
                    district=farm['district'] or 'Unknown',
                    state=farm['state'] or 'Unknown',
                    annual_credits=float(farm['annual_credits']) if farm['annual_credits'] else None,
                    annual_value_inr=float(farm['annual_value_inr']) if farm['annual_value_inr'] else None,
                    polygon_coordinates=farm['polygon_coordinates'] or '',
                    is_verified=bool(farm['is_verified']) if farm['is_verified'] is not None else False,
                    created_at=farm['created_at'] or '',
                    updated_at=farm['updated_at'] or '',
                    
                    # users table data
                    farmer_name=farm['farmer_name'] or '',
                    farmer_username=farm['farmer_username'] or '',
                    farmer_email=farm['farmer_email'] or '',
                    farmer_phone_user=farm['farmer_phone_user'] or '',
                    farmer_address=farm['farmer_address'] or '',
                    farmer_photo=farm['farmer_photo'] or '',
                    farmer_points=farm['farmer_points'] or 0
                )
            
            print(f"      ✓ Created {len(farms)} Farm node(s)")
    
    def verify_migration(self):
        """Display migration results and sample data"""
        
        # Get SQLite counts
        sqlite_cursor = self.sqlite_conn.cursor()
        sqlite_farm_count = sqlite_cursor.execute("SELECT COUNT(*) FROM farms").fetchone()[0]
        
        # Get Neo4j counts
        with self.neo4j_driver.session() as session:
            state_count = session.run("MATCH (s:State) RETURN count(s) as count").single()['count']
            district_count = session.run("MATCH (d:District) RETURN count(d) as count").single()['count']
            farm_count = session.run("MATCH (f:Farm) RETURN count(f) as count").single()['count']
            
            print("\n" + "="*70)
            print(" MIGRATION VERIFICATION - PURE DATABASE SCHEMA")
            print("="*70)
            print(f"\n  SQLite farms:  {sqlite_farm_count}")
            print(f"  Neo4j farms:   {farm_count}  {'✓' if sqlite_farm_count == farm_count else '✗ MISMATCH!'}")
            print(f"\n  States:        {state_count}")
            print(f"  Districts:     {district_count}")
            print(f"  Total nodes:   {state_count + district_count + farm_count}")
            
            # Check relationships
            state_district_rels = session.run("MATCH (:State)-[r:HAS_DISTRICT]->() RETURN count(r) as count").single()['count']
            district_farm_rels = session.run("MATCH (:District)-[r:HAS_FARM]->() RETURN count(r) as count").single()['count']
            
            print(f"\n  State → District relationships:   {state_district_rels}")
            print(f"  District → Farm relationships:    {district_farm_rels}")
            
            print("\n" + "="*70)
            print(" SAMPLE HIERARCHY (First 5 farms)")
            print("="*70)
            
            # Display sample data
            result = session.run("""
                MATCH (s:State)-[:HAS_DISTRICT]->(d:District)-[:HAS_FARM]->(f:Farm)
                RETURN 
                    s.name as State, 
                    d.name as District, 
                    f.id as FarmID,
                    f.farmer_name as FarmerName,
                    f.phone as Phone,
                    f.area_hectares as Area,
                    f.annual_credits as Credits
                ORDER BY f.id
                LIMIT 5
            """)
            
            for i, record in enumerate(result, 1):
                print(f"\n  {i}. {record['State']} → {record['District']}")
                print(f"     Farm ID: {record['FarmID']}")
                print(f"     Farmer:  {record['FarmerName']} ({record['Phone']})")
                print(f"     Area:    {record['Area']} ha")
                print(f"     Credits: {record['Credits']}")
            
            print("\n" + "="*70)
    
    def close(self):
        """Close all database connections"""
        self.sqlite_conn.close()
        self.neo4j_driver.close()
        print("\n✓ Migration complete! Connections closed.")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    
    print("\n" + "="*70)
    print(" PURE DATABASE SCHEMA MIGRATION TO NEO4J")
    print("="*70)
    
    # Configuration - Use raw string (r"") for Windows paths
    SQLITE_DB_PATH = r"C:\Users\Dell\Downloads\RamnarayanProjects\project\baseprogram\app.db"
    NEO4J_URI = os.getenv("NEO4J_URI")
    NEO4J_USER = os.getenv("NEO4J_USERNAME", "neo4j")  # Changed to match .env
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
    
    print(f"\n  SQLite Database: {SQLITE_DB_PATH}")
    print(f"  Neo4j URI:       {NEO4J_URI}")
    print(f"  Neo4j User:      {NEO4J_USER}")
    
    # Validate environment variables
    if not NEO4J_URI or not NEO4J_PASSWORD:
        print("\n❌ Error: Missing Neo4j credentials!")
        print("   Please set NEO4J_URI and NEO4J_PASSWORD in your .env file")
        exit(1)
    
    # Create migrator instance
    try:
        migrator = PureSchemaMigrator(
            SQLITE_DB_PATH,
            NEO4J_URI,
            NEO4J_USER,
            NEO4J_PASSWORD
        )
        
        # Execute migration
        print("\n" + "-"*70)
        print(" STARTING MIGRATION...")
        print("-"*70)
        
        # Uncomment the next line to clear existing Neo4j data before migration
        # migrator.clear_neo4j_database()
        
        migrator.create_constraints()
        migrator.migrate_pure_data()
        migrator.verify_migration()
        
    except FileNotFoundError:
        print(f"\n❌ Error: SQLite database file '{SQLITE_DB_PATH}' not found!")
        print("   Please update SQLITE_DB_PATH in the script.")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        try:
            migrator.close()
        except:
            pass
    
    print("\n" + "="*70 + "\n")