from django.contrib import admin
from manager.models import Package, Build


class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'source')


admin.site.register(Package, PackageAdmin)


class BuildAdmin(admin.ModelAdmin):
    list_display = ('package', 'version', 'date')


admin.site.register(Build, BuildAdmin)
