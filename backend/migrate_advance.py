import asyncio
import os
import sys
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Add the parent directory to sys.path so we can import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.models.task import Task
from app.models.graph import Base as GraphBase
from app.database import Base

async def migrate():
    print(f"Connecting to database at {settings.DATABASE_URL}...")
    engine = create_async_engine(settings.DATABASE_URL)
    
    async with engine.begin() as conn:
        print("Checking for missing columns in 'tasks' table...")
        
        # 1. Add missing columns to tasks table
        new_columns = [
            ("consequences", "TEXT"),
            ("risk_level", "INTEGER DEFAULT 0"),
            ("confidence_score", "FLOAT DEFAULT 1.0"),
            ("is_approved", "BOOLEAN DEFAULT TRUE"),
            ("dependency_id", "UUID REFERENCES tasks(id) ON DELETE SET NULL"),
            ("goal_id", "UUID") # We'll add FK after goals table is created
        ]
        
        for col_name, col_type in new_columns:
            try:
                await conn.execute(text(f"ALTER TABLE tasks ADD COLUMN {col_name} {col_type}"))
                print(f"  - Added column '{col_name}'")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"  - Column '{col_name}' already exists, skipping.")
                else:
                    print(f"  - Error adding '{col_name}': {e}")

        print("Creating new tables (goals, institutions, relationships, action_suggestions)...")
        # 2. Create new tables
        # We use run_sync to use the metadata creation
        def create_tables(sync_conn):
            # This will create tables that don't exist
            from app.models.graph import Goal, Institution, Relationship, ActionSuggestion
            GraphBase.metadata.create_all(sync_conn)
            
        await conn.run_sync(create_tables)
        print("  - New tables created successfully.")

        # 3. Add the goal_id Foreign Key now that the table exists
        try:
            await conn.execute(text("ALTER TABLE tasks ADD CONSTRAINT fk_tasks_goal FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE SET NULL"))
            print("  - Added foreign key constraint for 'goal_id'")
        except Exception as e:
            if "already exists" in str(e):
                print("  - FK constraint for 'goal_id' already exists, skipping.")
            else:
                print(f"  - Note: Could not add goal_id FK (might already exist): {e}")

    print("\nMigration complete! Your database is now ready for AI-LOS Advanced features.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate())
