
from django.contrib import admin
from .models import Genre, Publisher, Author, Book, Profile, Item, Payment

for m in [Genre, Publisher, Item]:
    admin.site.register(m)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    fields = ('name', 'ol_id', 'alternate_names', 'year_of_birth', 'year_of_death')
    list_display = ('name', 'ol_id', 'alternate_names')
    search_fields = ['name']

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    fields = ['title', 'ol_id', 'isbn', 'genres', 'authors', 'publisher', 'year_of_publication']
    list_display = ['title', 'ol_id']
    autocomplete_fields = ['authors']
    search_fields = ['title']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    fields = ['user', 'item', 'payment_date', 'payment_id', 'payment_request_id', 'amount', 'fees', 'status', 'longurl' ,'shorturl']
    list_display = ['payment_request_id', 'user', 'item', 'payment_date', 'amount', 'status']
    list_display_links = ['payment_request_id', 'user']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    fields = ('user', 'address', 'city', 'state', 'postal_code', ('phone_mobile', 'phone_landline'),
            'genres', 'favourite_books', 'favourite_authors', 'interests', 'boxes_remaining')
    readonly_fields = ( 'favourite_books', 'favourite_authors', 'interests' )

