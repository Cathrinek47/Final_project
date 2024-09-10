from django.db import models


class Apartment(models.Model):
    CATEGORY_CHOICES = [
        ('Hotel', 'Hotel'),
        ('Room', 'Room'),
        ('Hostel', 'Hostel'),
        ('Suite', 'Suite'),
        ('House', 'House'),
    ]

    title = models.CharField(max_length=100, unique=True, verbose_name="Title")
    description = models.TextField(max_length=255, verbose_name="Description")
    location = models.CharField(max_length=150, verbose_name="Location")
    price = models.DecimalField(max_digits=10, decimal_places=2,verbose_name="Price pro night")
    category = models.CharField(max_length=50, null=True, choices=CATEGORY_CHOICES)
    rooms_amount = models.PositiveIntegerField(verbose_name="Number of rooms")
    created_at = models.DateField(auto_now_add=True)
    # owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='tasks')

    def __str__(self):
        return f': {self.title}'

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Apartment'

