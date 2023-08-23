import logging
import traceback
from .models import User, Wallet, Userr
from sqlmodel import Session, select


async def find_existed_user(user_id: str, db: Session) -> Userr | None:
    """
    A method to fetch a user info given an email.

    Args:
        email (EmailStr) : A given user email.
        session (AsyncSession) : SqlAlchemy session object.

    Returns:
        Dict[str, Any]: a dict object that contains info about a user.
    """
    user = db.get(Userr, user_id)
    return user


def get_user(identifier: str, db: Session) -> Userr | None:
    """
    A method to fetch a user info given an email or username.

    Args:
        email (EmailStr) : A given user email.
        session (AsyncSession) : SqlAlchemy session object.

    Returns:
        Dict[str, Any]: a dict object that contains info about a user.
    """

    try:
        statement = select(Userr).where(Userr.email == identifier)
        results = db.exec(statement)
        user = results.one_or_none()
        print(user)

        # Email failed, try username
        if user is None:
            statement = select(Userr).where(Userr.username == identifier)
            results = db.exec(statement)
            user = results.one_or_none()

        print(user)
        return user
    except Exception as e:
        logging.error(traceback.format_exc())
        return None


async def create_user(user: User, db: Session) -> User:
    """
    A method to insert a user into the users table.

    Args:
        user (UserCreate) : A user schema object that contains all info about a user.
        session (AsyncSession) : SqlAlchemy session object.

    Returns:
        Result: Database result.
    """
    user.wallet = Wallet()
    db.add(user)
    db.commit()
    db.refresh(user)

    return user
