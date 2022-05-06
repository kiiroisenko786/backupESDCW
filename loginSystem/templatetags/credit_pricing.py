from django import template

from loginSystem.models import UserCredit

register = template.Library()


@register.filter(name='check_balance')
def check_balance(user, price):
    credit_price = price * 100
    user_credits = UserCredit.objects.get(user=user.id).credits
    if float(user_credits) >= float(credit_price):
        return True
    else:
        return False


@register.filter(name='get_price_cred')
def get_price_cred(price):
    credit_price = int(price * 100)
    return credit_price
