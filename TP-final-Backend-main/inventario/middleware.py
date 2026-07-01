from datetime import datetime
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

class RestriccionHorariaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.groups.filter(name='Admin').exists() and not request.user.is_superuser:
            hora_actual = datetime.now().time()
            hora_inicio = datetime.strptime("08:00", "%H:%M").time()
            hora_fin = datetime.strptime("23:00", "%H:%M").time()
            
            if not (hora_inicio <= hora_actual <= hora_fin):
                path_login = reverse('login')
                path_logout = reverse('logout')
                
                if request.path not in [path_login, path_logout]:
                    messages.error(request, "Acceso al sistema permitido únicamente de 08:00 a 18:00 hs.")
                    from django.contrib.auth import logout
                    logout(request)
                    return redirect('login')

        return self.get_response(request)