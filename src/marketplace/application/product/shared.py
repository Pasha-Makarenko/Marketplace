from marketplace.domain.entities.product.product import Product
from marketplace.domain.entities.seller.repository import SellerRepository
from marketplace.domain.exceptions import DomainError


async def check_product_ownership(
    product: Product,
    user_id: int,
    seller_repository: SellerRepository,
) -> None:
    seller = await seller_repository.by_user_id(user_id)
    if not seller:
        raise DomainError("User is not a seller.")

    if product.owner_id != seller.identity:
        raise DomainError("You are not the owner of this product.")
