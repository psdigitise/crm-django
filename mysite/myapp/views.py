from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.contrib import messages
import traceback
import razorpay
from django.http import JsonResponse
from django.conf import settings
from .models import Payment
import requests
import traceback


# from captcha.image import ImageCaptcha
# from django.http import HttpResponse
# import random, string

# def generate_captcha(request):
#     captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
#     request.session['captcha_text'] = captcha_text

#     image = ImageCaptcha()
#     data = image.generate(captcha_text)
#     return HttpResponse(data, content_type='image/png')



# -------------------- BUY PAGE -------------------- #
@csrf_exempt
def buy(request):
    """
    Render the buy page with plan, amount, and free/paid handling.
    """

    plan = request.GET.get("plan")
    amount = request.GET.get("amount", "0")

    # Validate plan
    if not plan:
        return render(request, "error.html", {"message": "Missing plan name."})

    # Convert amount safely
    try:
        amount = float(amount)
    except:
        amount = 0

    free = (amount == 0)

    # If FREE plan → do NOT show error.html
    if free:
        return render(request, "buy.html", {
            "plan": plan,
            "amount": 0,
            "free": True,
            "razorpay_key": ""   # No Razorpay needed
        })

    # ---------- PAID PLAN ----------
    return render(request, "buy.html", {
        "plan": plan,
        "amount": int(amount),
        "free": False,
        "razorpay_key": settings.RAZORPAY_KEY_ID
    })


# -------------------- CREATE ORDER -------------------- #
@csrf_exempt
def create_order(request):
    """
    Creates a Razorpay order for paid plans.
    For free plan: saves data directly without Razorpay.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    try:
        amount = float(request.POST.get('amount', 0))
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        plan = request.POST.get('plan', '').strip()

        # Validate mandatory fields
        if not name or not email or not phone:
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        # -------------------------------
        # ✅ FREE PLAN (NO RAZORPAY)
        # -------------------------------
        if amount == 0:
            Payment.objects.create(
                name=name,
                email=email,
                phone=phone,
                plan=plan,
                amount=0,
                order_id="FREE_PLAN",
                status="success"   # direct success
            )

            return JsonResponse({
                'status': 'success',
                'redirect': 'https://crm.erpnext.ai/login/'
            })

        # -------------------------------
        # ✅ PAID PLAN (RAZORPAY)
        # -------------------------------
        if amount <= 0:
            return JsonResponse({'error': 'Invalid amount'}, status=400)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        order_data = {
            'amount': int(amount * 100),
            'currency': 'INR',
            'receipt': f'order_rcpt_{phone}',
            'payment_capture': 1,
        }

        order = client.order.create(order_data)

        Payment.objects.create(
            name=name,
            email=email,
            phone=phone,
            plan=plan,
            amount=amount,
            order_id=order['id'],
            status='created'
        )

        return JsonResponse({
            'order_id': order['id'],
            'amount': order['amount'],
            'currency': order['currency']
        })

    except Exception as e:
        print("❌ Error:", str(e))
        return JsonResponse({'error': 'Internal server error'}, status=500)


# -------------------- SAVE PAYMENT -------------------- #
@csrf_exempt
def save_payment(request):
    """
    Handles both FREE plan and PAID plan payment records.
    
    FREE PLAN:
        - Saves name, email, phone, plan only.
        - Does NOT require order_id or payment_id.
    
    PAID PLAN:
        - Updates existing Payment entry using Razorpay order_id.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    plan = request.POST.get('plan')
    name = request.POST.get('name')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    print( name,email,phone,plan)
    # ---------- FREE PLAN LOGIC ----------
    if plan == "CRM Lite":
        Payment.objects.create(
            name=name,
            email=email,
            phone=phone,
            plan=plan,
            amount=0,
            status="success"
        )
        return JsonResponse({'status': 'free_saved'})

    # ---------- PAID PLAN LOGIC ----------
    order_id = request.POST.get('order_id')
    payment_id = request.POST.get('payment_id', '')
    status = request.POST.get('status', 'failed')

    if not order_id and plan !="Free":
        return JsonResponse({'error': 'Missing order_id for paid plan'}, status=400)

    try:
        payment = Payment.objects.filter(order_id=order_id).first()
        if payment:
            payment.payment_id = payment_id
            payment.status = status
            payment.save()
        else:
            # Fallback case if entry doesn’t exist
            Payment.objects.create(
                order_id=order_id,
                payment_id=payment_id,
                status=status
            )
        return JsonResponse({'status': 'success'})
    except Exception as e:
        print("❌ Error saving payment:", str(e))
        return JsonResponse({'error': str(e)}, status=500)


