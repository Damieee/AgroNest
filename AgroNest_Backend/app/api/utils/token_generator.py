# token_generator.py
import uuid

class TokenGenerator:
    
    @staticmethod
    async def generate_token():
        token = str(uuid.uuid4())  # Generate a UUID token
        return token
