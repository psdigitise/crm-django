from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import EmailMessage


from django.core.mail import EmailMessage
from django.shortcuts import render
import traceback
@csrf_protect
def index(request):
 
 
    if request.method == 'POST':
        # Get form values
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        comment = request.POST.get('comment', '').strip()

        # Simple validation
        if not all([name, email, phone, comment]):
            return render(request, 'index.html', {
                'error': 'Please fill all fields.',
                'name': name,
                'email': email,
                'phone': phone,
                'comment': comment
            })

        try:
            # 1️⃣ Email to your team
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
                ['sales@psdigitise.com']  # team email
            )
            email_team.content_subtype = "html"
            email_team.send()

            # 2️⃣ Confirmation to user
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

            return render(request, 'index.html', {
                # 'success': '✅ Your message has been sent successfully!'
            })

        except Exception as e:
            # Log the full traceback
            error_details = traceback.format_exc()
            print(f"Email sending failed: {str(e)}")
            return render(request, 'index.html', {
                'error': f'Email sending failed: {str(e)}',
                'traceback': error_details,
                'name': name,
                'email': email,
                'phone': phone,
                'comment': comment
            })

    # For GET request
    return render(request, 'index.html')





def about_us(request):
    return render(request, 'about-us.html')


def contact_us(request):
    return render(request, 'contact-us.html')


def buy(request):
    return render(request, 'buy.html')
