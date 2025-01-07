from django.shortcuts import render,redirect
from urllib import request
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.views import View
from .models import Product,Cart, Wishlist
from django.db.models import Count
from .forms import CustomerRegistrationForm, CustomerProfileForm,Customer
from django.contrib import messages
from django.conf import settings
import razorpay
import certifi
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# Create your views here.

# home page
@login_required(login_url="login")
def index(request):
    totalitem = 0
    wishlitam = 0
    if request.user.is_authenticated:
     totalitem = len(Cart.objects.filter(user=request.user))
     wishlitam = len(Wishlist.objects.filter(user=request.user))
    return render(request, "app/home.html",locals())


# about page

def about(request):
    totalitem = 0
    wishlitam = 0
    if request.user.is_authenticated:
     totalitem = len(Cart.objects.filter(user=request.user))
     wishlitam = len(Wishlist.objects.filter(user=request.user))
    return render(request, "app/about.html",locals())


# contact page

def contact(request):
    totalitem = 0
    wishlitam = 0
    if request.user.is_authenticated:
     totalitem = len(Cart.objects.filter(user=request.user))
     wishlitam = len(Wishlist.objects.filter(user=request.user))
    return render(request, "app/contact.html",locals())


# category view page

@method_decorator(login_required,name='dispatch')
class CategoryView(View):
    def get(self, request, val):
        totalitem = 0
        wishlitam = 0
        if request.user.is_authenticated:
         totalitem = len(Cart.objects.filter(user=request.user))
         wishlitam = len(Wishlist.objects.filter(user=request.user))
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title')
        return render(request, "app/category.html" ,locals())
    
    
class CategoryTitle(View):
    def get(self, request, val):
        totalitem = 0
        wishlitam = 0
        if request.user.is_authenticated:
         totalitem = len(Cart.objects.filter(user=request.user))
         wishlitam = len(Wishlist.objects.filter(user=request.user))
        product = Product.objects.filter(title=val)
        title = Product.objects.filter(category=product[0].category).values('title')
        return render(request, "app/category.html" ,locals())
    

# product detail page        

class ProductDetails(View):
 def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        wishlist = Wishlist.objects.filter(Q(product=product) & Q(user=request.user))
        
        totalitem = 0
        wishlitam = 0
        if request.user.is_authenticated:
         totalitem = len(Cart.objects.filter(user=request.user))
         wishlitam = len(Wishlist.objects.filter(user=request.user))
        return render(request, "app/productdetail.html", locals())
    

# registeration and login codes    

class  CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, "app/customerregistration.html", locals())
    
    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "user registeration sucessfully")
        else:
            messages.warning(request, "invalid input")
        return render(request, "app/customerregistration.html", locals())
    
    
class ProfileView(View):
    def get(self, request):
        totalitem = 0
        wishlitam = 0
        if request.user.is_authenticated:
          totalitem = len(Cart.objects.filter(user=request.user))
          wishlitam = len(Wishlist.objects.filter(user=request.user))
          form = CustomerProfileForm()
          return render(request, "app/profile.html", locals())
    def post(self, request):
     form = CustomerProfileForm(request.POST)
     if form.is_valid():
        user = request.user
        name = form.cleaned_data['name']
        locality = form.cleaned_data['locality']
        city = form.cleaned_data['city']
        mobile = form.cleaned_data['mobile']
        state = form.cleaned_data['state']
        zipcode = form.cleaned_data['zipcode']

        reg = Customer(user=user, name=name, locality=locality, mobile=mobile, city=city, state=state, zipcode=zipcode)
        reg.save()
        messages.success(request, "Congratulations! Profile Save Successfully")
     else:
        messages.warning(request, "Invalid Input Data")
     return render(request, 'app/profile.html', locals())
 
 
 
def address(request):
      add = Customer.objects.filter(user=request.user)
      return render(request, 'app/address.html', locals()) 

class updateAddress(View):
    def get(self, request, pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        return render(request, 'app/updateAddress.html', locals())

    def post(self, request, pk):
     form = CustomerProfileForm(request.POST)
     if form.is_valid():
        add = Customer.objects.get(pk=pk)
        add.name = form.cleaned_data['name']
        add.locality = form.cleaned_data['locality']
        add.city = form.cleaned_data['city']
        add.mobile = form.cleaned_data['mobile']
        add.state = form.cleaned_data['state']
        add.zipcode = form.cleaned_data['zipcode']
        add.save()
        messages.success(request, 'Congratulations! Profile Update Successfully')
     else:
        messages.warning(request, 'Invalid Input Data')
     return redirect('address')
 
 
 
 
#  cart page

def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    return redirect('/cart')

def show_cart(request):
    
    totalitem = 0
    wishlitam = 0
    if request.user.is_authenticated:
     totalitem = len(Cart.objects.filter(user=request.user))
     wishlitam = len(Wishlist.objects.filter(user=request.user))
     
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    for p in cart:
        value = p.quantity * p.product.discounted_price
        amount = amount + value
    totalamount = amount + 40
    return render(request, 'app/addtocart.html', locals())

class checkout(View):
    def get(self, request):
        
        totalitem = 0
        wishlitam = 0
        if request.user.is_authenticated:
         totalitem = len(Cart.objects.filter(user=request.user))
         wishlitam = len(Wishlist.objects.filter(user=request.user))
         
         
        user = request.user
        add = Customer.objects.filter(user=user)
        cart_items = Cart.objects.filter(user=user)
        famount = 0
        for p in cart_items:
            value = p.quantity * p.product.discounted_price
            famount = famount + value
        totalamount = famount + 40
        
        razoramount = int(totalamount * 100)
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        data = { "amount": razoramount, "currency": "INR", "receipt": "order_rcptid_12"}
        payment_response = client.order.create(data=data)
        print(payment_response)

        return render(request, 'app/checkout.html', locals())


# adding cart

def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)



# minus cart

def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity -= 1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': totalamount
        }
        return JsonResponse(data)

# deleteing cart

def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 40
        data = {
            'amount': amount,
            'totalamount': totalamount
        }
    return JsonResponse(data)



# wishlist related codes

def plus_wishlist(request):
 if request.method == 'GET':
  prod_id=request.GET['prod_id']
  product=Product.objects.get(id=prod_id)
  user = request.user
  Wishlist(user=user, product=product).save()
  data={
       'message' : 'Wishlist Added Successfully',
   }
  return JsonResponse(data)

def minus_wishlist(request):
 if request.method == 'GET':
    prod_id=request.GET['prod_id']
    product=Product.objects.get(id=prod_id)
    user = request.user
    Wishlist.objects.filter(user=user, product=product).delete()
    data={
         'message': 'Wishlist Remove Successfully',
    }
    return JsonResponse(data)


def wishlist_page(request):
    user = request.user
    wishlist_items = Wishlist.objects.filter(user=user).select_related('product')
    context = {
        'wishlist_items': wishlist_items
    }
    return render(request, 'app/wishlist.html', context)



# search bar codes

def search(request):
    query = request.GET.get('search', '')  # Safely get the search query
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = Wishlist.objects.filter(user=request.user).count()
    # Search for products matching the query
    product = Product.objects.filter(Q(title__icontains=query)) if query else []
    return render(request, "app/search.html", {'query': query, 'product': product, 'totalitem': totalitem, 'wishitem': wishitem})

   