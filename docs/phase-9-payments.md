# Phase 9 — Payments

## Summary
Phase 9 implemented a robust payment infrastructure supporting multiple providers (**Stripe** and **PayPal**). This phase introduced formal payment tracking, sandbox environment integration, and a comprehensive refund management system for course enrollments.

## Technical Implementation

### Multi-Provider Gateway
- **Stripe Checkout**: Integrated Stripe's pre-built Checkout session for secure card payments. Handled status synchronization via persistent webhooks.
- **PayPal Order Flow**: Leveraged the `paypalrestsdk` to implement an Order-Capture flow. Payments are initialized on the frontend, approved on PayPal's sandbox site, and finalized through a server-side capture step.
- **Unified Payment Model**: Refactored the `Payment` architecture to store provider-specific IDs (`provider_payment_id`) and handle standardized statuses (**PENDING**, **COMPLETED**, **REFUNDED**, **FAILED**).

### Refund Infrastructure
- **Provider-Specific Refunds**: Implemented backend logic to communicate with both Stripe and PayPal APIs to process full refunds.
- **Student Requests**: Added a "Request Refund" interface in the student dashboard, enabling users to initiate the refund process for their enrolled courses.
- **Revocation Logic**: Automatically revokes course enrollment status upon successful refund processing.

## Core Components

### Backend
- `enrollments.models.Payment`: Centralized tracking for all transactions across providers.
- `EnrollmentViewSet.create_stripe_checkout`: Generates Stripe Checkout sessions.
- `EnrollmentViewSet.create_paypal_order`: Initializes PayPal transactions.
- `EnrollmentViewSet.capture_paypal_payment`: Server-side finalization of PayPal payments.
- `EnrollmentViewSet.approve_refund`: Managed administrative logic for multi-provider refunds.
- `enrollments.webhooks.stripe_webhook`: Background synchronization for Stripe events.

### Frontend
- `CourseDetails`: Updated with a payment provider selection interface.
- `PaymentSuccess`: Handles post-success redirection and PayPal-specific capture calls.
- `LearningDashboard`: Enhanced with a refund request mechanism for active enrollments.

## API Routes
- `POST /api/enrollments/create_stripe_checkout/`: Start Stripe payment.
- `POST /api/enrollments/create_paypal_order/`: Start PayPal payment.
- `POST /api/enrollments/capture_paypal_payment/`: Finalize PayPal payment.
- `POST /api/enrollments/{id}/request_refund/`: Initiate refund request.
- `POST /api/enrollments/{id}/approve_refund/`: Process payment reversal (Admin only).
- `POST /api/enrollments/webhook/`: Stripe webhook endpoint.
