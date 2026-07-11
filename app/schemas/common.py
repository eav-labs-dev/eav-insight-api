from pydantic import BaseModel, Field


class PaginationMeta(BaseModel):
    """Pagination metadata for list responses."""

    total: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)
    count: int = Field(ge=0)
    has_next: bool
    has_previous: bool
    next_offset: int | None = None
    previous_offset: int | None = None

    @classmethod
    def from_values(cls, *, total: int, limit: int, offset: int, count: int) -> "PaginationMeta":
        """Build pagination metadata from a query result slice."""
        has_next = offset + count < total
        has_previous = offset > 0
        previous_offset = max(offset - limit, 0) if has_previous else None
        next_offset = offset + limit if has_next else None

        return cls(
            total=total,
            limit=limit,
            offset=offset,
            count=count,
            has_next=has_next,
            has_previous=has_previous,
            next_offset=next_offset,
            previous_offset=previous_offset,
        )
