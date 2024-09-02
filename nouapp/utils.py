from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_registration_success_email(user_email, user_name):
    # Subject and sender details
    subject = 'Welcome to NOU e-Gyan Learning Portal! Your Registration is Successful'
    from_email = settings.EMAIL_HOST_USER
    to = user_email

    # Load the HTML content
    html_content = render_to_string('registration/registration_success_email.html', {'user_name': user_name})
    text_content = strip_tags(html_content)  # Strip the HTML tags for the plain text version

    # Create the email
    email = EmailMultiAlternatives(subject, text_content, from_email, [to])
    email.attach_alternative(html_content, "text/html")  # Attach the HTML version

    # Send the email
    email.send()

def send_password_reset_email(user_email, user, reset_url):
    subject = 'Password Reset Requested'
    html_content = render_to_string('registration/reset_pass_email.html', {
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
    subject = 'NOU e-Gyan Learning Portal! {{subject}}'
    from_email = settings.EMAIL_HOST_USER
    print(emails)
    to = list(emails)
    print(list(emails))

    # Load the HTML content
    html_content = render_to_string('registration/notification_email.html', {"message": message})
    text_content = strip_tags(html_content)  # Strip the HTML tags for the plain text version

    # Create the email
    email = EmailMultiAlternatives(subject, text_content, from_email, list(emails))
    email.attach_alternative(html_content, "text/html")  # Attach the HTML version

    # Send the email
    email.send()
