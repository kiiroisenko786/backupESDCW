import datetime
import os
import pathlib
from tempfile import NamedTemporaryFile

from django.core.exceptions import ObjectDoesNotExist
import uuid
import csv
from django.template.defaultfilters import slugify

from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpRequest, HttpResponse, FileResponse
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.views.generic import ListView, DeleteView
from django.contrib.auth.models import Group

from .forms import CustomUserCreationForm, FilmForm, ScreenForm, ShowingForm, createClubDetailsForm, AccountForm
from .emails import emailBuilder

# Create your views here.
from .models import CustomUser, Film, Screen, Showing, Seat, Booking, Transaction, UserCredit, Club


def layoutViews(request):
    return render(request, "loginSystem/layout.html")


def addCredits(request):
    id = request.POST.get('id')
    user = get_object_or_404(CustomUser, id=id)
    userBalance = user.credits
    inputCredits = request.POST.get('creditInput')
    user.credits = float(userBalance) + float(inputCredits)
    user.save()
    return redirect("topUpCredits")


def payWithCardUnauth(request):
    context = {}

    if request.method == "POST":
        print(request.POST)
        context['type'] = request.POST.get('type')
        context['amount_to_pay'] = request.POST.get('amount_to_pay')
        context['showing_id'] = request.POST.get('showing_id')
        seats = request.POST.getlist('booked_seats')
        context['seats'] = seats

    return render(request, "loginSystem/payWithCardUnauth.html", context=context)


@login_required()
def topUp(request):
    context = {}
    try:
        context['user_credits'] = UserCredit.objects.get(user=request.user).credits
    except ObjectDoesNotExist:
        UserCredit.objects.create(user=request.user)
        context['user_credits'] = UserCredit.objects.get(user=request.user).credits

    print(UserCredit.objects.get(user=request.user).credits)

    return render(request, "loginSystem/topUpCredits.html", context)


def makeUserClubrep(user):
    targetGroup = Group.objects.get(name="ClubRep")
    targetGroup.user_set.add(user)
    print("User has been made club rep")


def home(request):
    if request.user.is_authenticated:
        if check_cinema_manager(request.user):
            return redirect('cinemaManagerPage')
        elif check_account_manager(request.user):
            return redirect('accountManagerPage')
        elif check_employee(request.user):
            return redirect('employeePage')
        elif check_club_student(request.user):
            return redirect('clubRepPage')

    context = {}
    film_list = []
    for film in Film.films.all():
        film_list.append(film)
    context['film_list'] = film_list
    return render(request, "loginSystem/home.html", context)


def check_cinema_manager(user):
    return user.groups.filter(name="CinemaManager").exists()


def check_account_manager(user):
    return user.groups.filter(name="AccountManager").exists()


def check_employee(user):
    return user.groups.filter(name="Employee").exists()


def check_staff(user):
    return user.groups.filter(name="Employee").exists() or user.groups.filter(name="CinemaManager").exists()


def check_club_rep(user):
    return user.groups.filter(name="ClubRep").exists()


def check_club_student(user):
    return user.groups.filter(name="ClubRep").exists() or user.groups.filter(name="Student").exists()


def check_user_authenticated(user):
    return user.is_authenticated


def check_user_unauthenticated(user):
    return not user.is_authenticated


@login_required
@user_passes_test(check_cinema_manager)
def menuForClubPage(request):
    return render(request, "loginSystem/clubPage.html")


@login_required
@user_passes_test(check_cinema_manager)
def createClubDetails(request):
    form = createClubDetailsForm(request.POST or None)
    context = {"form": form}
    if request.method == "POST":
        if form.is_valid():
            clubName = request.POST['name']

            group = Group(name=clubName)
            group.save()

            form.save()
            return redirect('showClubDetails')
        else:
            return render(request, "loginSystem/createClubDetails.html", context)
    else:
        return render(request, "loginSystem/createClubDetails.html", context)


@login_required
@user_passes_test(check_cinema_manager)
def showClubDetails(request):
    database = Club.clubs.all()

    context = {"database": database}

    return render(request, "loginSystem/showClubDetails.html", context)


