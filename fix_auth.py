#!/usr/bin/env python3
"""
Quick fix script to ensure admin user exists in database
Run this on the droplet to fix authentication
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from user_management import UserManager

def main():
    print("Fixing authentication...")

    # Initialize UserManager (will create tables if they don't exist)
    manager = UserManager('data/users.db')

    print("Database initialized with admin user.")
    print("\nLogin credentials:")
    print("  Username: admin")
    print("  Password: changeme123")
    print("\n⚠️  IMPORTANT: Change this password immediately after logging in!")

if __name__ == "__main__":
    main()