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
from django.shortcuts import redirect
from django.core.mail import EmailMessage
# import time


# from captcha.image import ImageCaptcha
# from django.http import HttpResponse
# import random, string

# def generate_captcha(request):
#     captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
#     request.session['captcha_text'] = captcha_text

#     image = ImageCaptcha()
#     data = image.generate(captcha_text)
#     return HttpResponse(data, content_type='image/png')


import requests
from django.shortcuts import render
from django.http import JsonResponse

def subscription_form(request):
    if request.method == "GET":
        return render(request, "payment_form.html")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        company = request.POST.get("company", "").strip()

        if not all([name, email, phone, company]):
            return JsonResponse({"status": "error", "message": "All fields required"}, status=400)

        url = "https://api.erpnext.ai/api/v2/document/On Request Form"

        payload = {
            "name1": name,
            "email": email,
            "phone_number": phone,
            "company": company
        }

        headers = {
            "Authorization": "token 33c44b17631ceb3:2d01782c6c01a7f",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)

            # ✅ SEND EMAIL ONLY IF REQUEST IS SUCCESSFUL
            if response.status_code in [200, 201]:

                subject = "Thank you for contacting us"
                body = f"""
                <html>
                  <body style="font-family: Arial, sans-serif; background:#f6f6f6; margin:0; padding:0;">
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                      <tr>
                        <td align="center" style="padding:40px 10px;">
                          <table width="600" style="background:#ffffff; border-radius:10px; overflow:hidden; border:1px solid #ddd;">
                            <tr>
                              <td style="padding:30px;">
                                <h2 style="color:#333;">Thank you for your interest in our Enterprise Plan, {name}.</h2>
                                <p style="color:#555;">
                                    We have received your request for a custom subscription plan.
                                    Our team will review your requirements and get in touch with you shortly.
                                </p>
                                <hr style="border:none; border-top:1px solid #eee; margin:20px 0;">
                                <h3 style="color:#333;">Submitted Details:</h3>
                                <p style="color:#555; line-height:1.6;">
                                  <strong>Name:</strong> {name}<br>
                                  <strong>Email:</strong> <a href="mailto:{email}" style="color:#1a73e8;">{email}</a><br>
                                  <strong>Phone:</strong> {phone}<br>
                                  <strong>Comment:</strong> {company}
                                </p>
                              </td>
                            </tr>
                            <tr>
                              <td style="background:#f9f4e8; text-align:center; padding:12px; font-size:13px; color:#777;">
                                © ERPNext AI 2025
                              </td>
                            </tr>
                          </table>
                        </td>
                      </tr>
                    </table>
                  </body>
                </html>
                """

                email_user = EmailMessage(
                    subject,
                    body,
                    "sales@erpnext.ai",
                    [email]
                )
                email_user.content_subtype = "html"
                email_user.send()

            return redirect("/subscribe")

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    if request.method == "GET":
        return render(request, "payment_form.html")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        company = request.POST.get("company", "").strip()

        if not all([name, email, phone, company]):
            return JsonResponse({"status": "error", "message": "All fields required"}, status=400)

        url = "https://api.erpnext.ai/api/v2/document/On Request Form"

        payload = {
            "name1": name,
            "email": email,
            "phone_number": phone,
            "company": company
        }

        headers = {
            "Authorization": "token 33c44b17631ceb3:2d01782c6c01a7f",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            return redirect("/subscribe")

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)



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
                # 'redirect': 'https://crm.erpnext.ai/app/'
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
    if plan == "Free CRM":
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

    if not order_id and plan !="Free CRM":
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
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.core.mail import EmailMessage
import requests, traceback

