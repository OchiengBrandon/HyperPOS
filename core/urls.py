from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Main landing page
    path('', views.IndexView.as_view(), name='index'),
    
    
    # Contact form submission
    path('contact/', views.ContactView.as_view(), name='contact'),
    
    # Newsletter signup
    path('newsletter-signup/', views.NewsletterSignupView.as_view(), name='newsletter_signup'),
    
    # Support and information pages
    path('help/', views.help_center_view, name='help'),
    path('documentation/', views.documentation_view, name='documentation'),
    path('blog/', views.blog_view, name='blog'),
    path('community/', views.community_view, name='community'),
    path('updates/', views.updates_view, name='updates'),
    path('roadmap/', views.roadmap_view, name='roadmap'),
    
    # You might add additional pages like:
    # path('about/', views.about_view, name='about'),
    # path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    # path('terms-of-service/', views.terms_of_service_view, name='terms_of_service'),
    # path('faq/', views.faq_view, name='faq'),
]