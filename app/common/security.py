from passlib.context import CryptContext

# bcrypt 해시 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    비밀번호를 bcrypt로 해싱합니다.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    평문 비밀번호와 해시된 비밀번호가 일치하는지 검증합니다.
    """
    return pwd_context.verify(plain_password, hashed_password)
