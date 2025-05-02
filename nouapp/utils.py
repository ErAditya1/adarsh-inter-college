from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_registration_success_email(user_email, user_name):
    
    try:
        # Subject and sender details
        subject = 'Welcome to Adarsh Inter College! Your Registration is Successful'
        from_email = settings.EMAIL_HOST_USER
        to = user_email

        # Load the HTML content
        html_content = render_to_string('emails/registration_success_email.html', {'user_name': user_name})
        text_content = strip_tags(html_content)  # Strip the HTML tags for the plain text version

        # Create the email
        email = EmailMultiAlternatives(subject, text_content, from_email, [to])
        email.attach_alternative(html_content, "text/html")  # Attach the HTML version

        print("Sending email to:", to)  # Debugging line to check the recipient's email
        print("Email subject:", subject)  # Debugging line to check the email subject
        # Send the email
        email.send()
        print("✅ Email sent successfully!")
    except Exception as e:
        print("❌ Failed to send email:", e)

def send_admin_registration_confirmation_email(user_email, user_name, username, password):
    try:
        # Subject and sender details
        subject = 'New Registration: Student Successfully Registered!'
        from_email = settings.EMAIL_HOST_USER
        to = user_email

        # Load the HTML content
        context = {
            'user_name': user_name,
            'username': username,
            'password': password,
        }
        html_content = render_to_string('emails/admin_registration_confirmation_email.html', context)
        text_content = strip_tags(html_content)  # Strip the HTML tags for the plain text version

        # Create the email
        email = EmailMultiAlternatives(subject, text_content, from_email, [to])
        email.attach_alternative(html_content, "text/html")  # Attach the HTML version

        # Send the email
        email.send()

        print(f"✅ Email sent to {to}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email to {to}: {e}")
        return False

def send_admin_teacher_registration_email(user_email, user_name, username, password, login_url=None):
    try:
        subject = 'Welcome to Adarsh Inter College – Teacher Registration Successful'
        from_email = settings.EMAIL_HOST_USER
        to = user_email

        context = {
            'user_name': user_name,
            'username': username,
            'password': password,
            'login_url': login_url or 'https://adarshintercollege.com/login'  # Fallback login URL
        }

        html_content = render_to_string('emails/teacher_registration_email.html', context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(subject, text_content, from_email, [to])
        email.attach_alternative(html_content, "text/html")
        email.send()

        print(f"✅ Teacher registration email sent to {to}")
        return True
    except Exception as e:
        print(f"❌ Failed to send teacher registration email to {user_email}: {e}")
        return False


def send_password_reset_email(user_email, user, reset_url):
    subject = 'Password Reset Requested'
    html_content = render_to_string('emails/reset_pass_email.html', {
        'user': user,
        'reset_url': reset_url,
    })
    from_email = settings.EMAIL_HOST_USER
    to = user_email

    # html_content = render_to_string('registration/registration_success_email.html', {'user_name': user_name})
    text_content = strip_tags(html_content)  # Strip the HTML tags for the plain text version

    # Create the email
    email = EmailMultiAlternatives(subject, text_content, from_email, [to])
    email.attach_alternative(html_content, "text/html")  # Attach the HTML version

    # Send the email
    email.send()
    
def send_notification_email(emails, subject, message):
    # Subject and sender details
    subject = 'Adarsh Inter College! {{subject}}'
    from_email = settings.EMAIL_HOST_USER
    print(emails)
    to = list(emails)
    print(list(emails))

    # Load the HTML content
    html_content = render_to_string('emails/notification_email.html', {"message": message})
    text_content = strip_tags(html_content)  # Strip the HTML tags for the plain text version

    # Create the email
    email = EmailMultiAlternatives(subject, text_content, from_email, list(emails))
    email.attach_alternative(html_content, "text/html")  # Attach the HTML version

    # Send the email
    email.send()
