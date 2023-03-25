from WoofWaf.models import waf_admin

class WafBackend:
    def authenticate(self, request, username=None, password=None):
        try:
            user = waf_admin.objects.get(username=username)
            if user.check_password(password):
                return user
        except waf_admin.DoesNotExist:
            return None


