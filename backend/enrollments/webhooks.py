import json
import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Enrollment, Payment
from courses.models import Course
from django.contrib.auth import get_user_model
from notifications.utils import create_notification

User = get_user_model()


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    # Require signature verification — reject any request without it
    if not settings.STRIPE_WEBHOOK_SECRET:
        return HttpResponse(
            'Stripe webhook secret not configured.', status=500
        )

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature — possible spoofed request
        return HttpResponse(status=400)

    # ----------------------------------------------------------------
    # checkout.session.completed
    # Stripe calls this after a successful Checkout payment.
    # This is the primary enrollment trigger for Stripe payments.
    # ----------------------------------------------------------------
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Debug print to see what session looks like
        print(f"DEBUG: Stripe Session: {session}")

        # Safely get metadata — session.metadata is a StripeObject, access ._data for the plain dict
        metadata = session.metadata._data if session.metadata else {}
        course_id = metadata.get('course_id')
        user_id = metadata.get('user_id')
        print(f"DEBUG: Metadata extracted: course_id={course_id}, user_id={user_id}")


        if not course_id or not user_id:
            return HttpResponse(status=400)

        try:
            user = User.objects.get(id=user_id)
            course = Course.objects.get(id=course_id)
        except (User.DoesNotExist, Course.DoesNotExist):
            return HttpResponse(status=404)

        # Create enrollment (idempotent)
        Enrollment.objects.get_or_create(student=user, course=course)

        # Update payment record: mark completed and store payment_intent_id
        payment = Payment.objects.filter(
            provider_payment_id=session['id']
        ).first()
        if payment:
            payment.status = 'COMPLETED'
            payment.payment_intent_id = session.get('payment_intent', '')
            payment.save()

        create_notification(
            recipient=user,
            type='ENROLLMENT',
            message=f"You have successfully enrolled in {course.title}.",
            course=course
        )

    # ----------------------------------------------------------------
    # checkout.session.expired
    # User abandoned the checkout page — mark payment as FAILED.
    # ----------------------------------------------------------------
    elif event['type'] == 'checkout.session.expired':
        session = event['data']['object']
        payment = Payment.objects.filter(
            provider_payment_id=session['id']
        ).first()
        if payment and payment.status == 'PENDING':
            payment.status = 'FAILED'
            payment.save()

    # ----------------------------------------------------------------
    # charge.refunded
    # Triggered after a refund is processed (via admin or Stripe dashboard).
    # ----------------------------------------------------------------
    elif event['type'] == 'charge.refunded':
        charge = event['data']['object']
        payment_intent_id = charge.get('payment_intent')
        if payment_intent_id:
            payment = Payment.objects.filter(
                payment_intent_id=payment_intent_id,
                status='COMPLETED'
            ).first()
            if payment:
                payment.status = 'REFUNDED'
                payment.save()
                # Revoke enrollment
                enrollment = Enrollment.objects.filter(
                    student=payment.user,
                    course=payment.course
                ).first()
                if enrollment:
                    enrollment.status = 'REFUNDED'
                    enrollment.save()
                create_notification(
                    recipient=payment.user,
                    type='REFUND',
                    message=f"Your refund for {payment.course.title} has been processed.",
                    course=payment.course
                )

    return HttpResponse(status=200)