# -------------------- INDEX PAGE FORM -------------------- #
import requests
import traceback
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def index(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        comment = request.POST.get('comment', '').strip()  # Used as Company Name

        if not all([name, email, phone, comment]):
            messages.error(request, '⚠️ Please fill all fields.')
            return redirect('index')

        try:
            # -----------------------------
            # 1️⃣ Email to PS Digitise Team
            # -----------------------------
            subject_team = 'ERPNext AI - New Contact Form Submission'
            body_team = f"""
            <html>
            <body style="font-family: Arial, sans-serif; background-color: #f8f9fa;">
                <table style="max-width: 600px; margin: 40px auto; background: #ffffff;
                border-radius: 8px; border: 1px solid #ddd;">
                <tr><td style="padding: 30px;">
                    <h2>📩 New Contact Form Submission</h2>
                    <p>You have received a new inquiry through the website form:</p>
                    <hr>
                    <p><strong>Name:</strong> {name}<br>
                       <strong>Email:</strong> {email}<br>
                       <strong>Phone:</strong> {phone}<br>
                       <strong>Message:</strong> {comment}</p>
                </td></tr></table>
            </body></html>
            """

            email_team = EmailMessage(
                subject_team, body_team,
                'info@psdigitise.com', ['sales@psdigitise.com']
            )
            email_team.content_subtype = "html"


            # -----------------------------
            # 2️⃣ Confirmation Email to User
            # -----------------------------
            subject_user = 'ERPNext AI - Thank You for Contacting Us'
            body_user = f"""
            <html><body style="font-family: Arial, sans-serif; background-color: #f6f6f6;">
                <table style="max-width: 600px; margin: 40px auto; background: #ffffff;
                border-radius: 8px; border: 1px solid #ddd;">
                <tr><td style="padding: 30px;">
                    <h2>Thank you for contacting us, {name}.</h2>
                    <p>We have received your message and will get in touch with you shortly.</p>
                    <hr>
                    <p><strong>Name:</strong> {name}<br>
                       <strong>Email:</strong> {email}<br>
                       <strong>Phone:</strong> {phone}<br>
                       <strong>Message:</strong> {comment}</p>
                </td></tr></table>
            </body></html>
            """

            email_user = EmailMessage(
                subject_user, body_user,
                'info@psdigitise.com', [email]
            )
            email_user.content_subtype = "html"


            # -----------------------------
            # API Headers
            # -----------------------------
            headers = {
                "Content-Type": "application/json",
                "Authorization": "token 33c44b17631ceb3:2d01782c6c01a7f"
            }

            # -----------------------------
            # 3️⃣ Check if Company exists
            # -----------------------------
            check_company_url = f"https://api.erpnext.ai/api/v2/document/Company/{comment}"
            check_company_res = requests.get(check_company_url, headers=headers)

            if check_company_res.status_code == 200:
                messages.error(request, "⚠️ This Company already exists!")
                return redirect('index')

            # -----------------------------
            # 4️⃣ Check if Email already exists
            # -----------------------------
            check_user_url = f"https://api.erpnext.ai/api/v2/document/User/{email}"
            check_user_res = requests.get(check_user_url, headers=headers)

            if check_user_res.status_code == 200:
                messages.error(request, "⚠️ This Email is already registered!")
                return redirect('index')

            # -----------------------------
            # 5️⃣ Create Company
            # -----------------------------
            company_payload = {
                "email_id": email,
                "company_name": comment,
                "plan_id": "0"
            }

            company_url = "https://api.erpnext.ai/api/v2/document/Company/"
            company_res = requests.post(company_url, json=company_payload, headers=headers)

            if company_res.status_code not in [200, 201]:
                print("Company API Error:", company_res.text)
                messages.error(request, "❌ Failed creating Company!")
                return redirect('index')

            # -----------------------------
            # 6️⃣ Create User
            # -----------------------------
            user_payload = {
                "email": email,
                "first_name": name,
                "company": comment,
                "role_profile_name": "Only If Create",
                "phone": phone,
                "plan_id": "0"
            }
            print("tyry",user_payload)
            user_url = "https://api.erpnext.ai/api/v2/document/User/"
            user_res = requests.post(user_url, json=user_payload, headers=headers)
            print("tyry",user_res)
            if user_res.status_code not in [200, 201]:
                print("User API Error:", user_res.text)
                messages.error(request, "❌ Failed creating User!")
                return redirect('index')

            # -----------------------------
            # SUCCESS RESPONSE
            # -----------------------------
            email_team.send()
            email_user.send()
            messages.success(request, '🎉 Your message has been submitted successfully!')
            return redirect('index')

        except Exception as e:
            print(traceback.format_exc())
            messages.error(request, f'❌ Failed: {str(e)}')
            return redirect('index')

    return render(request, 'index.html')



# -------------------- CONTACT US PAGE FORM -------------------- #
@csrf_protect


def contact_us(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        service = request.POST.get('service', '').strip()
        comment = request.POST.get('comment', '').strip()

        if not all([name, email, phone, service, comment]):
            messages.error(request, ' Please fill out all fields.')
            return redirect('contact_us')

        try:
            # -----------------------------
            # 1️⃣ Email to PS Digitise Team
            # -----------------------------
            subject_team = f'New Contact Form Submission - {service}'
            body_team = f"""
            <html>
              <body style="font-family: Arial, sans-serif; background-color: #f8f9fa; margin: 0; padding: 0;">
                <table role="presentation" style="max-width: 600px; margin: 40px auto; background: #ffffff; border-radius: 8px; overflow: hidden; border: 1px solid #ddd;">
                  <tr>
                    <td style="padding: 30px;">
                      <h2 style="color: #333;">📩 New Contact Form Submission</h2>
                      <p style="color: #555; font-size: 15px;">You have received a new inquiry through the contact form:</p>
                      <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                      <p style="color: #555; font-size: 15px; line-height: 1.6;">
                        <strong>Name:</strong> {name}<br>
                        <strong>Email:</strong> <a href="mailto:{email}" style="color: #1a73e8;">{email}</a><br>
                        <strong>Phone:</strong> {phone}<br>
                        <strong>Service:</strong> {service}<br>
                        <strong>Company:</strong> {comment}
                      </p>
                    </td>
                  </tr>
                  <tr>
                    <td style="background: #f1f1f1; text-align: center; padding: 12px; font-size: 13px; color: #777;">
                      © PS Digitise 2025 | Internal Notification
                    </td>
                  </tr>
                </table>
              </body>
            </html>
            """

            email_team = EmailMessage(
                subject_team,
                body_team,
                'info@psdigitise.com',
                ['sales@psdigitise.com'],
                    cc=[''] 
            )
            email_team.content_subtype = "html"
            email_team.send()

            # -----------------------------
            # 2️⃣ Confirmation Email to User
            # -----------------------------
            subject_user = "ERPNext AI - Thank You for Contacting Us"
            body_user = f"""
            <html>
              <body style="font-family: Arial, sans-serif; background-color: #f6f6f6; margin: 0; padding: 0;">
                <table role="presentation" style="max-width: 600px; margin: 40px auto; background: #ffffff; border-radius: 8px; overflow: hidden; border: 1px solid #ddd;">
                  <tr>
                    <td style="padding: 30px;">
                      <h2 style="color: #333333; margin-bottom: 10px;">Thank you for contacting us, {name}.</h2>
                      <p style="color: #555555; font-size: 15px;">
                        We have received your message and will get in touch with you shortly.
                      </p>
                      <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                      <h3 style="color: #333333; margin-bottom: 10px;">Your Submitted Details:</h3>
                      <p style="color: #555555; line-height: 1.6; font-size: 15px;">
                        <strong>Name:</strong> {name}<br>
                        <strong>Email:</strong> <a href="mailto:{email}" style="color: #1a73e8; text-decoration: none;">{email}</a><br>
                        <strong>Phone:</strong> {phone}<br>
                        <strong>Service:</strong> {service}<br>
                        <strong>Comment:</strong> {comment}
                      </p>
                    </td>
                  </tr>
                  <tr>
                    <td style="background: #f9f4e8; text-align: center; padding: 12px; font-size: 13px; color: #777;">
                      © ERPNext AI 2025
                    </td>
                  </tr>
                </table>
              </body>
            </html>
            """

            email_user = EmailMessage(
                subject_user,
                body_user,
                'info@psdigitise.com',
                [email]
            )
            email_user.content_subtype = "html"
            email_user.send()

            messages.success(request, '✅ Mail has been sent successfully!')
            return redirect('contact_us')

        except Exception as e:
            messages.error(request, f'❌ Failed to send mail: {str(e)}')
            print(traceback.format_exc())
            return redirect('contact_us')

    return render(request, 'contact-us.html')

# -------------------- OTHER STATIC PAGES -------------------- #
def about_us(request):
    return render(request, 'about-us.html')


def privacy_policy(request):
    return render(request, "privacy_policy.html")



def data_deletion(request):
    return render(request, "Data_Deletion.html")

