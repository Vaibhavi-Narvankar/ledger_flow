from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.core.exceptions import UserAlreadyExistsError
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserResponse


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.repository = UserRepository(db)

    async def create_user(self, data: UserCreate) -> UserResponse:
        email = str(data.email).strip().lower()

        existing_user = await self.repository.get_by_email(email)

        if existing_user is not None:
            raise UserAlreadyExistsError(
                "User with this email already exists"
            )

        user = User(email=email)

        try:
            user = await self.repository.create(user)
            await self.repository.db.commit()

        except IntegrityError as exc:
            await self.repository.db.rollback()

            if getattr(exc.orig, "sqlstate", None) == "23505":
                raise UserAlreadyExistsError(
                    "User with this email already exists"
                ) from None

            raise

        return UserResponse.model_validate(user)