from django.urls import path
from .views import Login_View,Client_view,Admin_view,LandingView,Logout_View,Cart_View,Delete_item,ViewAllCustomer,DeleteCustomer,AddCustomer,UpdateStudent,HandleProducts,AddProductView,AddQuantity,RemoveProduct,ClearCart,Checkout,PrevInvoices,SignUp,DownloadInvoice

urlpatterns = [
    
    path('',LandingView.as_view(),name='landingpage'),
    path ('login/',Login_View.as_view(),name='login'),
    path('home/',Client_view.as_view(),name='home'),
    path('adminHome/',Admin_view.as_view(),name='adminHome'),
    path('logout/',Logout_View.as_view(),name='logout'),
    path('cart',Cart_View.as_view(),name='cart'),
    path('delete_item/<int:item_id>/',Delete_item.as_view(),name='delete_item'),
    path('ViewAllCustomer',ViewAllCustomer.as_view(),name='ViewAllCustomer'),
    path('DeleteCustomer',DeleteCustomer.as_view(),name='DeleteCustomer'),
    path('AddCustomer',AddCustomer.as_view(),name='AddCustomer'),
    path('UpdateStudent/<int:id>/',UpdateStudent.as_view(),name='UpdateStudent'),
    path('HandleProducts',HandleProducts.as_view(),name='HandleProducts'),
    path('AddProduct',AddProductView.as_view(),name='AddProduct'),
    path('AddQuantity/<int:id>/',AddQuantity.as_view(),name='AddQuantity'),
    path('RemoveProduct',RemoveProduct.as_view(),name='RemoveProduct'),
    path('ClearCart',ClearCart.as_view(),name='ClearCart'),
    path('CheckOut',Checkout.as_view(),name='Checkout'),
    path('PrevInvoices',PrevInvoices.as_view(),name='PrevInvoices'),
    path('SignUp',SignUp.as_view(),name='SignUp'),
    path('DownloadInvoice/<int:invoice_id>/',DownloadInvoice.as_view(),name='DownloadInvoice'),
]
