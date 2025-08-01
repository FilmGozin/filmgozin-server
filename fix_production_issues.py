#!/usr/bin/env python3
"""
Fix Production Issues Script
This script helps fix common production issues with the FilmGozin server.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'filmgozin_server.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from movie.models import Movie
from user.models import ContactMessage

def check_database_schema():
    """Check if database schema matches models"""
    print("=== Checking Database Schema ===")
    
    try:
        with connection.cursor() as cursor:
            # Check ContactMessage table structure
            cursor.execute("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'user_contactmessage'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            
            print("ContactMessage table columns:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} (nullable: {col[2]})")
            
            # Check if phone_number column exists
            phone_col = [col for col in columns if col[0] == 'phone_number']
            if phone_col:
                print("❌ phone_number column still exists - needs migration")
                return False
            else:
                print("✅ phone_number column removed successfully")
                return True
                
    except Exception as e:
        print(f"❌ Error checking schema: {e}")
        return False

def test_contact_message_creation():
    """Test creating a contact message"""
    print("\n=== Testing Contact Message Creation ===")
    
    try:
        # Try to create a contact message
        message = ContactMessage.objects.create(
            name="Test User",
            email="test@example.com",
            message="Test message"
        )
        print(f"✅ Contact message created successfully: {message.id}")
        
        # Clean up
        message.delete()
        print("✅ Test message cleaned up")
        return True
        
    except Exception as e:
        print(f"❌ Error creating contact message: {e}")
        return False

def test_movie_admin():
    """Test movie admin functionality"""
    print("\n=== Testing Movie Admin ===")
    
    try:
        # Check if we can access movie admin
        from django.contrib import admin
        from movie.admin import MovieAdmin
        
        admin_instance = MovieAdmin(Movie, admin.site)
        print(f"✅ MovieAdmin created successfully")
        print(f"✅ List display: {admin_instance.list_display}")
        print(f"✅ List filters: {admin_instance.list_filter}")
        return True
        
    except Exception as e:
        print(f"❌ Error with MovieAdmin: {e}")
        return False

def check_movie_model():
    """Check movie model structure"""
    print("\n=== Checking Movie Model ===")
    
    try:
        # Check required fields
        required_fields = ['title', 'genre', 'original_language', 'release_year']
        for field in required_fields:
            if hasattr(Movie, field):
                print(f"✅ Field '{field}' exists")
            else:
                print(f"❌ Field '{field}' missing")
        
        # Check field types
        field_info = Movie._meta.get_field('genre')
        print(f"✅ Genre field type: {field_info.__class__.__name__}")
        print(f"✅ Genre choices: {len(field_info.choices)} options")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking movie model: {e}")
        return False

def run_migrations():
    """Run pending migrations"""
    print("\n=== Running Migrations ===")
    
    try:
        # Run migrations for all apps
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False

def main():
    """Main function to fix production issues"""
    print("Starting Production Issues Fix...")
    print("=" * 50)
    
    success = True
    
    # Run migrations first
    if not run_migrations():
        success = False
    
    # Check database schema
    if not check_database_schema():
        success = False
    
    # Test contact message creation
    if not test_contact_message_creation():
        success = False
    
    # Test movie admin
    if not test_movie_admin():
        success = False
    
    # Check movie model
    if not check_movie_model():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All production issues fixed!")
    else:
        print("❌ Some issues remain - check the output above")
    
    return success

if __name__ == '__main__':
    main() 