#!/usr/bin/env python3
"""
Test script to verify all components are working
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import config
from database.models import create_tables, get_database_stats
from data_collection.api_client import ClashRoyaleAPI

def test_configuration():
    """Test configuration loading"""
    print("🔧 Testing configuration...")
    try:
        config.validate()
        print("✅ Configuration is valid")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_database():
    """Test database connection and table creation"""
    print("🗄️ Testing database...")
    try:
        success = create_tables()
        if success:
            stats = get_database_stats()
            print(f"✅ Database ready - {stats['battles']} battles, {stats['players']} players")
            return True
        else:
            print("❌ Database setup failed")
            return False
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_api():
    """Test Clash Royale API connection"""
    print("🎮 Testing Clash Royale API...")
    try:
        api = ClashRoyaleAPI()
        success = api.test_connection()
        return success
    except Exception as e:
        print(f"❌ API error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Running setup tests for Clash Royale Predictor\n")
    
    tests = [
        ("Configuration", test_configuration),
        ("Database", test_database), 
        ("API", test_api)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Testing {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:15} {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! You're ready to start collecting data.")
        print("\nNext steps:")
        print("1. Run: python scripts/collect_data.py")
        print("2. Monitor progress in your Supabase dashboard")
    else:
        print("\n⚠️ Some tests failed. Please fix the issues above before proceeding.")
        print("\nCommon fixes:")
        print("- Check your .env file has correct API token and database URL")
        print("- Verify your IP address is registered with Clash Royale API")
        print("- Ensure Supabase project is active and accessible")

if __name__ == "__main__":
    main()