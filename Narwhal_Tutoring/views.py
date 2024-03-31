from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse
from .models import *
from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib import messages
import json
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
import stripe
from django.views.decorators.csrf import csrf_exempt
import os
from twilio.rest import Client
from django.utils.http import urlencode

stripe.api_key = settings.STRIPE_SECRET_KEY

account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN
client = Client('AC115c8c63c76f01ccb086edd2f0f40002', 'cc0a1a6eb07b0a566b4d35115ceae534')

# Create your views here.
def index(request):
    users = User.objects.all()

    tutors = []

    for user in users:
        check_and_create_details(user)
        if user.details.all()[0].tutor == True:
            tutors.append(user)

    print(tutors)

    for tutor in tutors:
        details = tutor.details.all()[0]
        username = tutor.username
        pfp_url = f"{username}.png"
        print(pfp_url)
        # Check if the image file exists
        pfp_path = finders.find(f'images/{pfp_url}')
        if pfp_path:
            details.pfp_url = pfp_url
        else:
            # Set default pfp_url if the file doesn't exist
            details.pfp_url = 'default.png'
        details.save()

    return render(request, "Narwhal_Tutoring/index.html", {
        "tutors": tutors,
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            
            # Check if 'next' is set to 'register', if yes, redirect to 'index'
            next_url = request.GET.get('next', 'index')
            if next_url == 'register':
                return redirect('index')  # Assuming 'index' is the name or URL of your index page

            try:
                return redirect(next_url)
            except Exception as e:
                print(e)
                return redirect('index')
        else:
            return render(request, "Narwhal_Tutoring/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "Narwhal_Tutoring/login.html")

def logout_view(request):
    logout(request)
    return redirect(request.GET.get('next', 'index'))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        mobile = request.POST.get('mobile')

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "Narwhal_Tutoring/register.html", {
                "message": "Passwords must match."
            })
        
        if User.objects.filter(email=email).exists():
            return render(request, "Narwhal_Tutoring/register.html", {
                "message": "Email address is already taken."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            details = User_details(user=user)

            # Set additional fields
            details.mobile = mobile

            details.save()
            user.save()
        except IntegrityError:
            return render(request, "Narwhal_Tutoring/register.html", {
                "message": "Username already taken."
            })
        login(request, user)

        try:
            message = client.messages.create(
                from_='+14697323760',
                body=f'{username} has just registered for Narwhal Tutoring',
                to='+61421286031'
            )
            print(message.sid)
        except Exception as e:
            print(e)

        try:
            return redirect(request.GET.get('next', 'index'))
        except Exception as e:
            return redirect('index')
    else:
        return render(request, "Narwhal_Tutoring/register.html")
    
def tutor_register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        mobile = request.POST.get('mobile')

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "Narwhal_Tutoring/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            details = User_details(user=user)
            details.mobile = mobile
            details.tutor = True

            pfp_url = f"{username}.png"
            pfp_path = finders.find(f'images/{pfp_url}')
            if pfp_path:
                details.pfp_url = pfp_url
            else:
                details.pfp_url = 'default.png'
            details.save()
            user.save()
        except IntegrityError:
            return render(request, "Narwhal_Tutoring/tutor_register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        try:
            return redirect(request.GET.get('next', 'index'))
        except Exception as e:
            return redirect('index')
    else:
        return render(request, "Narwhal_Tutoring/tutor_register.html")
    
def about(request):
    return render(request, "Narwhal_Tutoring/about.html")

def contact(request):
    return render(request, "Narwhal_Tutoring/contact.html")

def tutors(request):
    users = User.objects.all()

    tutors = []

    for user in users:
        check_and_create_details(user)
        if user.details.all()[0].tutor == True:
            details = user.details.all()[0]
            tutors.append(user)

            if not user.availability.all().exists():
                details.available = False
                details.save()

    primary_school_subjects = Subject.objects.filter(type="Primary School")
    high_school_subjects = Subject.objects.filter(type="High School")
    atar_subjects = Subject.objects.filter(type="ATAR")

    return render(request, "Narwhal_Tutoring/tutors.html", {
        "tutors": tutors,
        "primary_school_subjects": primary_school_subjects,
        "high_school_subjects": high_school_subjects,
        "atar_subjects": atar_subjects
    })

def tos(request):
    return render(request, "Narwhal_Tutoring/tos.html")

@login_required(login_url='login')
def dashboard(request):
    subjects = Subject.objects.all()
    user = request.user
    check_and_create_details(user)
    details = user.details.all()[0]

    try:
        availability = user.availability
    except Availability.DoesNotExist:
        availability = Availability(tutor=user)
        availability.save()

    if request.method == 'POST':
        # Extract form data from request.POST
        username = request.POST.get('username')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')

        # Common fields for both tutor and non-tutor users
        user.username = username
        user.email = email
        details.mobile = mobile

        if details.tutor:
            # Tutor-specific fields
            atar = request.POST.get('atar')
            suburb = request.POST.get('suburb')
            selected_subject_ids = request.POST.getlist('subjects')
            description = request.POST.get('description')
            university = request.POST.get('university')
            degree = request.POST.get('degree')

            details.atar = atar
            details.suburb = suburb
            details.subjects.set(selected_subject_ids)
            details.description = description
            details.university = university
            details.degree = degree
        else:
            # Non-tutor-specific fields
            address = request.POST.get('address')
            student1_name = request.POST.get('student1_name')
            student2_name = request.POST.get('student2_name')
            student3_name = request.POST.get('student3_name')

            details.address = address
            details.student1_name = student1_name
            details.student2_name = student2_name
            details.student3_name = student3_name

        # Save the user instance
        try:
            user.save()
            details.save()
            messages.success(request, 'Profile information updated successfully.')
        except IntegrityError:
            messages.error(request, 'Username already taken.', extra_tags='danger')

        return HttpResponseRedirect(reverse("dashboard"))  # Redirect to the dashboard after successful submission

    if details.tutor or user.username == 'admin':
        tutors = User.objects.all()
        weeks = []
        payslips = []

        start_date = datetime(2024, 1, 1)
        end_date = datetime.now()
        current_date = start_date

        while current_date.weekday() != 0:  # Monday has index 0
            current_date += timedelta(days=1)

        while current_date <= end_date:
            week_start = make_aware(current_date)
            week_end = make_aware(current_date + timedelta(days=6))
            weeks.append({"start_time": week_start, "end_time": week_end})
            current_date += timedelta(weeks=1)

        for week in weeks:
            payslip = {
                "start_date": week["start_time"].strftime('%d/%m/%y'),
                "end_date": week["end_time"].strftime('%d/%m/%y'),
                "tutors": [],
            }

            for tutor in tutors:
                if user.username=='admin' or user==tutor:
                    total = 0.0
                    tutor_table = {
                        "tutor": tutor.username,
                        "sessions": [],
                        "total": "",
                    }

                    for lesson in tutor.lessons.all():
                        # Checks if lesson is in week
                        if week["start_time"] <= lesson.start_time < week["end_time"] and lesson.cart.paid:
                            # Finds length of lesson in hours
                            hours = (lesson.end_time - lesson.start_time).seconds / 3600
                            payment = 45 * hours

                            session = {
                                "date": lesson.start_time.strftime('%d/%m'),
                                "time": lesson.start_time.strftime('%H:%M'),
                                "hours": hours,
                                "client": lesson.cart.user,
                                "tutor_payment": f"${payment:.2f}",
                            }

                            total += payment
                            tutor_table["sessions"].append(session)
                    tutor_table['total'] = f"${total:.2f}"
                    payslip['tutors'].append(tutor_table)
            payslips.append(payslip)
    else:
        payslips = 0

    return render(request, "Narwhal_Tutoring/dashboard.html", {
        "subjects": subjects,
        "user": user,
        "payslips": payslips,
    })
    
def tutor(request, tutor_id):
    try:
        tutor = User.objects.get(id=tutor_id)
        product = Product.objects.get(name="Test Product")
        prices = Price.objects.filter(product=product)

        if request.user.is_authenticated:
            discount = not request.user.details.all()[0].claimed_discount
        else:
            discount = True
        
        context = {
            "product": product,
            "prices": prices,
            "tutor": tutor,
            "discount": discount,
        }

        check_and_create_details(tutor)
        if tutor.details.all()[0].tutor == False:
            return render(request, "Narwhal_Tutoring/tutor_not_found.html")

        return render(request, "Narwhal_Tutoring/tutor.html", context) 
    except Exception as e:
        messages.error(request, f'{e}', extra_tags='danger')
        return render(request, "Narwhal_Tutoring/tutor.html")
    
def select_lesson_times(request, tutor_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('register'))
    
    try:
        tutor = User.objects.get(id=tutor_id)
        product = Product.objects.get(name="Test Product")
        prices = Price.objects.filter(product=product)
        
        discount = not request.user.details.all()[0].claimed_discount
        
        context = {
            "product": product,
            "prices": prices,
            "tutor": tutor,
            "discount": discount,
        }

        return render(request, "Narwhal_Tutoring/select_lesson_times.html", context)
    except Exception as e:
        messages.error(request, f'{e}', extra_tags='danger')
        return render(request, "Narwhal_Tutoring/select_lesson_times.html")

def save_availability(request):
    if request.method == 'POST':
        print("Posted")
        try:
            data = json.loads(request.body)
            
            # Extracting data from the request
            title = data.get('title', 'Availability')  # Default title if not provided
            start_time = data.get('startTime')
            end_time = data.get('endTime')
            day_of_week = data.get('daysOfWeek', [])[0]  # Assuming daysOfWeek is an array
            group_id = data.get('groupId', '0')  # Default group_id if not provided
            event_id = data.get('id', '0')
            
            tutor = request.user

            print('startTime:')
            print(data.get('startTime'))

            # Create and save the Availability instance
            Availability.objects.create(
                tutor=tutor,
                title=title,
                start_time=start_time,
                end_time=end_time,
                group_id=group_id,
                event_id=event_id,
                day_of_week=day_of_week,
            )

            print(f'Start Time: {start_time}')
            print(f'End Time: {end_time}')
            
            return JsonResponse({'message': 'Event saved successfully'}, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=500)

def delete_availability(request, event_id):
    if request.method == 'DELETE':
        try:
            availability = Availability.objects.get(event_id=event_id)

            # Check if the tutor deleting the availability is the owner of the availability
            if availability.tutor == request.user:
                availability.delete()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
        except Availability.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Availability not found'}, status=404)

def get_availability(request, tutor_id):
    if request.method == 'GET':
        tutor = User.objects.get(id=tutor_id)

        # Fetch availability events for the tutor
        availability_events = Availability.objects.filter(tutor=tutor)

        # Convert events to a format suitable for FullCalendar
        events = []
        for availability in availability_events:

            
            events.append({
                'id': availability.event_id,
                'title': availability.title,
                'startTime': availability.start_time,
                'endTime': availability.end_time, 
                'groupId': availability.group_id,
                'daysOfWeek': [availability.day_of_week],
            })

        return JsonResponse(events, safe=False)
    
def get_client_calendar(request):
    if request.method == 'GET':
        user = request.user

        # Fetch events for the tutor
        carts = user.carts.all()

        # Convert events to a format suitable for FullCalendar
        events = []

        for cart in carts:
            for lesson in cart.lessons.all():
                events.append({
                    'id': lesson.event_id,
                    'title': lesson.tutor.username,
                    'groupId': 'booked',
                    'start': lesson.start_time,
                    'end': lesson.end_time, 
                })

        return JsonResponse(events, safe=False)


def get_calendar(request, tutor_id):
    if request.method == 'GET':
        tutor = User.objects.get(id=tutor_id)

        # Fetch events for the tutor
        availability_events = Availability.objects.filter(tutor=tutor)
        lesson_events = tutor.lessons.all()

        # Convert events to a format suitable for FullCalendar
        events = []
        for availability in availability_events:
            events.append({
                'id': availability.event_id,
                'title': availability.title,
                'startTime': availability.start_time,
                'endTime': availability.end_time, 
                'groupId': availability.group_id,
                'daysOfWeek': [availability.day_of_week],
                'display': 'background'
            })

        for lesson in lesson_events:
            if lesson.cart.paid == True:
                events.append({
                    'id': lesson.event_id,
                    'title': 'Booked',
                    'groupId': 'booked',
                    'start': lesson.start_time,
                    'end': lesson.end_time, 
                    'backgroundColor': 'red',
                })

        return JsonResponse(events, safe=False)

def get_availability_and_lessons(request, tutor_id):
    print("Getting availabilities and lessons.")
    if request.method == 'GET':
        tutor = User.objects.get(id=tutor_id)

        # Fetch events for the tutor
        availability_events = Availability.objects.filter(tutor=tutor)
        lesson_events = tutor.lessons.all()

        # Convert events to a format suitable for FullCalendar
        events = []
        for availability in availability_events:
            events.append({
                'id': availability.event_id,
                'title': availability.title,
                'startTime': availability.start_time,
                'endTime': availability.end_time, 
                'groupId': availability.group_id,
                'daysOfWeek': [availability.day_of_week],
                'display': 'background'
            })

        for lesson in lesson_events:
            if lesson.cart.paid == True:
                events.append({
                    'id': lesson.event_id,
                    'title': lesson.cart.user.username,
                    'start': lesson.start_time,
                    'end': lesson.end_time, 
                })

        return JsonResponse(events, safe=False)

def update_availability(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(data.get('available', False))
            available = data.get('available', False)


            # Update the user's availability (replace this with your actual logic)
            details = request.user.details.all()[0]
            details.available = available
            details.save()

            print("WHAAAHAAA")

            return JsonResponse({'message': 'Availability updated successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
def create_checkout_session(request):
    user = request.user
    try:
        # Try to get the single cart associated with the user
        cart_instance = user.carts.get(processed=False)
        # Now, cart_instance holds the single Cart instance
    except Cart.DoesNotExist:
        # Handle the case where no cart is found
        print("No cart found for this user.")
    except Cart.MultipleObjectsReturned:
        # Handle the case where multiple carts are found (unexpected)
        print("Multiple carts found for this user. Investigate the data.")

    lessons = cart_instance.lessons.all()
    total_duration = sum((lesson.end_time - lesson.start_time).total_seconds() / 3600 for lesson in lessons)
    

    if total_duration < 5:
        price = Price.objects.get(price=3500)
    elif total_duration < 10:
        price = Price.objects.get(price=3150)
    else:
        price = Price.objects.get(price=3000)
    
    quantity = int(total_duration/0.5)

    if settings.DEBUG:
        domain = "http://" + request.get_host()
    else:
        domain = "https://" + request.get_host()

    # Check if the user has claimed the discount
    discounts = []
    if not user.details.all()[0].claimed_discount:
        # Include the discount if the user hasn't claimed it
        discounts.append({
            'coupon': 'SGOPKJwB'
        })

    # Setting up success url
    # Your payment logic here
    payment_success = True  # Set this based on the success of the payment process

    # Encode the boolean value into a URL parameter
    params = urlencode({'payment_success': payment_success})

    # Get the success URL with cart_instance.id
    success_url = reverse('success_view_name', args=[cart_instance.id])

    # Append the URL parameter to the success URL
    success_url_with_params = success_url + '?' + params
    
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price': price.stripe_price_id,
                'quantity': quantity,
            },
        ],
        discounts=discounts,
        #allow_promotion_codes=True,
        mode='payment',
        success_url = success_url_with_params,
        cancel_url=domain,
    )

    # Add a success message if needed
    messages.success(request, "Checkout session created successfully.")

    return redirect(checkout_session.url)

@login_required(login_url='login')
def success(request, cart_id):
    try:
        cart = Cart.objects.get(id=cart_id)
    except Exception as e:
        print(e)
        return HttpResponseRedirect(reverse('index'))

    if cart.user != request.user:
        print("Error: cart user isn't request user")
        return HttpResponseRedirect(reverse('index'))
    
    tutor = cart.lessons.all()[0].tutor

    if cart.paid:
        print("Error: cart already paid for")
        message1 = None
    else:
        payment_success = request.GET.get('payment_success', False)
        if payment_success:
            cart.paid = True
            cart.save()
            message1 = "Your payment has been successful!"
        else:
            message1 = "Your booking has been successful!"
        
        # Creating international phone number
        user = request.user
        mobile = tutor.details.all()[0].mobile
        # Check if the mobile number is already in international format
        if mobile.startswith('+61'):
            tutor_international_format = mobile
        else:
            tutor_international_format = '+61' + mobile[1:]  # Assuming the mobile number is in a format like 0412345678, needs improvement later

        print(tutor_international_format)


        # Creating the message
        details = user.details.all()[0]
        user_email = user.email if user.email else "N/A"
        user_mobile = details.mobile if details else "N/A"
        user_address = details.address if details else "N/A"
        lessons_info = "\n".join([f"{lesson.start_time.strftime('%Y-%m-%d')}: {lesson.start_time.strftime('%H:%M')} - {lesson.end_time.strftime('%H:%M')}" for lesson in cart.lessons.all()])
        message = f"{user} has booked the following lessons with {tutor}:\n{lessons_info}\n\nUser Details:\nEmail: {user_email}\nMobile: {user_mobile}\nAddress: {user_address}"
        
        # Same thing for clients
        if user_mobile.startswith('+61'):
            client_international_format = mobile
        else:
            client_international_format = '+61' + mobile[1:]  # Assuming the mobile number is in a format like 0412345678, needs improvement later

        print(client_international_format)

        try:
            message = client.messages.create(
                from_='+14697323760',
                body=message,
                to=tutor_international_format
            )
            print(message)
        except Exception as e: 
            print(e)

        try:
            message = client.messages.create(
                from_='+14697323760',
                body=message,
                to=client_international_format
            )
            print(message)
        except Exception as e: 
            print(e)

        #Noting that a purchase has been made with a discount.
         
        details = user.details.all()[0]
        details.claimed_discount = True
        details.save()

    return render(request, 'Narwhal_Tutoring/success.html', {
        "tutor": tutor,
        "message": message1,
    })

def cancel(request):
    return render(request, 'Narwhal_Tutoring/cancel.html')

def save_lessons_to_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        lessons_data = data.get('lessons_data', [])

        tutor_id = data.get('tutorId')
        tutor = User.objects.get(id=tutor_id)

        user = request.user
        Cart.objects.filter(user=user, processed=False).delete()
        cart = Cart.objects.create(user=user, tutor=tutor, processed=True, paid=False)

        for lesson_data in lessons_data:
            if lesson_data.get('title') != 'Availability' and lesson_data.get('title') != "Booked":
                Lesson.objects.create(
                    cart=cart,
                    tutor=tutor,
                    name=lesson_data.get('title', 'Lesson'),
                    start_time=lesson_data.get('start'),
                    end_time=lesson_data.get('end'),
                    event_id=lesson_data.get('id', 0)
                )
        lessons = Lesson.objects.filter(tutor=tutor)
        print("Save completed: ")
        print(lessons)

        return JsonResponse({'message': 'Lessons saved to cart successfully'})
    else:
        return JsonResponse({'error': 'Invalid request method'})

def check_and_create_details(tutor):
    try:
        # Assuming 'tutor' is the User instance representing the tutor
        # Check if the tutor already has details
        if not tutor.details.all().exists():
            # No details found, create a new details instance
            new_details = User_details(user=tutor)
            new_details.save()
            print(f"Details created for the tutor {tutor.username}.")

    except User.DoesNotExist:
        print(f"Tutor does not exist.")