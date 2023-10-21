from sqlalchemy import Column, ForeignKey, Integer, String

from .base_model import CharityBaseModel


class Donation(CharityBaseModel):
    comment = Column(String)
    user_id = Column(Integer, ForeignKey("user.id"))

    def __repr__(self):
        return (
            f"{super().__repr__()},"
            f"user_id={self.user_id},"
            f"comment={self.comment}"
        )
