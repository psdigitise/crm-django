from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
import traceback

@csrf_protect
def index(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        comment = request.POST.get('comment', '').strip()

        if not all([name, email, phone, comment]):
            messages.error(request, '⚠️ Please fill all fields.')
            return redirect('index')

        try:
            # Email to team
            subject_team = 'ERPNext AI - New Contact Form Submission'
            body_team = f"""
            <h2>New Contact Form Submission</h2>
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Phone:</strong> {phone}</p>
            <p><strong>Message:</strong> {comment}</p>
            """
            email_team = EmailMessage(
                subject_team,
                body_team,
                'info@psdigitise.com',
                ['sales@psdigitise.com']
            )
            email_team.content_subtype = "html"
            email_team.send()

            # Confirmation email to user
            subject_user = 'ERPNext AI - Thank You for Contacting Us'
            body_user = f"""
            <h2>Thank you {name}!</h2>
            <p>We have received your message and will contact you soon.</p>
            <hr>
            <p><strong>Your details:</strong></p>
            <p>Name: {name}<br>Email: {email}<br>Phone: {phone}<br>Message: {comment}</p>
            """
            email_user = EmailMessage(
                subject_user,
                body_user,
                'info@psdigitise.com',
                [email]
            )
            email_user.content_subtype = "html"
            email_user.send()

            # ✅ Success message (shown only once)
            messages.success(request, '✅ Your message has been sent successfully!')
            return redirect('index')

        except Exception as e:
            messages.error(request, f'❌ Email sending failed: {str(e)}')
            print(traceback.format_exc())
            return redirect('index')

    return render(request, 'index.html')




def about_us(request):
    return render(request, 'about-us.html')


def contact_us(request):
    return render(request, 'contact-us.html')


def buy(request):
    return render(request, 'buy.html')
