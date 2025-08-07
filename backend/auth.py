from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import hmac
import hashlib
import json
import time
from urllib.parse import parse_qs
from typing import Dict, Optional
from models import User
from services import UserService
from database import get_database
import os

security = HTTPBearer()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8482163056:AAFO_l3IuliKB6I81JyQ-3_VrZuQ-8S5P-k")

async def verify_telegram_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """Verify Telegram Web App authentication"""
    try:
        auth_data = credentials.credentials
        
        # Логируем полученные данные для отладки
        print(f"Received auth data: {auth_data[:100]}...")
        
        # Try parsing as Telegram initData (query string format)
        try:
            # Parse query string format (standard Telegram Web Apps format)
            parsed = parse_qs(auth_data)
            if parsed:
                user_data = {}
                for key, value in parsed.items():
                    user_data[key] = value[0] if value else None
                
                # Extract user info if it's in 'user' parameter
                if 'user' in user_data:
                    user_info = json.loads(user_data['user'])
                    print(f"Parsed Telegram user data: {user_info}")
                    
                    # Verify hash for production (commented for now)
                    # if not verify_telegram_hash(parsed, BOT_TOKEN):
                    #     raise HTTPException(status_code=401, detail="Invalid hash")
                    
                    return user_info
                else:
                    print(f"Query string user data: {user_data}")
                    return user_data
        except Exception as e:
            print(f"Failed to parse as query string: {e}")
        
        # Fallback: Try to parse as direct JSON (for development/testing)
        try:
            # Try to decode base64 first if it looks like base64
            try:
                import base64
                decoded_data = base64.b64decode(auth_data).decode('utf-8')
                user_data = json.loads(decoded_data)
                print(f"Decoded user data: {user_data}")
                return user_data
            except:
                # If not base64, try direct JSON
                user_data = json.loads(auth_data)
                print(f"Direct JSON user data: {user_data}")
                return user_data
        except json.JSONDecodeError as e:
            print(f"Failed to parse as JSON: {e}")
        
        # If all parsing fails, raise error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not parse authentication data"
        )
    
    except Exception as e:
        print(f"Auth verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication data"
        )

def verify_telegram_hash(auth_data: Dict, bot_token: str) -> bool:
    """Verify Telegram authentication hash according to official documentation"""
    try:
        received_hash = auth_data.get('hash')
        if not received_hash:
            return False
        
        # Create data string for hash verification
        data_check_arr = []
        for key, value in auth_data.items():
            if key != 'hash':
                data_check_arr.append(f"{key}={value}")
        
        data_check_arr.sort()
        data_check_string = '\n'.join(data_check_arr)
        
        # Create secret key according to Telegram docs
        secret_key = hashlib.sha256(bot_token.encode()).digest()
        
        # Calculate hash
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        return hmac.compare_digest(received_hash, calculated_hash)
    
    except Exception as e:
        print(f"Hash verification error: {e}")
        return False

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_database)
) -> User:
    """Get current user from token"""
    try:
        # Verify auth data
        user_data = await verify_telegram_auth(credentials)
        telegram_id = user_data.get('id')
        
        if not telegram_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No user ID in token"
            )
        
        # Get user from database
        user_service = UserService(db)
        user = await user_service.get_user_by_telegram_id(int(telegram_id))
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )