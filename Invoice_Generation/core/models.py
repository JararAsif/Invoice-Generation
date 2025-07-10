from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin,Permission
from decimal import Decimal
from django.utils import timezone

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, name, role, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        role = extra_fields.pop('role', 'admin') 
    
        return self.create_user(email=email, name=name, role=role, password=password, **extra_fields)



class User(AbstractBaseUser,PermissionsMixin):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('client', 'Client'),
    )

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects=UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    

    def __str__(self):
        return self.name



#Product table
class product(models.Model):
    name=models.CharField(max_length=100,unique=True)
    description=models.TextField(blank=True,null=True)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    quantity=models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"name: {self.name}  price: {self.price} quantity: {self.quantity}"
    


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('PAID', 'Paid'),
        ('UNPAID', 'Unpaid'),
        ('OVERDUE', 'Overdue'),
    ]
        
    client = models.ForeignKey(User,on_delete=models.CASCADE)
    date_create=models.DateField(default=timezone.now,null=True)
    due_date=models.DateField()
    status=models.CharField(max_length=12,choices=STATUS_CHOICES,default='UNPAID')

    def __str__(self):
        return f"Invoice #{self.id} for {self.client}"
    
    @property
    def subtotal(self):
            send=sum(item.total_price() for item in self.invoices.all())
            if send>0:
                return send.quantize(Decimal('0.01' ))
            else:
                return send
    
    @property
    def tax(self):
        
        return self.subtotal*Decimal(0.17).quantize(Decimal('0.01'))
    @property
    def total(self):
        return self.subtotal+self.tax.quantize(Decimal('0.01'))
    

class InvoiceItem(models.Model):

    product=models.ForeignKey(product,on_delete=models.CASCADE,related_name='items')
    invoice= models.ForeignKey(Invoice,on_delete=models.CASCADE,related_name='invoices')
    quantity=models.PositiveIntegerField()
    unit_price=models.DecimalField(max_digits=10,decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} on Invoice #{self.invoice.id}"
    
    def total_price(self):
        return self.quantity*self.unit_price
    

    





