from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.contrib import messages
import traceback


# -------------------- INDEX PAGE FORM -------------------- #
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
            # -----------------------------
            # 1️⃣ Email to PS Digitise Team
            # -----------------------------
            subject_team = 'ERPNext AI - New Contact Form Submission'
            body_team = f"""
            <html>
              <body style="font-family: Arial, sans-serif; background-color: #f8f9fa; margin: 0; padding: 0;">
                <table role="presentation" style="max-width: 600px; margin: 40px auto; background: #ffffff; border-radius: 8px; overflow: hidden; border: 1px solid #ddd;">
                  <tr>
                    <td style="padding: 30px;">
                      <h2 style="color: #333;">📩 New Contact Form Submission</h2>
                      <p style="color: #555; font-size: 15px;">You have received a new inquiry through the website form:</p>
                      <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                      <p style="color: #555; font-size: 15px; line-height: 1.6;">
                        <strong>Name:</strong> {name}<br>
                        <strong>Email:</strong> <a href="mailto:{email}" style="color: #1a73e8;">{email}</a><br>
                        <strong>Phone:</strong> {phone}<br>
                        <strong>Message:</strong> {comment}
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
                ['sales@psdigitise.com']
            )
            email_team.content_subtype = "html"
            email_team.send()

            # -----------------------------
            # 2️⃣ Confirmation Email to User
            # -----------------------------
            subject_user = 'ERPNext AI - Thank You for Contacting Us'
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
                        <strong>Message:</strong> {comment}
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

            messages.success(request, '✅ Your message has been sent successfully!')
            return redirect('index')

        except Exception as e:
            messages.error(request, f'❌ Email sending failed: {str(e)}')
            print(traceback.format_exc())
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
            messages.error(request, '⚠️ Please fill out all fields.')
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
                        <strong>Comment:</strong> {comment}
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
                ['sales@psdigitise.com']
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


def buy(request):
    return render(request, 'buy.html')
