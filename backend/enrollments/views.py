import stripe
import paypalrestsdk
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Enrollment, Payment
from .serializers import EnrollmentSerializer, PaymentSerializer
from courses.models import Course
from notifications.utils import create_notification

stripe.api_key = settings.STRIPE_SECRET_KEY

paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return Enrollment.objects.none()
        if user.role == 'MENTOR':
            return Enrollment.objects.filter(course__mentor=user)
        return Enrollment.objects.filter(student=user)

    @action(detail=False, methods=['post'])
    def enroll_free(self, request):
        """Directly enroll in a free course (no payment required)."""
        course_id = request.data.get('course_id')
        course = get_object_or_404(Course, id=course_id)

        if not course.is_free:
            return Response({'error': 'This course is not free.'}, status=status.HTTP_400_BAD_REQUEST)

        if Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response({'error': 'Already enrolled'}, status=status.HTTP_400_BAD_REQUEST)

        enrollment = Enrollment.objects.create(student=request.user, course=course)
        create_notification(
            recipient=request.user,
            type='ENROLLMENT',
            message=f"You have successfully enrolled in {course.title}.",
            course=course
        )
        return Response(EnrollmentSerializer(enrollment).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def create_stripe_checkout(self, request):
        course_id = request.data.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response({'error': 'Already enrolled'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': course.title},
                        'unit_amount': int(course.price * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=settings.FRONTEND_URL + '/payment-success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=settings.FRONTEND_URL + '/payment-failed',
                customer_email=request.user.email,
                metadata={'course_id': course.id, 'user_id': request.user.id}
            )
            
            Payment.objects.create(
                user=request.user,
                course=course,
                provider='STRIPE',
                amount=course.price,
                provider_payment_id=checkout_session.id,
                # payment_intent_id filled by webhook after payment completes
                payment_intent_id=''
            )
            
            return Response({'id': checkout_session.id, 'url': checkout_session.url})
        except stripe.error.AuthenticationError as e:
            return Response(
                {'error': 'Stripe authentication failed. Check your STRIPE_SECRET_KEY in .env.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def create_paypal_order(self, request):
        course_id = request.data.get('course_id')
        course = get_object_or_404(Course, id=course_id)

        if Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response({'error': 'Already enrolled'}, status=status.HTTP_400_BAD_REQUEST)

        paypal_currency = getattr(settings, 'PAYPAL_CURRENCY', 'USD')
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "redirect_urls": {
                "return_url": settings.FRONTEND_URL + "/payment-success",
                "cancel_url": settings.FRONTEND_URL + "/payment-failed"
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": course.title,
                        "sku": str(course.id),
                        "price": str(course.price),
                        "currency": paypal_currency,
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": str(course.price),
                    "currency": paypal_currency
                },
                "description": f"Enrolling in {course.title}"
            }]
        })

        try:
            if payment.create():
                approval_url = next(
                    link.href for link in payment.links if link.rel == 'approval_url'
                )
                Payment.objects.create(
                    user=request.user,
                    course=course,
                    provider='PAYPAL',
                    amount=course.price,
                    provider_payment_id=payment.id,
                    status='PENDING'
                )
                return Response({'approval_url': approval_url, 'payment_id': payment.id})
            else:
                error_msg = payment.error.get('message', 'PayPal order creation failed.') if payment.error else 'PayPal order creation failed.'
                return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_str = str(e)
            if 'Client Authentication failed' in error_str or '401' in error_str:
                return Response(
                    {'error': 'PayPal authentication failed. Check your PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET in .env.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response({'error': error_str}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def verify_stripe_session(self, request):
        """
        Called by the frontend after Stripe redirects back with ?session_id=...
        Retrieves the session from Stripe, verifies payment_status='paid', and
        creates the enrollment. This is idempotent — safe to call even if the
        webhook already ran.
        """
        session_id = request.data.get('session_id')
        if not session_id:
            return Response({'error': 'session_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = stripe.checkout.Session.retrieve(session_id)
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if session.payment_status != 'paid':
            return Response(
                {'error': f'Payment not completed. Status: {session.payment_status}'},
                status=status.HTTP_402_PAYMENT_REQUIRED
            )

        # Verify the session belongs to the authenticated user via metadata
        # session.metadata is a StripeObject whose internal data lives in ._data (a plain dict)
        metadata = session.metadata._data if session.metadata else {}
        user_id = metadata.get('user_id')
        course_id = metadata.get('course_id')

        if str(request.user.id) != str(user_id):
            return Response({'error': 'Unauthorized.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Create enrollment idempotently
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user,
            course=course
        )

        # Update payment record
        payment = Payment.objects.filter(provider_payment_id=session_id).first()
        if payment and payment.status != 'COMPLETED':
            payment.status = 'COMPLETED'
            payment.payment_intent_id = getattr(session, 'payment_intent', '') or ''
            payment.save()

        if created:
            create_notification(
                recipient=request.user,
                type='ENROLLMENT',
                message=f"You have successfully enrolled in {course.title}.",
                course=course
            )

        return Response({
            'status': 'enrolled',
            'course_id': course.id,
            'course_title': course.title,
            'already_enrolled': not created,
        })

    @action(detail=False, methods=['post'])
    def capture_paypal_payment(self, request):
        payment_id = request.data.get('payment_id')
        payer_id = request.data.get('payer_id')
        
        payment = paypalrestsdk.Payment.find(payment_id)

        if payment.execute({"payer_id": payer_id}):
            # Update Payment record
            payment_record = get_object_or_404(Payment, provider_payment_id=payment_id)
            payment_record.status = 'COMPLETED'
            payment_record.save()

            # Create Enrollment
            enrollment, created = Enrollment.objects.get_or_create(
                student=payment_record.user,
                course=payment_record.course
            )

            # Notification
            create_notification(
                recipient=payment_record.user,
                type='ENROLLMENT',
                message=f"You have successfully enrolled in {payment_record.course.title}.",
                course=payment_record.course
            )

            return Response({'status': 'Payment captured and enrollment created'})
        else:
            return Response({'error': payment.error}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def request_refund(self, request, pk=None):
        enrollment = self.get_object()
        if enrollment.status == 'REFUNDED':
            return Response({'error': 'Already refunded'}, status=400)
        
        # Simple refund request for now (could add more complex logic)
        return Response({'status': 'Refund requested'})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve_refund(self, request, pk=None):
        enrollment = self.get_object()
        payment = Payment.objects.filter(course=enrollment.course, user=enrollment.student, status='COMPLETED').last()
        
        if not payment:
            return Response({'error': 'No completed payment found for this enrollment'}, status=400)

        refund_success = False
        if payment.provider == 'STRIPE':
            try:
                # Use stored payment_intent_id if available, else fetch from session
                pi_id = payment.payment_intent_id
                if not pi_id:
                    session = stripe.checkout.Session.retrieve(payment.provider_payment_id)
                    pi_id = session.payment_intent
                stripe.Refund.create(payment_intent=pi_id)
                refund_success = True
            except Exception as e:
                return Response({'error': f"Stripe refund failed: {str(e)}"}, status=400)
        
        elif payment.provider == 'PAYPAL':
            try:
                # For PayPal, we need to find the sale ID from the executed payment
                pp_payment = paypalrestsdk.Payment.find(payment.provider_payment_id)
                sale_id = pp_payment.transactions[0].related_resources[0].sale.id
                sale = paypalrestsdk.Sale.find(sale_id)
                refund = sale.refund({})
                if refund.success():
                    refund_success = True
                else:
                    return Response({'error': f"PayPal refund failed: {refund.error}"}, status=400)
            except Exception as e:
                return Response({'error': f"PayPal refund logic failed: {str(e)}"}, status=400)

        if refund_success:
            enrollment.status = 'REFUNDED'
            enrollment.save()
            payment.status = 'REFUNDED'
            payment.save()

            create_notification(
                recipient=enrollment.student,
                type='REFUND',
                message=f"Your refund for {enrollment.course.title} has been processed successfully.",
                course=enrollment.course
            )
            return Response({'status': 'Refunded successfully'})
        
        return Response({'error': 'Refund failed'}, status=400)

class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)
