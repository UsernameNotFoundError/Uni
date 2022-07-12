from django.contrib import admin
from mainapp.models import *
# Register your models here in oder to see them when we log in as an admin
admin.site.register(Species)
admin.site.register(UserProfileInfo)
admin.site.register(Searchregister)
admin.site.register(Assembly)
admin.site.register(Genomicannotation)
admin.site.register(Proteinset)
admin.site.register(Featureannotation)
admin.site.register(Diamonddb)
admin.site.register(Blastdb)
admin.site.register(Noncodingrna)
admin.site.register(Searchresults)
