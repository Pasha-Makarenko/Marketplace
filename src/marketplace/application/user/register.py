from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.user.factory import (
    CreateUserRequest,
    UserFactory,
)
from marketplace.domain.entities.user.repository import UserRepository


class RegisterUserCommand:
    def __init__(
        self,
        user_factory: UserFactory,
        user_repository: UserRepository,
        transaction_manager: TransactionManager,
    ) -> None:
        self._user_factory = user_factory
        self._user_repository = user_repository
        self._transaction_manager = transaction_manager

    async def execute(self, data: CreateUserRequest) -> int:
        user = await self._user_factory.create(data=data)

        self._user_repository.add(user)
        await self._transaction_manager.commit()

        return user.identity.value
