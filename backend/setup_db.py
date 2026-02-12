#!/usr/bin/env python3
"""
Federation Database Setup and Management Script

This script provides comprehensive database management capabilities:
- Initialize database schema
- Seed with sample data (engagements, frameworks, expertise)
- Reset database (drop and recreate)
- Clear data without dropping schema
- Show database status

Usage:
    python setup_db.py init          # Create database and tables
    python setup_db.py seed          # Populate with sample data
    python setup_db.py init --seed   # Create tables and seed data
    python setup_db.py reset         # Drop all tables and recreate
    python setup_db.py reset --seed  # Reset and seed with fresh data
    python setup_db.py clear         # Delete all data (keep tables)
    python setup_db.py status        # Show database statistics
    python setup_db.py migrate       # Run any pending migrations

Environment Variables:
    DATABASE_URL - SQLAlchemy connection string (default: sqlite+aiosqlite:///./data/federation.db)
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path


# Add app to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def print_header(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_status(message: str, status: str = "info") -> None:
    """Print a status message with appropriate formatting."""
    icons = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
        "pending": "⏳",
    }
    icon = icons.get(status, "•")
    print(f"  {icon} {message}")


async def get_db_path() -> Path:
    """Get the database file path from settings."""
    from app.config import settings
    
    # Extract path from sqlite URL
    db_url = settings.database_url
    if "sqlite" in db_url:
        # Parse: sqlite+aiosqlite:///./data/federation.db
        path_part = db_url.split("///")[-1]
        return Path(path_part)
    return Path("./data/federation.db")


async def ensure_data_directory() -> None:
    """Ensure the data directory exists."""
    db_path = await get_db_path()
    data_dir = db_path.parent
    if not data_dir.exists():
        data_dir.mkdir(parents=True, exist_ok=True)
        print_status(f"Created data directory: {data_dir}", "success")


async def init_database(verbose: bool = True) -> bool:
    """Initialize the database schema (create all tables)."""
    if verbose:
        print_header("Initializing Database")
    
    try:
        await ensure_data_directory()
        
        from app.models.database import init_db, engine
        from app.config import settings
        
        if verbose:
            print_status(f"Database URL: {settings.database_url}", "info")
        
        await init_db()
        
        if verbose:
            db_path = await get_db_path()
            if db_path.exists():
                size_kb = db_path.stat().st_size / 1024
                print_status(f"Database file: {db_path} ({size_kb:.1f} KB)", "info")
            print_status("Database schema initialized successfully", "success")
        
        return True
        
    except Exception as e:
        print_status(f"Failed to initialize database: {e}", "error")
        return False


async def reset_database(verbose: bool = True) -> bool:
    """Drop all tables and recreate the schema."""
    if verbose:
        print_header("Resetting Database")
    
    try:
        await ensure_data_directory()
        
        from app.models.database import Base, engine
        
        if verbose:
            print_status("Dropping all tables...", "pending")
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        if verbose:
            print_status("All tables dropped", "success")
            print_status("Recreating schema...", "pending")
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        if verbose:
            print_status("Database schema recreated successfully", "success")
        
        return True
        
    except Exception as e:
        print_status(f"Failed to reset database: {e}", "error")
        return False


async def clear_database(verbose: bool = True) -> bool:
    """Clear all data from the database without dropping tables."""
    if verbose:
        print_header("Clearing Database Data")
    
    try:
        from app.models.database import (
            AsyncSessionLocal,
            init_db,
            Conversation,
            Message,
            AgentTrace,
            Document,
            KnowledgeItem,
            Engagement,
            Metric,
        )
        from sqlalchemy import delete, select, func
        
        await init_db()
        
        async with AsyncSessionLocal() as db:
            # Count records before deletion
            tables = [
                ("Messages", Message),
                ("Agent Traces", AgentTrace),
                ("Conversations", Conversation),
                ("Documents", Document),
                ("Knowledge Items", KnowledgeItem),
                ("Engagements", Engagement),
                ("Metrics", Metric),
            ]
            
            counts = {}
            for name, model in tables:
                result = await db.execute(select(func.count()).select_from(model))
                counts[name] = result.scalar() or 0
            
            if verbose:
                total = sum(counts.values())
                print_status(f"Found {total} total records across {len(tables)} tables", "info")
            
            # Delete in order respecting foreign keys
            delete_order = [
                AgentTrace,
                Message,
                Conversation,
                Document,
                KnowledgeItem,
                Engagement,
                Metric,
            ]
            
            for model in delete_order:
                await db.execute(delete(model))
            
            await db.commit()
            
            if verbose:
                for name, count in counts.items():
                    if count > 0:
                        print_status(f"Deleted {count} {name.lower()}", "success")
                print_status("All data cleared successfully", "success")
        
        return True
        
    except Exception as e:
        print_status(f"Failed to clear database: {e}", "error")
        return False


async def seed_database(verbose: bool = True, skip_embeddings: bool = False) -> bool:
    """Seed the database with TechVista social media data."""
    if verbose:
        print_header("Seeding Database")

    try:
        from app.models.database import AsyncSessionLocal, init_db, KnowledgeItem, Engagement
        from sqlalchemy import select, func

        await init_db()

        # Check if data already exists
        async with AsyncSessionLocal() as db:
            knowledge_count = await db.execute(select(func.count()).select_from(KnowledgeItem))
            engagement_count = await db.execute(select(func.count()).select_from(Engagement))

            existing_knowledge = knowledge_count.scalar() or 0
            existing_engagements = engagement_count.scalar() or 0

            if existing_knowledge > 0 or existing_engagements > 0:
                if verbose:
                    print_status(
                        f"Database already contains {existing_knowledge} knowledge items "
                        f"and {existing_engagements} campaigns",
                        "warning"
                    )
                    print_status("Use 'reset --seed' to clear and reseed, or 'clear' first", "info")
                return False

        # Delegate to seed module
        from app.data.seed import seed_database as run_seed
        await run_seed(skip_embeddings=skip_embeddings)

        if verbose:
            print_status("Database seeding complete!", "success")

        return True

    except Exception as e:
        print_status(f"Failed to seed database: {e}", "error")
        import traceback
        traceback.print_exc()
        return False


async def show_status(verbose: bool = True) -> dict:
    """Show database status and statistics."""
    if verbose:
        print_header("Database Status")
    
    status = {
        "initialized": False,
        "tables": {},
        "file_size_kb": 0,
        "file_path": "",
    }
    
    try:
        from app.models.database import (
            AsyncSessionLocal,
            init_db,
            Conversation,
            Message,
            AgentTrace,
            Document,
            KnowledgeItem,
            Engagement,
            Metric,
        )
        from app.config import settings
        from sqlalchemy import select, func
        
        db_path = await get_db_path()
        status["file_path"] = str(db_path)
        
        if verbose:
            print_status(f"Database URL: {settings.database_url}", "info")
        
        if db_path.exists():
            status["file_size_kb"] = db_path.stat().st_size / 1024
            status["initialized"] = True
            
            if verbose:
                print_status(
                    f"Database file: {db_path} ({status['file_size_kb']:.1f} KB)",
                    "success"
                )
        else:
            if verbose:
                print_status("Database file does not exist yet", "warning")
                print_status("Run 'python setup_db.py init' to create it", "info")
            return status
        
        await init_db()
        
        async with AsyncSessionLocal() as db:
            tables = [
                ("Conversations", Conversation),
                ("Messages", Message),
                ("Agent Traces", AgentTrace),
                ("Documents", Document),
                ("Knowledge Items", KnowledgeItem),
                ("Engagements", Engagement),
                ("Metrics", Metric),
            ]
            
            if verbose:
                print_status("Table statistics:", "info")
            
            for name, model in tables:
                result = await db.execute(select(func.count()).select_from(model))
                count = result.scalar() or 0
                status["tables"][name] = count
                
                if verbose:
                    icon = "✓" if count > 0 else "○"
                    print(f"      {icon} {name}: {count} records")
        
        if verbose:
            total = sum(status["tables"].values())
            print_status(f"Total records: {total}", "info")
            
            # Check seeding status
            if status["tables"].get("Knowledge Items", 0) == 0:
                print_status("Knowledge base is empty - run 'seed' to populate", "warning")
            else:
                print_status("Knowledge base is populated", "success")
        
        return status
        
    except Exception as e:
        print_status(f"Failed to get database status: {e}", "error")
        return status


async def run_migrations(verbose: bool = True) -> bool:
    """Run any pending database migrations."""
    if verbose:
        print_header("Running Migrations")
    
    try:
        # For SQLite with SQLAlchemy, migrations are typically handled
        # by creating tables that don't exist. For a production system,
        # you'd use Alembic for proper migrations.
        
        from app.models.database import Base, engine
        
        if verbose:
            print_status("Checking for schema updates...", "pending")
        
        async with engine.begin() as conn:
            # Create any missing tables (safe operation)
            await conn.run_sync(Base.metadata.create_all)
        
        if verbose:
            print_status("Database schema is up to date", "success")
            print_status(
                "Note: For complex migrations, consider using Alembic",
                "info"
            )
        
        return True
        
    except Exception as e:
        print_status(f"Migration failed: {e}", "error")
        return False


async def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Federation Database Setup and Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup_db.py init              # Initialize database
  python setup_db.py seed              # Seed with sample data
  python setup_db.py init --seed       # Initialize and seed
  python setup_db.py reset --seed      # Reset and seed fresh
  python setup_db.py status            # Show database info
  python setup_db.py seed --no-embeddings  # Seed without embeddings (faster)
        """
    )
    
    parser.add_argument(
        "command",
        choices=["init", "seed", "reset", "clear", "status", "migrate"],
        help="Database operation to perform"
    )
    
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Also seed the database after init/reset"
    )
    
    parser.add_argument(
        "--no-embeddings",
        action="store_true",
        help="Skip generating embeddings during seeding (faster)"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Minimal output"
    )
    
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip confirmation prompts"
    )
    
    args = parser.parse_args()
    verbose = not args.quiet
    
    # Confirmation for destructive operations
    if args.command in ["reset", "clear"] and not args.yes:
        print(f"\n⚠️  This will {'drop all tables and recreate them' if args.command == 'reset' else 'delete all data'}!")
        confirm = input("Are you sure? (y/N): ").strip().lower()
        if confirm != "y":
            print("Cancelled.")
            return 0
    
    success = False
    
    if args.command == "init":
        success = await init_database(verbose)
        if success and args.seed:
            success = await seed_database(verbose, skip_embeddings=args.no_embeddings)
    
    elif args.command == "seed":
        # Ensure database is initialized first
        await init_database(verbose=False)
        success = await seed_database(verbose, skip_embeddings=args.no_embeddings)
    
    elif args.command == "reset":
        success = await reset_database(verbose)
        if success and args.seed:
            success = await seed_database(verbose, skip_embeddings=args.no_embeddings)
    
    elif args.command == "clear":
        success = await clear_database(verbose)
    
    elif args.command == "status":
        status = await show_status(verbose)
        success = status["initialized"]
    
    elif args.command == "migrate":
        success = await run_migrations(verbose)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
