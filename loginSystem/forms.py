import uuid
from datetime import date

from django import forms
from django.contrib.admin import widgets
from django.forms.widgets import NumberInput, Select
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser, Film, Screen, Showing, Club, Transaction, UserCredit


class FilmForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FilmForm, self).__init__(*args, **kwargs)
        self.fields['film_id'].initial = uuid.uuid4()
        self.fields['film_id'].disabled = True

    class Meta:
        model = Film
        fields = ('film_id', 'title', 'description', 'age_rating', 'duration', 'image')


class ViewFilmForms(forms.ModelForm):
    class Meta:
        model = Film
        fields = ('title', 'description', 'image')


class ScreenForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ScreenForm, self).__init__(*args, **kwargs)
        self.fields['screen_id'].initial = uuid.uuid4()
        self.fields['screen_id'].disabled = True

    class Meta:
        model = Screen
        fields = ('screen_id', 'number', 'social_distancing')


class ViewScreenForms(forms.ModelForm):
    class Meta:
        model = Screen
        fields = ('number',)


class createClubDetailsForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = '__all__'


class TimePickerInput(forms.TimeInput):
    input_type = 'time'


class DatePickerInput(forms.DateInput):
    input_type = 'date'


class ShowingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ShowingForm, self).__init__(*args, **kwargs)
        self.fields['showing_id'].initial = uuid.uuid4()
        self.fields['showing_id'].disabled = True
        self.fields['screen'] = forms.ModelChoiceField(queryset=Screen.screens.all())
        self.fields['film'] = forms.ModelChoiceField(queryset=Film.films.all())
        self.fields['price'] = forms.FloatField()
        self.fields['date'] = forms.DateField(widget=DatePickerInput)

    class Meta:
        model = Showing
        fields = ('showing_id', 'film', 'screen', 'price', 'start_time')
        widgets = {
            'start_time': TimePickerInput()
        }


class AccountForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        #self.fields['id'].initial = uuid.uuid4()
        #self.fields['id'].disabled = True
        self.fields['user'] = forms.ModelChoiceField(queryset=CustomUser.objects.all())
        self.fields['credits'] = forms.IntegerField()
        self.fields['discount_rate'] = forms.DecimalField(max_digits=3, decimal_places=2)

    class Meta:
        model = UserCredit
        fields = ('user', 'credits', 'discount_rate')


class ViewShowingForms(forms.ModelForm):
    class Meta:
        model = Showing
        fields = ('film', 'screen', 'start_time')


class cardPaymentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(cardPaymentForm, self).__init__(*args, **kwargs)
        self.fields['name'] = forms.CharField(required=True, max_length=150)
        self.fields['cardnumber'] = forms.CharField(required=True, max_length=16)
        self.fields['expirationdate'] = forms.CharField(required=True, max_length=5)
        self.fields['securitycode'] = forms.Charfield(required=True, max_length=3)


        

class DateInput(forms.DateInput):
    input_type = 'date'

todaysDate = date.today()
strTodaysDate = todaysDate.strftime("%Y-%m-%d")

class CustomUserCreationForm(UserCreationForm):
    firstname = forms.CharField(max_length=50)
    lastname = forms.CharField(max_length=50)
    date_of_birth = forms.DateField(widget=DatePickerInput(attrs={'min': '1900-01-01', 'max': strTodaysDate}))
    clubChoice = forms.ModelChoiceField(queryset=Club.clubs.all(), widget=Select(attrs={'class' : 'form-control'}), required=False)
    class Meta:
        model = CustomUser
        fields = ('username', 'firstname', 'lastname', 'email', 'date_of_birth', 'password1', 'password2', 'clubChoice')

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = CustomUser.objects.exclude(pk=self.instance.pk).get(username=username)
        except CustomUser.DoesNotExist:
            return username
        raise forms.ValidationError(u'Username "%s" is already in use.' % username)


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('date_of_birth', 'first_name', 'last_name')
