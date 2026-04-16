"""
Database management script for Library API
Usage:
    python manage_db.py init     - Initialize database with sample data
    python manage_db.py reset    - Reset database to initial state
    python manage_db.py clear    - Clear all data from database
    python manage_db.py seed     - Add more sample books
"""

import sys
from app import app, db, Book
from datetime import datetime


def init_database():
    """Initialize database tables"""
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully")


def reset_database():
    """Reset database to initial state"""
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("🗑️  Dropped all tables")
        
        # Recreate tables
        db.create_all()
        print("✅ Recreated tables")
        
        # Add sample data
        add_sample_data()


def clear_database():
    """Clear all data from database"""
    with app.app_context():
        Book.query.delete()
        db.session.commit()
        print("✅ All books deleted")


def add_sample_data():
    """Add sample books to database"""
    with app.app_context():
        # Check if data already exists
        if Book.query.count() > 0:
            print("⚠️  Database already contains data. Use 'reset' to clear first.")
            return
        
        sample_books = [
            Book(
                title="Clean Code",
                author="Robert C. Martin",
                isbn="978-0132350884",
                year=2008,
                available=True
            ),
            Book(
                title="Design Patterns",
                author="Gang of Four",
                isbn="978-0201633610",
                year=1994,
                available=True
            ),
            Book(
                title="The Pragmatic Programmer",
                author="Andrew Hunt, David Thomas",
                isbn="978-0135957059",
                year=2019,
                available=False
            )
        ]
        
        db.session.add_all(sample_books)
        db.session.commit()
        print(f"✅ Added {len(sample_books)} sample books")


def seed_more_books():
    """Add more sample books for testing"""
    with app.app_context():
        more_books = [
            Book(
                title="Refactoring",
                author="Martin Fowler",
                isbn="978-0134757599",
                year=2018,
                available=True
            ),
            Book(
                title="You Don't Know JS",
                author="Kyle Simpson",
                isbn="978-1491950357",
                year=2015,
                available=True
            ),
            Book(
                title="Eloquent JavaScript",
                author="Marijn Haverbeke",
                isbn="978-1593279509",
                year=2018,
                available=True
            ),
            Book(
                title="Python Crash Course",
                author="Eric Matthes",
                isbn="978-1593279288",
                year=2019,
                available=False
            ),
            Book(
                title="Head First Design Patterns",
                author="Eric Freeman",
                isbn="978-0596007126",
                year=2004,
                available=True
            )
        ]
        
        db.session.add_all(more_books)
        db.session.commit()
        print(f"✅ Added {len(more_books)} more books")


def show_stats():
    """Show database statistics"""
    with app.app_context():
        total = Book.query.count()
        available = Book.query.filter_by(available=True).count()
        unavailable = Book.query.filter_by(available=False).count()
        
        print("📊 Database Statistics:")
        print(f"   Total books: {total}")
        print(f"   Available: {available}")
        print(f"   Unavailable: {unavailable}")


def list_books():
    """List all books in database"""
    with app.app_context():
        books = Book.query.all()
        
        if not books:
            print("📚 No books in database")
            return
        
        print(f"\n📚 Books in database ({len(books)} total):\n")
        for book in books:
            status = "✅" if book.available else "❌"
            print(f"  {status} [{book.id}] {book.title}")
            print(f"      Author: {book.author}")
            print(f"      ISBN: {book.isbn}, Year: {book.year}")
            print()


def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        print("Usage: python manage_db.py [command]")
        print("\nCommands:")
        print("  init     - Initialize database with sample data")
        print("  reset    - Reset database to initial state")
        print("  clear    - Clear all data from database")
        print("  seed     - Add more sample books")
        print("  stats    - Show database statistics")
        print("  list     - List all books")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    commands = {
        'init': lambda: (init_database(), add_sample_data()),
        'reset': reset_database,
        'clear': clear_database,
        'seed': seed_more_books,
        'stats': show_stats,
        'list': list_books
    }
    
    if command in commands:
        print(f"\n{'='*50}")
        print(f"  Library Database Management")
        print(f"{'='*50}\n")
        
        commands[command]()
        
        print(f"\n{'='*50}")
        print("  Done!")
        print(f"{'='*50}\n")
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: init, reset, clear, seed, stats, list")
        sys.exit(1)


if __name__ == '__main__':
    main()