@csrf_protect
def index(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('fullnum', '').strip()
        comment = request.POST.get('comment', '').strip()  # Used as Company Name

        if not all([name, email, phone, comment]):
            return JsonResponse({"status": "error", "message": "⚠️ Please fill all fields."})

        try:
            # -----------------------------
            # 1️⃣ Email to PS Digitise Team
            # -----------------------------
            subject_team = 'ERPNext AI - New Contact Form Submission'
            body_team = f"""
            <html><body>
                <h2>📩 New Contact Form Submission</h2>
                <p><strong>Name:</strong> {name}<br>
                   <strong>Email:</strong> {email}<br>
                   <strong>Phone:</strong> {phone}<br>
                   <strong>Message:</strong> {comment}</p>
            </body></html>
            """

            email_team = EmailMessage(
                subject_team, body_team,
                'sales@erpnext.ai', ['sales@psdigitise.com']
            )
            email_team.content_subtype = "html"

            # -----------------------------
            # 2️⃣ Confirmation Email to User
            # -----------------------------
            subject_user = 'ERPNext AI - Thank You for Contacting Us'
            body_user = f"""
            <html><body>
                <h2>Thank you for contacting us, {name}.</h2>
                <p>We have received your message and will get in touch with you shortly.</p>
                <p><strong>Name:</strong> {name}<br>
                   <strong>Email:</strong> {email}<br>
                   <strong>Phone:</strong> {phone}<br>
                   <strong>Message:</strong> {comment}</p>
            </body></html>
            """
            

            email_user = EmailMessage(
                subject_user, body_user,
                'sales@erpnext.ai', [email]
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
                return JsonResponse({"status": "company_exists", "message": "⚠️ This Company already exists!"})

            # -----------------------------
            # 4️⃣ Check if Email already exists
            # -----------------------------
            check_user_url = f"https://api.erpnext.ai/api/v2/document/User/{email}"
            check_user_res = requests.get(check_user_url, headers=headers)

            if check_user_res.status_code == 200:
                return JsonResponse({"status": "email_exists", "message": "⚠️ This Email is already registered!"})

            # -----------------------------
            # 5️⃣ Create Company
            # -----------------------------
            company_payload = {
                "email_id": email,
                "company_name": comment,
                "plan_id": "0",
              
            }

            company_url = "https://api.erpnext.ai/api/v2/document/Company/"
            company_res = requests.post(company_url, json=company_payload, headers=headers)

            if company_res.status_code not in [200, 201]:
                return JsonResponse({"status": "error", "message": "❌ Failed creating Company!"})

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

            user_url = "https://api.erpnext.ai/api/v2/document/User/"
            user_res = requests.post(user_url, json=user_payload, headers=headers)

            if user_res.status_code not in [200, 201]:
                return JsonResponse({"status": "error", "message": "❌ Failed creating User!"})

            # -----------------------------
            # SUCCESS RESPONSE
            # -----------------------------
            email_team.send()
            # email_user.send()
            return JsonResponse({"status": "success", "message": "🎉 Your message has been submitted successfully!"})

        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({"status": "error", "message": f"❌ Failed: {str(e)}"})

    context = {
        "page_title": "ERPNext AI CRM | Lead, Contact & Sales Pipeline Management",
        "meta_description": (
            "Accelerate customer relationship management with AI-enabled ERPNext CRM — "
            "lead capture, deal tracking, email integration, pipeline automation, and smart insights "
            "for growing teams. Start free and close deals faster."
        ),
    }
    return render(request, "index.html", context)



# -------------------- CONTACT US PAGE FORM -------------------- #
@csrf_protect


def contact_us(request):
    if request.method == 'POST':

        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        company = request.POST.get('comment', '').strip()
        message = request.POST.get('message', '').strip()

        contact_type = request.POST.get('contact_type', 'contact')
        support_category = request.POST.get('support_category', '').strip()

        if not all([name, email, phone, company]):
            messages.error(request, 'Please fill out all fields.')
            return redirect('contact_us')

     

        try:
            # ==================================================
            # 1️⃣ INTERNAL TEAM EMAIL
            # ==================================================
            if contact_type == "support":
                subject_team = "New Support Request"
                to_email = ['sales@erpnext.ai']
            else:
                subject_team = "New Contact Form Submission"
                to_email = ['sales@erpnext.ai']

            body_team = f"""
            <html>
              <body style="font-family: Arial, sans-serif;background:#f6f6f6;">
                <table style="max-width:600px;margin:40px auto;background:#fff;border-radius:8px;border:1px solid #ddd;">
                  <tr>
                    <td style="padding:30px;">
                      <h2>{subject_team}</h2>
                      <hr>
                      <p><strong>Name:</strong> {name}</p>
                      <p><strong>Email:</strong> {email}</p>
                      <p><strong>Phone:</strong> {phone}</p>
                      <p><strong>Company:</strong> {company}</p>
                      <p><strong>Request Type:</strong> {contact_type.title()}</p>
                      {f"<p><strong>Support Category:</strong> {support_category.title()}</p>" if contact_type == "support" else ""}
                      <hr>
                      <p><strong>Message:</strong></p>
                      <p style="background:#f9f9f9;padding:12px;border-radius:6px;">
                        {message}
                      </p>
                    </td>
                  </tr>
                </table>
              </body>
            </html>
            """

            email_team = EmailMessage(
                subject_team,
                body_team,
                'sales@erpnext.ai',
                to_email
            )
            email_team.content_subtype = "html"
            email_team.send()

            # ==================================================
            # 2️⃣ USER CONFIRMATION EMAIL (IMAGE-2 STYLE)
            # ==================================================
            subject_user = "ERPNext AI – Thank You for Contacting Us"

            body_user = f"""
            <html>
              <body style="font-family: Arial, sans-serif;background:#f6f6f6;">
                <table style="max-width:600px;margin:40px auto;background:#fff;border-radius:10px;border:1px solid #ddd;">
                  <tr>
                    <td style="padding:30px;">
                      <h2>Thank you, {name}</h2>
                      <p>We have received your message and will get in touch with you shortly.</p>

                      <hr>

                      <h3>Your Submitted Details</h3>

                      <p><strong>Name:</strong> {name}</p>
                      <p><strong>Email:</strong> {email}</p>
                      <p><strong>Phone:</strong> {phone}</p>
                      <p><strong>Company:</strong> {company}</p>
                      <p><strong>Request Type:</strong> {contact_type.title()}</p>
                      {f"<p><strong>Support Category:</strong> {support_category.title()}</p>" if contact_type == "support" else ""}

                      <hr>

                      <p><strong>Message:</strong></p>
                      <p style="background:#f9f9f9;padding:12px;border-radius:6px;">
                        {message}
                      </p>
                    </td>
                  </tr>
                  <tr>
                    <td style="background:#f9f4e8;text-align:center;padding:12px;font-size:13px;">
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
                'sales@erpnext.ai',
                [email]
            )
            email_user.content_subtype = "html"
            email_user.send()

            messages.success(request, ' Mail has been sent successfully!')
            return redirect('contact_us')

        except Exception:
            print(traceback.format_exc())
            messages.error(request, '    Failed to send mail. Please try again.')
            return redirect('contact_us')

    return render(request, 'contact-us.html')


# -------------------- OTHER STATIC PAGES -------------------- #
def about_us(request):
    return render(request, 'about-us.html')


def privacy_policy(request):
    return render(request, "privacy_policy.html")



def data_deletion(request):
    return render(request, "Data_Deletion.html")

def terms_and_conditions(request):
    return render(request, "terms_and_conditions.html")

def security(request):
    return render(request, "Security.html")

def partners(request):
    return render(request, "Partners.html")

@csrf_protect
def pricing(request):
    return render(request, "Pricing.html")

def features(request):
    return render(request, "Features.html")

def cookies(request):
    return render(request, "Cookies.html")

# def my_view(request):
#     context = {
#         "timestamp": int(time.time())
#     }
#     return render(request, "my_template.html", context)