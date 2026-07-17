import stripe
import paypalrestsdk
from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Payment, Enrollment
from .serializers import PaymentSerializer
from notifications.utils import create_notification

stripe.api_key = settings.STRIPE_SECRET_KEY

paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

class AdminRefundViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.filter(status='REFUND_REQUESTED').order_by('-created_at')
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        payment = self.get_object()
        enrollment = get_object_or_404(Enrollment, course=payment.course, student=payment.user)
        
        refund_success = False
        if payment.provider == 'STRIPE':
            try:
                session = stripe.checkout.Session.retrieve(payment.provider_payment_id)
                stripe.Refund.create(payment_intent=session.payment_intent)
                refund_success = True
            except Exception as e:
                return Response({'error': f"Stripe refund failed: {str(e)}"}, status=400)
        
        elif payment.provider == 'PAYPAL':
            try:
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
            payment.status = 'REFUNDED'
            payment.save()
            enrollment.delete()

            create_notification(
                recipient=payment.user,
                type='REFUND',
                message=f"Your refund for {payment.course.title} has been approved. You have been unenrolled from the course.",
                course=payment.course
            )
            return Response({'status': 'Refund approved'})
        
        return Response({'error': 'Refund failed'}, status=400)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        payment = self.get_object()
        payment.status = 'COMPLETED' # Reset to completed
        payment.save()
        
        reason = request.data.get('reason', 'No reason provided.')
        create_notification(
            recipient=payment.user,
            type='REFUND',
            message=f"Your refund request for {payment.course.title} was rejected. Reason: {reason}",
            course=payment.course
        )
        return Response({'status': 'Refund rejected'})
