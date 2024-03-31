from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model  # Import the get_user_model function

class Subject(models.Model):
    name = models.CharField(max_length=100)
    # Either Primary School, Highschool, or ATAR
    type = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.type} {self.name}"
    
User = get_user_model()  # Retrieve the User model

class User_details(models.Model):
    user = models.ForeignKey(User, related_name="details", on_delete=models.CASCADE)
    student1_name = models.CharField(max_length=255, null=True, blank=True)
    student2_name = models.CharField(max_length=255, null=True, blank=True)
    student3_name = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    claimed_discount = models.BooleanField(default=False)

    tutor = models.BooleanField(default=False)

    # Tutors Only
    mobile = models.CharField(max_length=15, null=True, blank=True)
    suburb = models.CharField(max_length=127, null=True, blank=True)
    subjects = models.ManyToManyField(Subject, related_name="tutors", blank=True)
    atar = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    description = models.TextField(max_length=1000, blank=True)
    university = models.CharField(max_length=255, null=True, blank=True)
    degree = models.CharField(max_length=255, null=True, blank=True)
    available = models.BooleanField(default=True, blank=True)
    pfp_url = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.user}'s details"

class Availability(models.Model):
    tutor = models.ForeignKey(User, related_name="availability", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    group_id = models.CharField(max_length=255)
    start_time = models.CharField(max_length=20)  # Adjust the max length as needed
    end_time = models.CharField(max_length=20)    # Adjust the max length as needed
    event_id = models.CharField(max_length=255)
    day_of_week = models.IntegerField()

    def __str__(self):
        return f"{self.tutor} - {self.start_time}"
    
class Product(models.Model):
    name = models.CharField(max_length=100)
    stripe_product_id = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
 
class Price(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="prices")
    stripe_price_id = models.CharField(max_length=100)
    price = models.IntegerField(default=0)  # cents
    
    def get_display_price(self):
        return "{0:.2f}".format(self.price / 100)
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    paid = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)

    def __str__(self):
        if self.paid:
            return f"PAID - {self.user} - Tutor: {self.tutor}"
        elif self.processed:
            return f"PROCESSED - {self.user} - Tutor: {self.tutor}"
        else:
            return f"INACTIVE - {self.user} - Tutor: {self.tutor}"


class Lesson(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="lessons")
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lessons')
    name = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    event_id = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}: {self.start_time} - {self.end_time}"