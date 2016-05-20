from django.contrib import admin
from manager.models import Package, Build


class PackageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'source')


admin.site.register(Package, PackageAdmin)


class BuildAdmin(admin.ModelAdmin):
    list_display = ('id', 'package', 'version', 'date', 'status')


admin.site.register(Build, BuildAdmin)
