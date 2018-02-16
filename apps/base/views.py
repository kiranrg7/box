"""Views for the base app"""

from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import DetailView
from django.views.generic.list import ListView
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.core import serializers
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from instamojo_wrapper import Instamojo
from datetime import datetime, timedelta

from .models import Genre, Author, Publisher, Book, Profile, Item, Payment
from .forms import ProfileForm
from utils import has_profile

User = get_user_model()

if settings.INSTAMOJO['TEST']:
    payment_api = Instamojo(api_key=settings.INSTAMOJO['API_KEY'],
        auth_token=settings.INSTAMOJO['AUTH_TOKEN'],
        endpoint='https://test.instamojo.com/api/1.1/')
else:
    payment_api = Instamojo(api_key=settings.INSTAMOJO['API_KEY'],
        auth_token=settings.INSTAMOJO['AUTH_TOKEN'])

def home(request):
    """ Default view for the root """
    items = Item.objects.all()
    return render(request, 'base/home.html', context={'items': items})

def check_profile(request):
    if Profile.objects.filter(user__username=request.user):
        return redirect('home')
    else:
        return redirect('profile-create')

def search_book_title(request):
    data = serializers.serialize("json", Book.objects.filter(title__icontains=request.GET.get("q")))
    return JsonResponse(data, safe=False)

def search_author_name(request):
    data = serializers.serialize("json", Author.objects.filter(name__icontains=request.GET.get("name")))
    return JsonResponse(data, safe=False)

@login_required
def make_payment(request, pk):
    item = Item.objects.get(pk=pk)
    payment = Payment.objects.create(
            user=request.user,
            item=item,
            payment_date=datetime.today(),
            amount=item.price)
    response = payment_api.payment_request_create(
            amount=item.price,
            purpose=item.name,
            send_email=True,
            email=request.user.email,
            redirect_url=request.build_absolute_uri(reverse('payment-redirect', kwargs={'pk': payment.id}))
            )
    if response['success']:
        payment.payment_request_id = response['payment_request']['id']
        payment.save()
    return render(request, 'base/payment_create.html',
                    {
                    'item': item,
                    'payment': payment,
                    'response': response
                    }
                )

@login_required
def payment_redirect(request, pk):
    payment = Payment.objects.get(pk=pk)
    payment.payment_id = request.GET.get("payment_id")
    payment.payment_request_id = request.GET.get("payment_request_id")
    payment.save()

    return render(request, 'base/payment_complete.html')


def payment_webhook(request):
    data = request.POST.dict()
    mac = data.pop("mac")
    message = "|".join(v for k, v in sorted(data.items(), key=lambda x: x[0].lower()))
    mac_calculated = hmac.new(settings.INSTAMOJO['SALT'], message, hashlib.sha1).hexdigest()
    if mac_calculated == mac:
        payment.payment_id = data['payment_id']
        payment.payment_request_id = data['payment_request_id']
        payment.status = data['status']
        payment.fees = data['fees']
        payment.longurl = data['longurl']
        payment.shorturl = data['shorturl']

        if payment.status == 'Credit':
            payment.user.profile.boxes_remaining = payment.user.profile.boxes_remaining + payment.item.boxes_added
            payment.user.profile.save()
        payment.save()
        return HttpResponse(status_code=200)
    else:
        return HttpResponse(status_code=400)

class ProfileCreate(CreateView):
    model = Profile
    form_class = ProfileForm

    def dispatch(self, request, *args, **kwargs):
        if has_profile(request.user):
            return HttpResponseRedirect(reverse('profile-edit'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        for book_id in self.request.POST.getlist('favourite_books'):
            book = Book.objects.get(pk=int(book_id))
            form.instance.favourite_books.add(book)

        for author_id in self.request.POST.getlist('favourite_authors'):
            author = Author.objects.get(pk=int(author_id))
            form.instance.favourite_authors.add(author)
        return response

class ProfileUpdate(UpdateView):
    model = Profile
    form_class = ProfileForm

    def get_object(self):
        return Profile.objects.get(user=self.request.user)

class ProfileDetail(DetailView):
    model = Profile

class ItemList(ListView):
    model = Item

