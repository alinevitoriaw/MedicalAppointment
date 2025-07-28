from django.db import models
from django.contrib.auth.models import User

STATUS_CHOICES = (
    ('Pendente', 'Pendente'),
    ('Confirmado', 'Confirmado'),
)

class Department(models.Model):
  dep_name = models.CharField(max_length= 100,blank=True)
  dep_desc = models.TextField(blank=True)
  dep_image = models.ImageField(upload_to='dep',null=True)
  
  def __str__(self):
    return self.dep_name
    
class Doctor(models.Model):
  doc_name = models.CharField(max_length=100,blank=True)
  doc_spec = models.CharField(max_length=100, blank=True)
  doc_phone = models.CharField(max_length=10,blank=True)
  doc_email = models.EmailField(blank=True)
  dep_name = models.ForeignKey(Department,on_delete= models.CASCADE,null=True)
  doc_image = models.ImageField(upload_to='doctors',null=True)
  
  def __str__(self):
    return 'Dr.'+self.doc_name+'-('+self.doc_spec+')'

class Booking(models.Model):
  p_name = models.CharField(max_length=100,blank=True)
  user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
  p_phone = models.CharField(max_length=10,blank = True)
  p_email = models.EmailField()
  doc_name = models.ForeignKey(Doctor, on_delete = models.CASCADE)
  booking_date = models.DateField(null=True)
  booking_time = models.TimeField(null=True)
  booked_on = models.DateField(auto_now = True)
  status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pendente')
  
  def __str__(self):
    return self.p_name
