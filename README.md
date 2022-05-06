# UWEFlix
A web-based cinema booking app, created using python and django.

## Usage Instructions
To launch the program, open a command prompt in the project directory and enter the following: `python manage.py runserver`.
The website can be viewed by entering `http://127.0.0.1:8000` into any browser of your choice.

## Account Creation
There are **5** types of user - **CinemaManager**, **AccountManager**, **Employee**, **ClubRep**, and **Student**.
**CinemaManager**, **AccountManager** and **Employee** are all "staff" accounts *(See **Creating Staff Accounts** for more info)*.
**ClubRep** and **Student** are student accounts *(See **Creating Student Accounts** for more info)*.
### Creating a Superuser
In order to set up the system, at least 1 superuser account is required. 
Open a command prompt in the project directory and enter the following: `python manage.py createsuperuser [username] [password]`
The cinema manager can be considered a superuser, but you can use any username or password that you like.

### Creating Staff Accounts
Staff accounts can be created through the *admin* panel, accessible via `http://127.0.0.1:8000/admin`. Only superusers/cinema managers can log onto the admin panel.
Within the admin panel, head to the *Users* section from the panel on the right-hand side. New users can be created within this area.
Once the user has been created, head to the *Groups* section. Select the group that you wish to add the user to and double-click their name from the *users* area.

*Note: if the groups are not created by default, then create them using the same names outlined in **Account Creation**.*

### Creating Student Accounts
Students and Club Reps can use the *register* page to sign up for an account. Entering all the relevant details and pressing *Register Account* will submit
an application for an account. The Cinema Manager can approve/deny these sign up requests from the *applications* page. 

*Note: when signing up, students should **NOT** select a club, but club reps should. See **Creating Clubs** for more information on creating a club.*

## Staff Features

### Creating Clubs
The Cinema Manager can create a club through the taskbar at the top of their page. Editing and deleting clubs is also available through this page.

### Financial Reports
The Account Manager can access the transactions page, which allows them to filter by the account that made the purchase, search start date/time, 
and search end date/time. A summation of the transaction totals can be found at the bottom of the page.

### Account Application Approval/Denial
The Cinema Manager can approve/deny account creation requests through a tab on their page.

