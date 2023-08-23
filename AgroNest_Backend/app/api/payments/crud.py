from ..auth.models import User, Wallet
from sqlmodel import Session, select


# async def find_existed_user(user_id: str, db: Session) -> User | None:
#     """
#     A method to fetch a user info given an email.

#     Args:
#         email (EmailStr) : A given user email.
#         session (AsyncSession) : SqlAlchemy session object.

#     Returns:
#         Dict[str, Any]: a dict object that contains info about a user.
#     """
#     user = db.get(User, user_id)
#     return user


def get_wallet(id: str, db: Session) -> Wallet | None:
    """
    A method to fetch a user info given an email.

    Args:
        email (EmailStr) : A given user email.
        session (AsyncSession) : SqlAlchemy session object.

    Returns:
        Dict[str, Any]: a dict object that contains info about a user.
    """
    statement = select(Wallet).where(Wallet.id == id)
    results = db.exec(statement)
    wallet = results.one()
    return wallet

def update_wallet(wallet: Wallet, db: Session) -> Wallet:
    """
    A method to fetch a user info given an email.

    Args:
        email (EmailStr) : A given user email.
        session (AsyncSession) : SqlAlchemy session object.

    Returns:
        Dict[str, Any]: a dict object that contains info about a user.
    """
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet
