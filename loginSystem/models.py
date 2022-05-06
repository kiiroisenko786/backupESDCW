from django.contrib.auth.models import AbstractUser, User
from django.db import models
import uuid

from loginSystem.managers import CustomUserManager
from web_project import settings


class Film(models.Model):
    # UUID
    film_id = models.UUIDField(default=uuid.uuid4(), unique=True, blank=False, primary_key=True)
    # Other fields
    title = models.CharField(max_length=100, blank=False)
    description = models.CharField(max_length=1000, blank=False)
    age_rating = models.CharField(max_length=5, blank=False)
    duration = models.CharField(max_length=10, blank=False)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    films = models.Manager()

    def __str__(self):
        return f'{self.title} [id={self.film_id}]'

    class Meta:
        ordering = ['title']


class Screen(models.Model):
    # UUID
    screen_id = models.UUIDField(default=uuid.uuid4(), unique=True, blank=False, primary_key=True)
    # Other fields
    number = models.CharField(max_length=3, unique=True, blank=False)  # Each screen should have a unique number
    social_distancing = models.BooleanField(default=False, blank=True)  # Toggle on manually, off by default
    screens = models.Manager()

    def __str__(self):
        return f'{self.number} [id={self.screen_id}]'

    class Meta:
        ordering = ['number']


class Seat(models.Model):
    # UUID
    seat_id = models.UUIDField(default=uuid.uuid4(), unique=True, blank=False, primary_key=True)
    # Other fields
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE)  # Relation to Screen table
    vip = models.BooleanField(default=False)
    row = models.IntegerField(blank=False)
    column = models.IntegerField(blank=False)
    seats = models.Manager()

    def __str__(self):
        return f'{self.seat_id}: {self.screen} vip={self.vip} {self.row}{self.column}'

    class Meta:
        ordering = ['row']


class Showing(models.Model):
    # UUID
    showing_id = models.UUIDField(default=uuid.uuid4(), unique=True, blank=False, primary_key=True)
    # Other fields
    film = models.ForeignKey(Film, on_delete=models.CASCADE)  # Relation to Film table
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE)  # Relation to Screen table
    start_time = models.DateTimeField(auto_now=False)
    price = models.FloatField(default=0.0)
    showings = models.Manager()

    def __str__(self):
        return f'{self.showing_id}: {self.film} {self.screen} {self.start_time}'

    def get_film(self):
        return Film.films.get(film_id=self.film)

    def get_screen(self):
        return Screen.screens.get(screen_id=self.screen)

    class Meta:
        ordering = ['start_time']


class FinanceAccount(models.Model):
    # UUID
    account_id = models.UUIDField(default=uuid.uuid4(), unique=True, blank=False, primary_key=True)
    # Other fields
    title = models.CharField(max_length=40)
    card_num = models.CharField(max_length=20)
    expiry_date = models.CharField(max_length=10)
    discount_rate = models.FloatField(default=1.0)
    accounts = models.Manager()

    def __str__(self):
        return f'{self.account_id}: {self.title} {self.card_num} {self.expiry_date} {self.discount_rate}'

    class Meta:
        ordering = ['title']


class Club(models.Model):
    # UUID
    club_id = models.UUIDField(default=uuid.uuid4(), unique=True, blank=False, primary_key=True)
    # Other fields
    name = models.CharField(max_length=40)
    # Location details
    street_num = models.CharField(max_length=10)
    street_name = models.CharField(max_length=30)
    city = models.CharField(max_length=20)
    post_code = models.CharField(max_length=10)
    # Contact details
    email = models.CharField(max_length=100)
    landline_num = models.CharField(max_length=30)
    mobile_num = models.CharField(max_length=30)
    clubs = models.Manager()

    def __str__(self):
        return self.name

    # def __str__(self):
    #     return f'{self.club_id}: {self.account} {self.name} \n' \
    #            f'{self.street_num}, {self.street_name}, {self.city}, {self.post_code} \n' \
    #            f'{self.email} {self.landline_num} {self.mobile_num}'

    class Meta:
        ordering = ['name']

# class CustomUser(AbstractUser):
#     pass
#     date_of_birth = models.DateField(null=True, auto_now=False)
#     REQUIRED_FIELDS = []

#     objects = CustomUserManager()

#     def __str__(self):
#         return self.username

class CustomUser(AbstractUser):
    firstname = models.CharField(verbose_name="First name", max_length=100, blank=False, default="")
    lastname = models.CharField(verbose_name="Last name", max_length=100, blank=False, default="")
    date_of_birth = models.DateField(null=True, auto_now=False)
    is_active = models.BooleanField(default=False)
    clubChoice = models.CharField(verbose_name='club name', max_length=254, null=True, default=None)
    REQUIRED_FIELDS = []
    cardNumber = models.CharField(verbose_name="Card Number", max_length=16, blank=True)
    expiryDate = models.CharField(verbose_name="Expiry Date", max_length=5, blank=True)
    cvv = models.CharField(verbose_name="CVV", max_length=3, blank=True)

    objects = CustomUserManager()

    def __str__(self):
        return self.username

    def getUserActive(self):
        return self.is_active


class UserCredit(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, blank=False, editable=False, primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    credits = models.IntegerField(default=0)
    discount_rate = models.DecimalField(default=1.00, max_digits=3, decimal_places=2)

    objects = models.Manager()

    def __str__(self):
        return f'{self.user}, {self.credits}'

    class Meta:
        ordering = ['user']


class Booking(models.Model):
    # UUID
    booking_id = models.UUIDField(default=uuid.uuid4(), unique=True, blank=False, primary_key=True)
    # Other fields
    showing = models.ForeignKey(Showing, on_delete=models.CASCADE)
    seats = models.ManyToManyField(Seat, related_name="booking_seats")
    booking_type = models.CharField(default="purchase", max_length=10)
    total_spent = models.FloatField(default=0.00, verbose_name="Total spent", max_length=10)
    credit_acc = models.ForeignKey(UserCredit, related_name="credit_account", null=True, blank=True, on_delete=models.DO_NOTHING)
    associatedEmail = models.EmailField(verbose_name="associated email", blank=True)
    cancellationMarker = models.BooleanField(verbose_name="cancellation request?", default=False, blank=False)
    bookings = models.Manager()

    def __str__(self):
        return f'{self.showing}, {self.total_spent}, {self.booking_type}, {self.credit_acc}, {self.seats}'


class Transaction(models.Model):
    transactionID = models.UUIDField(default=uuid.uuid4(), unique=True, blank=False, editable=False, primary_key=True)
    payee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=None, blank=True, null=True)
    transactionType = models.CharField(verbose_name="Currency", max_length=6)
    transactionPurpose = models.CharField(verbose_name="Purpose", max_length=50, blank=False)
    transactionTotal = models.DecimalField(verbose_name="Total spent", max_digits=5, decimal_places=2)
    cardName = models.CharField(verbose_name="Payee Name", max_length=50, blank=True)
    cardNumber = models.CharField(verbose_name="Card Number", max_length=16, blank=True)
    expiryDate = models.CharField(verbose_name="Expiry Date", max_length=5, blank=True)
    cvv = models.CharField(verbose_name="CVV", max_length=3, blank=True)
    date = models.DateTimeField(auto_now=True)

    transactions = models.Manager()

    def __str__(self):
        return f'{self.transactionID}: {self.payee} {self.transactionType} {self.transactionTotal} {self.date}'

    class Meta:
        ordering = ['date']
