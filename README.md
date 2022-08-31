# UWEFlix
A web-based cinema booking app, created using python and django.

## Usage Instructions
To launch the program, open a command prompt in the project directory and enter the following: `python manage.py runserver`.
The website can be viewed by entering `http://127.0.0.1:8000` into any browser of your choice.

## Basic home page view
![image](https://user-images.githubusercontent.com/102281970/187746853-bb567e97-c9f0-4357-ae29-1c23fac33200.png)

## User login page
![image](https://user-images.githubusercontent.com/102281970/187748375-452d7735-44bb-448e-9712-015588864d93.png)

## User registration page
![image](https://user-images.githubusercontent.com/102281970/187750228-03bd970f-8c93-47d4-9985-40525b77cec5.png)

The user has the option of selecitng a club, if they are the representative of one of the clubs in the dropdown list.

## Current films page
![image](https://user-images.githubusercontent.com/102281970/187749581-e643ab61-b186-435b-8eb9-112d312fffe9.png)

## Cinema manager account home page
![image](https://user-images.githubusercontent.com/102281970/187749677-31c8a5a2-dca6-4691-ba75-f99c73fe41a1.png)

### Cinema manager account functionality
The cinema manager, as displayed in the above image, is able to create and edit club details for different film clubs.
They are also able to create, edit and delete different showings, and assign seats and screens for the showings.

### Cinema manager user registration approval
The account manager is also able to approve or reject a user's registration.
When a user creates an account, their login will be prevented until approved by the cinema manager.

![image](https://user-images.githubusercontent.com/102281970/187754615-1bd8d029-caf1-4d9b-84fa-b9c37e92b159.png)

As shown above, the cinema manager is shown the username of the pending applications, and an accept or reject button.

![image](https://user-images.githubusercontent.com/102281970/187763516-2b4d7b06-51a5-414b-81a0-5cce251b73be.png)

The cinema manager can view their details by clicking on the name, and then go back to either approve or reject the request.

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

## Booking tickets
By selecting a showing for a certain movie, tickets can be booked.

![image](https://user-images.githubusercontent.com/102281970/187767853-0e395fcc-30ad-4117-9ba3-30551283323d.png)

The above screenshow shows the highlighted unavailable spaces in red, and the highlighted selected space in green.

![image](https://user-images.githubusercontent.com/102281970/187768009-e618f220-5a0e-4b63-91af-9ca9236e071b.png)

The booking is then paid for (with credits if registered user, otherwise a normal user will be taken to a card payment form)

![image](https://user-images.githubusercontent.com/102281970/187770961-480aaa2b-0316-427b-a27a-daf9f877eabf.png)

Above is the interactive payment form (credits in source code) that non registered users will pay with, or registered users will use to purchase credits

## Booking Cancellation
![image](https://user-images.githubusercontent.com/102281970/187766517-78b9bdf6-9543-4374-aa0b-605a7a5d40a9.png)

Users can have their bookings cancelled by entering their booking ID into the text area and submit a cancellation.

## Staff Features

### Creating Clubs
The Cinema Manager can create a club through the taskbar at the top of their page. Editing and deleting clubs is also available through this page.

### Financial Reports
The Account Manager can access the transactions page, which allows them to filter by the account that made the purchase, search start date/time, 
and search end date/time. A summation of the transaction totals can be found at the bottom of the page.

### Account Application Approval/Denial
The Cinema Manager can approve/deny account creation requests through a tab on their page.

