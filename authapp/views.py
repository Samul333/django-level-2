from django.shortcuts import render
from rest_framework import generics
from .serializers import RegisterSerializer,LoginSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse
import jwt
from django.urls import reverse
from django.conf import settings
import io
class RegisterView(generics.GenericAPIView):

    def post(self, request):
        user = request.data
        serializer = RegisterSerializer(data = user)
        import ipdb
        ipdb.sset_trace()
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_data = serializer.data
        user = User.objects.get(email = user_data['email'])
        
        token = RefreshToken.for_user(user).access_token
        current_site = get_current_site(request).domain

        
        relativeLink = reverse('email-verify')
        absurl = 'http://'+ current_site+relativeLink+ "?token="+ str(token)
        email_body = 'Hi ' + user.username + 'Use the link to verify your email \n'+absurl
        data = {'to_email':user.email,'email_body':email_body, 'email_subject':'Verify your email'}
      
        Util.send_email(data)
        return Response(user_data)
        
    def delete(self,request):
        json_data = request.body
        stream  = io.BytesIO(json_data)
        pythondata = JSONParser().parse(stream)
        id = pythondata.get('id')
        stu = User.objects.get(id=id)
        stu.delete()
        res = {'msg', 'Data has been deleted!!'}
        json_data = JSONRenderer().render(res)
        return HttpResponse(json_data, content_type='application/json')

    

class VerifyEmail(generics.GenericAPIView):
    def get(self,request):
        token = request.GET.get('token')
        print(settings.SECRET_KEY)
        try:
            payload = jwt.decode(token,settings.SECRET_KEY,algorithms=['HS256'])
            print(payload)
            user = User.objects.get(id=payload['user_id'])
            user.is_verified = True
            user.save()
            return Response({'email':'Sucessfully activated'})
        except:
            return Response({'email':'Error validation'})

class LoginAPIView(generics.GenericAPIView):

    def post(self,request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)