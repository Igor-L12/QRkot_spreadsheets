from typing import List
from app.models import CharityBaseModel


def invest_money(
    target: CharityBaseModel, sources: List[CharityBaseModel]
) -> List[CharityBaseModel]:
    if target.invested_amount is None:
        target.invested_amount = 0
    results = []
    for item in sources:
        remaining = item.to_invest_amount()
        to_invest = min(remaining, target.to_invest_amount())
        for object in item, target:
            object.invested_amount += to_invest
            if object.invested_amount == object.full_amount:
                object.set_fully_invested()
        results.append(item)
        if to_invest == 0:
            break
    return results
