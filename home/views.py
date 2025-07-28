from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import CreateUserForm, Bookingform
from .models import *
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.views.decorators.cache import never_cache


def register(request ):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                
                subject = 'MEDICAL APPOINTMENT ACCOUNT REGISTRATION'
                message = 'Account Register Confirmation'
                recipient = form.cleaned_data.get('email')
                context = {
                    'user': user
                }
                card_html = render_to_string('registeremail.html', context)
                
                try:
                    email = EmailMultiAlternatives(subject, message, settings.EMAIL_HOST_USER, [recipient])
                    email.attach_alternative(card_html, 'text/html')
                    email.send(fail_silently=False)
                except Exception as e:
                    messages.warning(request, f"Conta criada, mas o e-mail de confirmação falhou: {e}")

                messages.success(request, 'Account created for ' + user)
                return redirect('login')
            else:
                for error in form.errors.values():
                    messages.error(request, error)

        context = {'form': form}
        return render(request, 'register.html', context)


def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid Credentials')
                return render(request, 'login.html')

    context = {}
    return render(request, 'login.html', context)


def logout_user(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def index(request):
    dict_dept = {
        'dept': Department.objects.all()
    }
    return render(request, 'home.html', dict_dept)


@login_required(login_url='login')
def about(request):
    return render(request, 'about.html')


@login_required(login_url='login')
def booking(request):
    if request.method == 'POST':
        form = Bookingform(request.POST)
        
        if form.is_valid():
            booking_instance = form.save(commit=False)
            booking_instance.user = request.user
            booking_instance.save()

            messages.success(request, 'Sua consulta foi submetida com sucesso!')

            # Lógica de envio de e-mail (opcional)
            try:
                context = {
                   'patient': form.cleaned_data.get('p_name'),
                   'booking_time': form.cleaned_data.get('booking_time'),
                   'booking_date': form.cleaned_data.get('booking_date'),
                   'doctor': form.cleaned_data.get('doc_name')
                }
                card_html = render_to_string('emailsend.html', context)
                subject = 'MEDICAL APPOINTMENT'
                message = 'Medical Appointment confirmation'
                recipient = form.cleaned_data.get('p_email')
                email = EmailMultiAlternatives(subject, message, settings.EMAIL_HOST_USER, [recipient])
                email.attach_alternative(card_html, 'text/html')
                email.send(fail_silently=False)
            except Exception as e:
                messages.warning(request, f"Agendamento salvo, mas houve um erro ao enviar o e-mail de confirmação: {e}")

            # Redireciona para a página "Meus Agendamentos"
            return redirect('myappointment')
        
    else:
        form = Bookingform()

    context = {'form': form}
    return render(request, 'booking.html', context)


@login_required(login_url='login')
def contact(request):
    return render(request, 'contact.html')


@login_required(login_url='login')
def delete(request, pk):
    instance = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        instance.delete()
        messages.success(request, f"Agendamento de {instance.p_name} foi deletado.")
    return redirect('appointment')


@login_required(login_url='login')
@never_cache
def deletee(request, pk):
    instance = get_object_or_404(Booking, pk=pk, user=request.user)
    instance.delete()
    messages.success(request, "Seu agendamento foi cancelado.")
    return redirect('myappointment')


def is_admin(user):
    return user.is_staff


@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def appointments(request):
    dict_book = {
        'booking': Booking.objects.all().order_by('-booking_date', '-booking_time')
    }
    return render(request, 'appointments.html', dict_book)


@login_required(login_url='login')
def doctors(request):
    dict_dept = {
        'dept': Doctor.objects.all()
    }
    return render(request, 'doctors.html', dict_dept)


@login_required(login_url='login')
def myappointments(request):
    user_bookings = Booking.objects.filter(user=request.user).order_by('-booking_date', '-booking_time')
    return render(request, 'myappointments.html', {'bookings': user_bookings})


@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def confirm_booking(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id)
        booking.status = 'Confirmado'
        booking.save()
        messages.success(request, f"Agendamento de {booking.p_name} confirmado com sucesso!")
    return redirect('appointment')
