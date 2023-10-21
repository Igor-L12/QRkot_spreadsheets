from sqlalchemy import Column, String

from .base_model import CharityBaseModel


class CharityProject(CharityBaseModel):
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)

    def __repr__(self):
        return (
            f"{super().__repr__()},"
            f"name={self.name},"
            f"description={self.description}"
        )
