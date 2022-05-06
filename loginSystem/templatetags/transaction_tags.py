from decimal import Decimal

from django import template

register = template.Library()


@register.filter(name='sum_transactions')
def sum_transactions(transactions):
    sum = Decimal(0.00)
    for transaction in transactions:
        sum += transaction.transactionTotal
    return sum
