from marketplace.application.common.transaction_manager import (
    TransactionManager,
)
from marketplace.domain.entities.user.factory import (
    CreateUserRequest,
    UserFactory,
)


class RegisterUserCommand:
    def __init__(
        self,
        user_factory: UserFactory,
        transaction_manager: TransactionManager,
    ) -> None:
        self._user_factory = user_factory
        self._transaction_manager = transaction_manager

    async def execute(self, data: CreateUserRequest) -> int:
        user = await self._user_factory.create(data=data)

        await self._transaction_manager.commit()

        return user.identity.value
