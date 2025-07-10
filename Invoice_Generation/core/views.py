from django.shortcuts import render,redirect
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .models import product,User,Invoice,InvoiceItem
from django.contrib import messages
from .forms import Create_User,AddProduct
from django.utils import timezone
from django.core.paginator import Paginator
from .tasks import send_invoice_email
from django.http import HttpResponse, Http404
from django.template.loader import get_template
from weasyprint import HTML
# Create your views here.

class AdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.role!='admin':
            messages.error(request, "You are not authorized to access this page.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    

class LandingView(View):
    def get(self,request):
        return render(request,'LandingPage.html')
    

class SignUp(View):
    def get(self,request):
        customer_data=Create_User()
        return render(request,'SignUp.html',{'form':customer_data})
    
    def post(self,request):
        data=Create_User(request.POST)

        try:
            if data.is_valid():
                data.save()
                messages.success(request, "You Signed Up successfully.")
                return redirect('home')
            else:
                messages.error(request, "Form is invalid. Please correct the errors below.")
                return render(request, 'AddCustomer.html', {'form': data})
        except Exception as e:
                messages.error(request, f"Something went wrong: {e}")

        return redirect('SignUp')
    

class Login_View(View):
    def get(self,request):
        if request.user.is_authenticated:
            print(request.user.role)

            if request.user.role == 'client':
                return redirect('home')
            elif request.user.role == 'admin':
                return redirect('adminHome')
            
        return render(request,'userLogin.html')
    
    def post(self,request):
        email=request.POST.get('email')
        password=request.POST.get('password')
        print(email)
        print(password)
        user=authenticate(request,email=email,password=password)

        if user is not None:
            login(request,user)
            if user.role == 'client':
                return redirect('home')
            elif user.role =='admin':
                return redirect('adminHome')
            
        return render(request,'userLogin.html',{'error':'Invalid Credentials'})    
    

class Logout_View(View):
    def get(self,request):
        logout(request)
        return render(request,'userLogin.html')
    def post(self,request):
        logout(request)
        return redirect('login')
    
    

class Client_view(LoginRequiredMixin,View):
    def get(self,request):
        prod=product.objects.all()
        pagin=Paginator(prod,6)
        page_num=request.GET.get('page')
        page_obj=pagin.get_page(page_num)
        return render(request,'home.html',{'products':page_obj})
    
    def post(self, request):
        product_id = request.POST.get('product_id')
        prod = get_object_or_404(product, id=product_id)
        user = request.user
        if prod.quantity <= 0:
            messages.error(request, f"Sorry, '{prod.name}' is out of stock.")
            return redirect('home')

        invoice, created = Invoice.objects.get_or_create(
            client=user,
            status='UNPAID',
            defaults={'due_date':datetime.today().date() + timedelta(days=7)}
        )

        item, item_created = InvoiceItem.objects.get_or_create(
            invoice=invoice,
            product=prod,
            defaults={'quantity': 1, 'unit_price': prod.price}
        )

        if not item_created:
            item.quantity += 1
            print(prod.quantity)
            item.save()

        prod.quantity-=1
        prod.save()    
        messages.success(request, f"'{prod.name}' added to your cart.")
        return redirect('home')
    

class Admin_view(AdminRequiredMixin,View):

        def get(self,request):
            return render(request,'adminHome.html')


class Cart_View(LoginRequiredMixin,View):
    def get(Self,request):
        user=request.user
        try:
            invoice, created = Invoice.objects.get_or_create(
                client=request.user,
                status="UNPAID",
                defaults={
                    'due_date': timezone.now() + timedelta(days=7),
                }
        )
            items=invoice.invoices.all()
            subtotal=invoice.subtotal
            tax=invoice.tax
            total=invoice.total

        except invoice.DoesNotExist:
                    invoice = None
                    items = []
                    subtotal = 0
                    tax = 0
                    total = 0

        return render(request,'Cart.html', {'invoice': invoice,
        'items': items,
        'subtotal': subtotal,
        'tax': tax,
        'total': total})        

class Delete_item(LoginRequiredMixin,View):
    def post(self,request,item_id):
         item = get_object_or_404(InvoiceItem, id=item_id, invoice__client=request.user, invoice__status='UNPAID')
         item.product.quantity+=item.quantity
         item.product.save()

         item.delete()

         messages.success(request, f"'{item.product.name}' was removed from your cart.")
         return redirect('cart')
    

class ViewAllCustomer(AdminRequiredMixin,View):
    def get(self,request):
        prod= User.objects.filter(role='client')
        pagin=Paginator(prod,12)
        page_num=request.GET.get('page')
        page_obj=pagin.get_page(page_num)
            
        return render(request,'ViewCustomer.html',{'emp_data':page_obj})
    
class DeleteCustomer(AdminRequiredMixin,View):
    def post(self, request):
        customer_id = request.POST.get('id')
        try:
            delete_record = User.objects.get(id=customer_id)
            delete_record.delete()
            messages.success(request, "Customer deleted successfully.")
        except User.DoesNotExist:
            messages.error(request, "Customer not found.")
        
        return redirect('ViewAllCustomer') 

class AddCustomer(AdminRequiredMixin,View):
    def get(self,request):
        customer_data=Create_User()
        return render(request,'AddCustomer.html',{'form':customer_data})
    
    def post(self,request):
        data=Create_User(request.POST)

        try:
            if data.is_valid():
                data.save()
                messages.success(request, "Customer added successfully.")
                return redirect('ViewAllCustomer')
            else:
                messages.error(request, "Form is invalid. Please correct the errors below.")
                return render(request, 'AddCustomer.html', {'form': data})
        except Exception as e:
                messages.error(request, f"Something went wrong: {e}")

        return redirect('ViewAllCustomer')
        
class UpdateStudent(AdminRequiredMixin,View):
    def get(self,request,id):
        customer=User.objects.get(id=id)
        form_add=Create_User(instance=customer)
        return render(request,'UpdateRecord.html',{'form':form_add})

    def post(self,request,id):   
        data=User.objects.get(id=id)    
        changed_data=Create_User(request.POST,instance=data)
        if(changed_data.is_valid):
            changed_data.save()
            return redirect('ViewAllCustomer')
        

class HandleProducts(AdminRequiredMixin,View):
    def get(self,request):
        prod=product.objects.all()
        pagin=Paginator(prod,9)
        page_num=request.GET.get('page')
        page_obj=pagin.get_page(page_num)
        return render(request,'HandleProducts.html',{'products':page_obj})
    
    def post(self,request):
        return render('/')


class AddProductView(AdminRequiredMixin, View): 
    def get(self, request):
        form = AddProduct() 
        return render(request, 'AddProduct.html', {'form': form})

    def post(self, request):
        form = AddProduct(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully.")
            return redirect('HandleProducts')
        else:
            messages.error(request, "Please fix the errors below.")
        return render(request, 'AddProduct.html', {'form': form})

    
class AddQuantity(AdminRequiredMixin, View):
    def post(self, request, id):
        prod = get_object_or_404(product, id=id)

        qty_to_add = request.POST.get('quantity')
        
        try:
            qty = int(qty_to_add)
            if qty > 0:
                prod.quantity += qty
                prod.save()

                messages.success(request, f"Added {qty} to '{prod.name}'.")
            else:
                messages.warning(request, "Quantity must be greater than zero.")

        except ValueError:
            messages.error(request, "Invalid quantity input.")
        return redirect('HandleProducts')
    
class RemoveProduct(AdminRequiredMixin,View):
       def post(self, request):
        product_id = request.POST.get('id')
        try:
            delete_record = product.objects.get(id=product_id)
            delete_record.delete()
            messages.success(request, "Product deleted successfully.")
        except:
            messages.error(request, "Something went wrong.")
        
        return redirect('HandleProducts') 

class ClearCart(LoginRequiredMixin,View):
    def post(self,request):
        try:
            invoice=Invoice.objects.get(client=request.user,status="UNPAID")
            item=invoice.invoices.all()

            for it in item:
                it.product.quantity+=it.quantity
                it.product.save()

            item.delete()    
            messages.success(request, "Cart cleared successfully.")
        except invoice.DoesNotExist:
            messages.warning(request, "No active cart to clear.")

        return redirect('cart')

class Checkout(LoginRequiredMixin, View):

    def post(self, request):
        try:
            invoice = Invoice.objects.get(client=request.user, status="UNPAID")
            invoice.status = "PAID"
            invoice.save()
            send_invoice_email.delay(request.user.id)

            # deleted_count, _ = InvoiceItem.objects.filter(invoice=invoice).delete()
            # print(f"{deleted_count} invoice items deleted.")

            messages.success(request, "Checkout successful. Your invoice is now marked as PAID and the cart is cleared.")
        except Invoice.DoesNotExist:
            messages.warning(request, "No active cart found for checkout.")

        return redirect('home')


class PrevInvoices(LoginRequiredMixin,View):
    def get(self, request):
        invoices = Invoice.objects.filter(client=request.user, status="PAID").order_by('-date_create')

        # for item in invoices:
        #     print(item.product.name)
        #     print(item.quantity)
        return render(request, 'Invoices.html', {'invoices': invoices})
    

class DownloadInvoice(LoginRequiredMixin,View):
    def get(self, request, invoice_id):
        try:
            invoice = Invoice.objects.get(id=invoice_id, client=request.user)
        except Invoice.DoesNotExist:
            raise Http404("Invoice not found.")

        template = get_template('invoice_pdf_template.html')
        html_content = template.render({'invoice': invoice})

        pdf_file = HTML(string=html_content).write_pdf()

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.id}.pdf"'
        return response