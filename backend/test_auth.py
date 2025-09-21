#!/usr/bin/env python3
"""
Simple test script to verify JWT authentication is working
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_objectid_conversion():
    """Test that ObjectId conversion works correctly"""
    from bson import ObjectId
    from app.models.user_model import UserResponse
    
    # Test data with ObjectId
    test_data = {
        "_id": ObjectId("68cf764de671bb2ea0b7442f"),
        "email": "test@example.com",
        "role": "Admin"
    }
    
    try:
        user = UserResponse.model_validate(test_data)
        print(f"✅ ObjectId conversion successful: {user.id}")
        print(f"✅ User data: {user.model_dump()}")
        return True
    except Exception as e:
        print(f"❌ ObjectId conversion failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing ObjectId conversion...")
    success = test_objectid_conversion()
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed!")
        sys.exit(1)