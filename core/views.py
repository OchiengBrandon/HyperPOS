from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse

class IndexView(TemplateView):
    """
    View for the main landing page of HyperPOS website.
    Displays marketing information, features, pricing, and testimonials.
    """
    template_name = 'core/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add features data for the features section
        context['features'] = [
            {
                'icon': 'shopping-cart',
                'title': 'Intuitive Sales Interface',
                'description': 'Process transactions quickly with our user-friendly interface designed for speed and accuracy, reducing customer wait times.'
            },
            {
                'icon': 'chart-line',
                'title': 'Real-time Analytics',
                'description': 'Gain valuable insights into your business performance with comprehensive reports and dashboards updated in real-time.'
            },
            {
                'icon': 'box',
                'title': 'Inventory Management',
                'description': 'Keep track of your stock levels automatically, receive low-stock alerts, and manage suppliers all in one place.'
            },
            {
                'icon': 'users',
                'title': 'Customer Relationship',
                'description': 'Build stronger relationships with customer profiles, purchase history tracking, and personalized loyalty programs.'
            },
            {
                'icon': 'credit-card',
                'title': 'Multiple Payment Options',
                'description': 'Accept various payment methods including credit cards, mobile payments, and split payments with ease.'
            },
            {
                'icon': 'cloud',
                'title': 'Cloud-Based System',
                'description': 'Access your business data from anywhere, anytime with our secure cloud-based solution with automatic backups.'
            }
        ]
        
        # Add pricing plans data
        context['pricing_plans'] = [
            {
                'name': 'Starter',
                'price': 29,
                'popular': False,
                'features': [
                    'Single register',
                    'Up to 500 products',
                    'Basic reporting',
                    'Email support',
                    'Cloud backup'
                ]
            },
            {
                'name': 'Professional',
                'price': 59,
                'popular': True,
                'features': [
                    'Up to 3 registers',
                    'Unlimited products',
                    'Advanced reporting',
                    'Priority support',
                    'Customer loyalty program',
                    'Employee management'
                ]
            },
            {
                'name': 'Enterprise',
                'price': 99,
                'popular': False,
                'features': [
                    'Unlimited registers',
                    'Unlimited products',
                    'Custom reporting',
                    '24/7 dedicated support',
                    'Advanced inventory management',
                    'Multi-location support',
                    'API access'
                ]
            }
        ]
        
        # Add testimonials data
        context['testimonials'] = [
            {
                'text': 'HyperPOS has completely transformed how we run our cafe. The intuitive interface means our staff needed minimal training, and the real-time inventory tracking has reduced our wastage by over 30%.',
                'author': 'Sarah Johnson',
                'title': 'Owner, Sunrise Cafe',
                'image': 'https://picsum.photos/id/1027/200'
            },
            {
                'text': 'As a retail boutique, we needed a system that could handle both in-store and online sales seamlessly. HyperPOS has exceeded our expectations with its omnichannel capabilities and detailed analytics.',
                'author': 'Michael Chen',
                'title': 'Director, Urban Style Boutique',
                'image': 'https://picsum.photos/id/1012/200'
            },
            {
                'text': 'The customer support team at HyperPOS is outstanding. They helped us migrate from our old system and were available every step of the way. Now our hardware store operations are smoother than ever.',
                'author': 'Robert Garcia',
                'title': 'Manager, Garcia\'s Hardware',
                'image': 'https://picsum.photos/id/1074/200'
            }
        ]
        
        # Add steps data for how it works section
        context['steps'] = [
            {
                'number': 1,
                'title': 'Sign Up & Setup',
                'description': 'Create your account, input your business details, and customize your POS settings to match your specific needs.'
            },
            {
                'number': 2,
                'title': 'Import Your Inventory',
                'description': 'Easily import your existing product catalog or create a new one from scratch with our user-friendly tools.'
            },
            {
                'number': 3,
                'title': 'Train Your Team',
                'description': 'Take advantage of our comprehensive training resources to get your staff up to speed quickly.'
            },
            {
                'number': 4,
                'title': 'Go Live & Grow',
                'description': 'Start processing sales and use our analytics to make data-driven decisions that help your business thrive.'
            }
        ]
        
        # Footer quick links
        context['quick_links'] = [
            {'name': 'Features', 'url': '#features'},
            {'name': 'Pricing', 'url': '#pricing'},
            {'name': 'Testimonials', 'url': '#testimonials'},
            {'name': 'Blog', 'url': '/blog'},
            {'name': 'POS System', 'url': '/pos'}
        ]
        
        # Support links for footer
        context['support_links'] = [
            {'name': 'Help Center', 'url': '/help'},
            {'name': 'Documentation', 'url': '/documentation'},
            {'name': 'Community', 'url': '/community'},
            {'name': 'Updates', 'url': '/updates'},
            {'name': 'Roadmap', 'url': '/roadmap'}
        ]
        
        # Contact information
        context['contact_info'] = {
            'address': '123 Business Avenue, Tech City, TC 10101',
            'phone': '+1 (555) 123-4567',
            'email': 'info@hyperpos.com',
            'hours': 'Mon-Fri: 9AM - 5PM EST'
        }
        
        # Social media links
        context['social_links'] = [
            {'platform': 'facebook', 'url': '#'},
            {'platform': 'twitter', 'url': '#'},
            {'platform': 'instagram', 'url': '#'},
            {'platform': 'linkedin', 'url': '#'}
        ]
        
        return context


class POSRedirectView(View):
    """
    View to redirect users to the actual POS application.
    If user is not authenticated, redirects to login page.
    """
    @method_decorator(login_required)
    def get(self, request):
        # This would redirect to your actual POS application
        # You might have different logic based on user type or subscription
        return redirect('pos_app:dashboard')


class ContactView(View):
    """
    View to handle contact form submissions.
    """
    def post(self, request):
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Here you would typically process the contact form
        # e.g., send an email, create a database entry, etc.
        
        # For demonstration, we'll just return a success message
        if name and email and message:
            # Send email logic would go here
            # ...
            
            messages.success(request, "Thank you for contacting us! We'll get back to you soon.")
            return redirect('core:index')
        else:
            messages.error(request, "Please fill in all required fields.")
            return redirect('core:contact')


class NewsletterSignupView(View):
    """
    View to handle newsletter signup.
    """
    def post(self, request):
        email = request.POST.get('email')
        
        if not email:
            return JsonResponse({'success': False, 'message': 'Email is required'})
        
        # Here you would typically add the email to your newsletter service
        # e.g., Mailchimp, SendGrid, etc.
        
        # For demonstration purposes
        return JsonResponse({
            'success': True, 
            'message': 'Thank you for subscribing to our newsletter!'
        })


# These views would be implemented in separate authentication apps
# or using Django's built-in auth views, but included here for reference

def login_view(request):
    """
    View for the login page.
    """
    return render(request, 'core/login.html')


def signup_view(request):
    """
    View for the signup page.
    """
    return render(request, 'core/signup.html')


def help_center_view(request):
    """
    View for the help center page.
    """
    return render(request, 'core/help.html')


def documentation_view(request):
    """
    View for the documentation page.
    """
    return render(request, 'core/documentation.html')


def blog_view(request):
    """
    View for the blog listing page.
    """
    return render(request, 'core/blog.html')


def community_view(request):
    """
    View for the community page.
    """
    return render(request, 'core/community.html')


def updates_view(request):
    """
    View for the updates/changelog page.
    """
    return render(request, 'core/updates.html')


def roadmap_view(request):
    """
    View for the product roadmap page.
    """
    return render(request, 'core/roadmap.html')