@login_required
@user_passes_test(check_cinema_manager)
def editClubDetails(request, pk):
    formOutput = Club.clubs.get(club_id=pk)

    form = createClubDetailsForm(instance=formOutput)

    if request.method == 'POST':
        form = createClubDetailsForm(request.POST, instance=formOutput)
        if form.is_valid():
            form.save()
            return redirect('showClubDetails')

    context = {'form': form}

    return render(request, "loginSystem/editClubDetails.html", context)


@login_required
@user_passes_test(check_account_manager)
def downloadReport(request):
    context = {}

    if request.method == 'POST':
        headers = ['Transaction ID', 'Payee Name', 'Time of Purchase', 'Purpose', 'Currency/Type', 'Transaction Total']
        transaction_ids = request.POST.getlist('trans')
        transactions = []
        report_name = slugify(f'report_{datetime.datetime.now()}')
        report_name = report_name + ".csv"

        for tid in transaction_ids:
            transactions.append(Transaction.transactions.get(pk=tid))
            print(Transaction.transactions.get(pk=tid))

        with open(report_name, 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            for transaction in transactions:
                as_row = [transaction.transactionID, transaction.payee, transaction.date, transaction.transactionPurpose, transaction.transactionType, transaction.transactionTotal]
                writer.writerow(as_row)
            writer.writerow([])
            writer.writerow(['Sum', request.POST.get('sum')])

        file_to_download = open(str(report_name), 'rb')
        response = FileResponse(file_to_download, content_type='application/csv')
        response['Content-Disposition'] = f'inline; filename={report_name}'
        return response

    return redirect('transactions')


@login_required
@user_passes_test(check_staff)
def editShowingsView(request, pk):
    formOutput = Showing.showings.get(showing_id=pk)

    form = ShowingForm(instance=formOutput)

    if request.method == 'POST':
        form = ShowingForm(request.POST, instance=formOutput)

        datetxt = f"{form.data['date']} {form.data['start_time']}"
        dt = datetime.datetime.strptime(datetxt, '%Y-%m-%d %H:%M')
        data = form.data.copy()
        data['start_time'] = dt
        form.data = data
        print(form.data)

        if form.is_valid():
            form.save()
            return redirect('showings')

    context = {'form': form}

    return render(request, "loginSystem/editShowings.html", context)


def deleteClubDetails(request, pk):
    database = Club.clubs.get(club_id=pk)

    if request.method == "POST":
        database.delete()
        return redirect('showClubDetails')

    context = {"database": database}

    return render(request, "loginSystem/deleteClubDetails.html", context)


@login_required
def topUpCard(request):
    context = {}

    if request.method == "POST":
        print(request.POST)
        context['type'] = request.POST.get('type')
        amount = float(request.POST.get('creditInput')) / 100
        context['amount_to_pay'] = f'{amount:.2f}'

    return render(request, "loginSystem/payWithCardAuth.html", context=context)

@login_required()
@user_passes_test(check_cinema_manager)
def cancellations(request):
    ls = Booking.bookings.all()
    for booking in ls:
        # print(f'ID: {booking.booking_id} Status: {booking.cancellationMarker}')
        print(f'{booking.booking_id} // {booking}')
    return render(request, "loginSystem/viewCancellationRequests.html", {"ls": ls})


@login_required
def topUpSuccess(request):
    context = {}

    if request.method == "POST":
        context['amount_to_pay'] = request.POST.get('total')

        num_credits = int(float(request.POST.get('total')) * 100)
        try:
            set = UserCredit.objects.get(user=request.user)
            set.credits += num_credits
            print(UserCredit.objects.get(user=request.user))
            set.save()
        except ObjectDoesNotExist:
            UserCredit.objects.create(user=request.user)
            print(UserCredit.objects.get(user=request.user))
        total = float(request.POST.get('total'))
        transaction = Transaction()
        transaction.transactionID = uuid.uuid4()
        transaction.transactionTotal = total
        transaction.payee = request.user
        transaction.transactionType = "GBP (£)"
        transaction.transactionPurpose = "Topping up account"
        transaction.cardName = request.POST.get('name')
        transaction.cardNumber = request.POST.get('cardnumber')
        transaction.expiryDate = request.POST.get('expiry')
        transaction.cvv = request.POST.get('cvv')
        transaction.save()
        return redirect("topUp")

    return redirect("topUp")


@login_required()
@user_passes_test(check_cinema_manager)
def viewBookingData(request):
    id = request.POST.get('id')
    print(id)
    booking = get_object_or_404(Booking, booking_id=id)
    return render(request, "loginSystem/showBookingData.html", {'booking':booking})

@login_required()
@user_passes_test(check_cinema_manager)
def viewAppData(request):
    id = request.POST.get('id')
    print(id)
    user = get_object_or_404(CustomUser, id=id)
    return render(request, "loginSystem/showAppData.html", {'user':user})

@login_required
@user_passes_test(check_cinema_manager)
def acceptUserApplication(request):
    id = request.POST.get('id')
    print(id)
    user = get_object_or_404(CustomUser, id=id)
    user.is_active = True
    if user.clubChoice is not None:
        makeUserClubrep(user)
    user.save()
    print("User has been accepted")
    receiver_email = user.email
    emailBuilder("acceptance", receiver_email)
    ls = CustomUser.objects.all()
    return render(request, "loginSystem/applications.html", {"ls":ls})

@login_required
@user_passes_test(check_cinema_manager)
def rejectUserApplication(request):
    id = request.POST.get('id')
    print(id)
    try:
        user = get_object_or_404(CustomUser, id=id)
        receiver_email = user.email
        user.delete()
        print("User successfully deleted!")
        emailBuilder("rejection", receiver_email)
    except CustomUser.DoesNotExist:
        return render(request, "loginSystem/applications.html")
    except Exception as e:
        return render(request, "loginSystem/applications.html")
    return render(request, "loginSystem/applications.html")

@login_required()
@user_passes_test(check_cinema_manager)
def applications(request):
    ls = CustomUser.objects.all()
    return render(request, "loginSystem/applications.html", {"ls":ls})

@login_required
@user_passes_test(check_cinema_manager)
def cinema_manager_page(request):
    context = {}
    film_list = []
    for film in Film.films.all():
        film_list.append(film)
    context['film_list'] = film_list
    return render(request, "loginSystem/cinemaManagerPage.html", context)


@login_required
@user_passes_test(check_account_manager)
def accounts(request):
    context = {}
    acc = []
    for account in UserCredit.objects.all():
        acc.append(account)
    context['accounts'] = acc
    return render(request, "loginSystem/creditAccountsPage.html", context)


@login_required
@user_passes_test(check_account_manager)
def edit_account(request, pk):
    formOutput = UserCredit.objects.get(id=pk)

    form = AccountForm(instance=formOutput)

    if request.method == 'POST':
        form = AccountForm(request.POST, instance=formOutput)

        if form.is_valid():
            form.save()
            return redirect('accounts')

    context = {'form': form}

    return render(request, "loginSystem/editAccounts.html", context)



@login_required
@user_passes_test(check_cinema_manager)
def add_film_page(request):
    form = FilmForm(request.POST, request.FILES, initial={'film_id': uuid.uuid4})
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect("films")
        else:
            return render(request, "loginSystem/addPage.html", {"form": form})

    return render(request, "loginSystem/addPage.html", {"form": form})


@login_required
@user_passes_test(check_cinema_manager)
def add_screen_page(request):
    form = ScreenForm(request.POST, initial={'film_id': uuid.uuid4})
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect("screens")
        else:
            return render(request, "loginSystem/addPage.html", {"form": form})

    return render(request, "loginSystem/addPage.html", {"form": form})


@login_required
@user_passes_test(check_cinema_manager)
def add_showing_page(request):
    form = ShowingForm(request.POST, initial={'showing_id': uuid.uuid4})
    if request.method == 'POST':
        datetxt = f"{form.data['date']} {form.data['start_time']}"
        dt = datetime.datetime.strptime(datetxt, '%Y-%m-%d %H:%M')
        data = form.data.copy()
        data['start_time'] = dt
        form.data = data
        print(form.data)
        if form.is_valid():
            form.save()
            return redirect("showings")
        else:
            return render(request, "loginSystem/addPage.html", {"form": form})

    return render(request, "loginSystem/addPage.html", {"form": form})


@login_required
@user_passes_test(check_account_manager)
def account_manager_page(request):
    context = {}
    film_list = []
    for film in Film.films.all():
        film_list.append(film)
    context['film_list'] = film_list
    return render(request, "loginSystem/accountManagerPage.html", context)


@login_required
@user_passes_test(check_employee)
def employee_page(request):
    context = {}
    film_list = []
    for film in Film.films.all():
        film_list.append(film)
    context['film_list'] = film_list
    return render(request, "loginSystem/employeePage.html", context)


@login_required
@user_passes_test(check_club_rep)
def club_rep_page(request):
    context = {}
    film_list = []
    for film in Film.films.all():
        film_list.append(film)
    context['film_list'] = film_list
    return render(request, "loginSystem/clubRepPage.html", context)


# def register_user(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             return HttpResponse("registered")

#     return render(request, "loginSystem/registerPage.html", {})

def register_user(request):
    form = CustomUserCreationForm()
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get("username")
            messages.success(request, "Account registration has been submitted for " + user)
            receiver_email = request.POST.get('email')
            emailBuilder("registration", receiver_email)
            return redirect("loginPage")
    context = {'form':form}
    return render(request, 'loginSystem/registerPage.html', context)


class FilmList(ListView):
    model = Film

    def get_context_data(self, **kwargs):
        context = super(FilmList, self).get_context_data(**kwargs)
        return context


class ShowingList(ListView):
    model = Showing

    def get_context_data(self, **kwargs):
        context = super(ShowingList, self).get_context_data(**kwargs)
        return context


@login_required
@user_passes_test(check_cinema_manager)
def delete_film(request):
    # dictionary for initial data with
    # field names as keys
    context = {}

    # fetch the object related to passed id
    # obj = get_object_or_404(Film, id = id)
    film_id = request.POST.get('film_id')
    print(film_id)
    obj = get_object_or_404(Film, film_id=film_id)

    if request.method == "POST":
        print(request)
        # delete object
        if obj.image:
            obj.image.delete()
        obj.delete()
        # after deleting redirect to
        # home page
        return redirect("films")

    return render(request, "loginSystem/films_list.html", context)


@login_required
@user_passes_test(check_cinema_manager)
def delete_showing(request):
    # dictionary for initial data with
    # field names as keys
    context = {}

    # fetch the object related to passed id
    # obj = get_object_or_404(Film, id = id)
    showing_id = request.POST.get('showing_id')
    print(showing_id)
    obj = get_object_or_404(Showing, showing_id=showing_id)

    if request.method == "POST":
        # delete object
        obj.delete()
        # after deleting redirect to
        # home page
        return redirect("showings")

    return render(request, "loginSystem/showing_list.html", context)


@login_required
@user_passes_test(check_cinema_manager)
def build_seats(request):
    # dictionary for initial data with
    # field names as keys
    context = {}

    # fetch the object related to passed id
    # obj = get_object_or_404(Film, id = id)
    screen_id = request.POST.get('screen_id')
    print(screen_id)
    obj = get_object_or_404(Screen, screen_id=screen_id)

    if request.method == "POST":
        # delete object
        row_len = 6
        col_len = 6
        for x in range(row_len):
            for y in range(col_len):
                # Create new seat
                seat = Seat(seat_id=uuid.uuid4(), screen=obj, vip=False, row=x, column=y)
                seat.save()
        # after deleting redirect to
        # home page
        return redirect("screens")

    return render(request, "loginSystem/screen_list.html", context)


class SeatAvailability():
    def __init__(self, seat, status):
        self.seat = seat
        self.status = status

    def __str__(self):
        return f'{self.seat.row}{self.seat.column}, {self.status}'


def show_seats(request):
    context = {}

    if request.method == "POST":
        context['showing_id'] = request.POST.get('showing_id')
        showing_id = request.POST.get('showing_id')
        showing = get_object_or_404(Showing, showing_id=showing_id)
        screen = showing.screen
        seats = Seat.seats.filter(screen_id=screen.screen_id)
        booked_seats = []
        if screen.social_distancing:
            # Make every other seat unavailable to book
            current_row = 0
            counter = 0
            for seat in seats:
                if seat.row != current_row:
                    current_row = seat.row
                    counter = counter + 1
                if counter == 1:
                    booked_seats.append(seat)
                counter = (counter + 1) % 2
        # Get a list of seats that have already been booked
        for booking in Booking.bookings.filter(showing_id=showing_id):
            booked = booking.seats.all()
            for seat in booked:
                booked_seats.append(seat)
        seat_maps = []
        for seat in seats:
            while int(seat.row) > len(seat_maps) - 1:
                seat_maps.append([])
            if seat in booked_seats:
                # Make seat unavailable
                seat_maps[int(seat.row)].append(SeatAvailability(seat, False))
            else:
                seat_maps[int(seat.row)].append(SeatAvailability(seat, True))
        if len(seat_maps) == 0:
            return HttpResponse("Error - no seats found for this screen")
        context['seat_maps'] = seat_maps
        return render(request, "loginSystem/seatsPage.html", context)
    else:
        return render(request, "loginSystem/seatsPage.html", context)


def confirm_booking(request):
    context = {}

    if request.method == "POST":
        print(request.POST)
        showing_id = request.POST.get('showing_id')
        showing = get_object_or_404(Showing, showing_id=showing_id)
        seats = []
        names = []
        for seat_id in request.POST.getlist('seats'):
            seats.append(seat_id)
            seat = get_object_or_404(Seat, seat_id=seat_id)
            names.append(f'{seat.row}{seat.column}')
        context['showing'] = showing
        context['bseats'] = seats
        context['num_seats'] = len(seats)
        context['names'] = names
        context['total_price'] = showing.price * len(seats)
        if request.user.is_authenticated:
            try:
                credits = UserCredit.objects.get(user=request.user)
            except ObjectDoesNotExist:
                UserCredit.objects.create(user=request.user)
                credits = UserCredit.objects.get(user=request.user)
            context['user_credits'] = credits

    return render(request, "loginSystem/confirmBooking.html", context)


def booking_confirmed(request):
    context = {}

    if request.method == "POST":
        showing_id = request.POST.get('showing_id')
        showing = get_object_or_404(Showing, showing_id=showing_id)
        context['showing'] = showing
        context['total'] = request.POST.get('total')
        booking = Booking.bookings.create(booking_id=uuid.uuid4(), showing=showing, total_spent=float(request.POST.get('total')), booking_type=request.POST.get('type'))
        seats = []
        for seat_id in request.POST.getlist('seats'):
            seat = get_object_or_404(Seat, seat_id=seat_id)
            seats.append(seat)
            booking.seats.add(seat)
        print(booking)
        context['seats'] = seats
        context['booking_id'] = booking.booking_id

        if not request.user.is_authenticated:
            # Generate transaction
            transaction = Transaction()
            transaction.transactionID = uuid.uuid4()
            transaction.transactionTotal = request.POST.get('total')
            transaction.transactionType = "GBP (£)"
            transaction.transactionPurpose = "Booking seats for film"
            transaction.cardName = request.POST.get('name')
            transaction.cardNumber = request.POST.get('cardnumber')
            transaction.expiryDate = request.POST.get('expiry')
            transaction.cvv = request.POST.get('cvv')
            transaction.save()
        else:
            # Subtract credits from account
            userCreds = UserCredit.objects.get(user=request.user)
            total = int(request.POST.get('total'))
            print(userCreds.credits)
            print(total)
            userCreds.credits = userCreds.credits - total
            userCreds.save()
            booking.credit_acc = userCreds
            associatedEmail = request.POST.get("confirmation_address")
            if associatedEmail is not None:
                booking.associatedEmail = associatedEmail
                booking.save()
                stringID = str(booking.booking_id)
                emailBuilder("booking", associatedEmail, stringID)
            else:
                booking.save()

    return render(request, "loginSystem/bookingConfirmed.html", context)

def cancelBooking(request):
    context = {}
    return render(request, "loginSystem/cancelBooking.html", context)

def cancelBookingProcess(request):
    bookingID = request.POST.get('booking_id')
    print(f'Retrieved ID: {bookingID}')
    try:
        targetBooking = get_object_or_404(Booking, booking_id=bookingID)
        print(f'Target booking ID: {str(targetBooking.booking_id)}')
        if targetBooking.cancellationMarker == False:
            targetBooking.cancellationMarker = True
            targetBooking.save()
            print(f'ID: {targetBooking.booking_id} Status: {targetBooking.cancellationMarker}')
            userEmail = targetBooking.associatedEmail
            if userEmail is not None:
                stringID = str(targetBooking.booking_id)
                print(f'Split ID: {stringID}')
                emailBuilder("cancellationRequest", userEmail, stringID)
    except Exception as e:
        print(e)
    return render(request, "loginSystem/layout.html")

def rejectBookingCancellation(request):
    bookingID = request.POST.get('id')
    print(f'Retrieved ID: {bookingID}')
    try:
        targetBooking = get_object_or_404(Booking, booking_id=bookingID)
        stringID = str(targetBooking.booking_id)
        userEmail = targetBooking.associatedEmail
        print(f'Target booking ID: {str(targetBooking.booking_id)}')
        targetBooking.cancellationMarker = True
        targetBooking.save()
        emailBuilder("cancellationReject", userEmail, stringID)
    except Exception as e:
        print(e)
    return render(request, "loginSystem/layout.html")

def processBookingCancellation(request):
    bookingID = request.POST.get('id')
    print(f'Retrieved ID: {bookingID}')
    try:
        targetBooking = get_object_or_404(Booking, booking_id=bookingID)
        print(f'Target booking ID: {str(targetBooking.booking_id)}')
        userEmail = targetBooking.associatedEmail
        if userEmail is not None:
            stringID = str(targetBooking.booking_id)
            # splitStringID = stringID[7:(len(stringID)-4)]
            print(f'Split ID: {stringID}')
            emailBuilder("cancellation", userEmail, stringID)
            print("Cancellation email sent!")
        targetBooking.delete()
        print("Booking deleted!")
        if request.user.is_authenticated:
            userCreds = UserCredit.objects.get(user=request.user)
            total = targetBooking.total_spent
            print(userCreds.credits)
            print(total)
            userCreds.credits = userCreds.credits + total
            userCreds.save()
            print(userCreds.credits)
            print(f"Credit user has been refunded, new balance: {userCreds.credits}")
    except Exception as e:
        print(e)
        bookings = Booking.bookings.all()
        for booking in bookings:
            print(f'Booking ID: {bookingID} / {booking.booking_id}')
    # if targetBooking.credit_acc is not None:
    #     targetBooking.credit_acc
    # bookings = Booking.bookings.all()
    # for booking in bookings:
    #     print(f'Booking ID: {bookingID} / {booking.booking_id}')
    #     if str(bookingID) == str(booking.booking_id):
    #         print("FOUND!")
        # if str(booking.booking_id) == str(bookingID):
        #     try:
        #         booking = get_object_or_404(Booking, booking_id=bookingID)
        #         booking.delete()
        #         print("Successfully deleted")
        #     except Exception as e:
        #         print(e)
    return render(request, "loginSystem/layout.html")

@user_passes_test(check_account_manager)
def view_transactions(request):
    context = {}

    if request.method == 'GET':
        transactions_matching_criteria = Transaction.transactions.order_by('date')
        context['transactions'] = transactions_matching_criteria

    if request.method == 'POST':
        start_date = None
        end_date = None

        startdatetxt = ''
        enddatetxt = ''
        temp_time = "00:00"
        print(request.POST.get('start_time'))
        print(request.POST.get('start_time'))
        if request.POST.get('start_date') != '':
            startdatetxt = f"{request.POST.get('start_date')} "
            if request.POST.get('start_time') != '':
                startdatetxt = startdatetxt + f'{request.POST.get("start_time")}'
                start_date = datetime.datetime.strptime(startdatetxt, '%Y-%m-%d %H:%M')
            else:
                startdatetxt = startdatetxt + temp_time
                start_date = datetime.datetime.strptime(startdatetxt, '%Y-%m-%d %H:%M')

        if request.POST.get('end_date') != '':
            enddatetxt = f"{request.POST.get('end_date')} "
            if request.POST.get('end_time') != '':
                enddatetxt = enddatetxt + f'{request.POST.get("end_time")}'
                end_date = datetime.datetime.strptime(enddatetxt, '%Y-%m-%d %H:%M')
            else:
                enddatetxt = enddatetxt + temp_time
                end_date = datetime.datetime.strptime(enddatetxt, '%Y-%m-%d %H:%M')

        account = request.POST.get('account')

        if account == ".....":
            account = None

        transactions_matching_criteria = Transaction.transactions.order_by('date')

        if account is not None:
            if account != "no_user":
                payee = CustomUser.objects.get(id=account)
            else:
                payee = None
            transactions_matching_criteria = transactions_matching_criteria.filter(payee=payee)

        if start_date is not None:
            transactions_matching_criteria = transactions_matching_criteria.filter(date__range=[f'{start_date}', datetime.datetime.now()])

        if end_date is not None:
            transactions_matching_criteria = transactions_matching_criteria.filter(date__range=[f'{transactions_matching_criteria.first().date}', f'{end_date}'])

        context['transactions'] = transactions_matching_criteria
        context['payee'] = account
        context['start_date'] = start_date
        context['end_date'] = end_date

    context['accounts'] = CustomUser.objects.all()

    return render(request, "loginSystem/transactions.html", context)


def view_film_showings(request):

    context = {}

    if request.method == "POST":
        film_id = request.POST.get('film_id')
        obj = get_object_or_404(Film, film_id=film_id)
        # Build showing list from film
        print(obj)
        showings = Showing.showings.filter(film=obj)
        context['showing_list'] = showings
        context['film_name'] = obj.title
        return render(request, "loginSystem/film_showings.html", context)
    else:
        return render(request, "loginSystem/film_showings.html", context)


class ScreenList(ListView):
    """Renders the home page, with a list of all messages."""
    model = Screen

    def get_context_data(self, **kwargs):
        context = super(ScreenList, self).get_context_data(**kwargs)
        return context


@login_required
@user_passes_test(check_cinema_manager)
def delete_screen(request):
    # dictionary for initial data with
    # field names as keys
    context = {}

    # fetch the object related to passed id
    # obj = get_object_or_404(Film, id = id)
    screen_id = request.POST.get('screen_id')
    print(screen_id)
    obj = get_object_or_404(Screen, screen_id=screen_id)

    if request.method == "POST":
        print(request)
        # delete object
        obj.delete()
        # after deleting redirect to
        # home page
        return redirect("screens")

    return render(request, "screen_list.html", context)


@user_passes_test(check_user_unauthenticated)
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        print(request.user)
        print(request.user.groups)
        if user is not None and user.is_active:
            login(request, user)
            if user.groups.filter(name='CinemaManager').exists():
                return redirect('cinemaManagerPage')
            elif user.groups.filter(name='AccountManager').exists():
                return redirect('accountManagerPage')
            elif user.groups.filter(name='Employee').exists():
                return redirect('employeePage')
            elif user.groups.filter(name='ClubRep').exists():
                return redirect('clubRepPage')
            else:
                return HttpResponse("Logged in as an invalid user - probably no group assigned?")
        else:
            messages.info(request, 'Invalid Login Info')

    context = {}
    return render(request, "loginSystem/loginPage.html", context)


@user_passes_test(check_user_authenticated)
def userLogout(request):
    logout(request)
    return redirect('home')
