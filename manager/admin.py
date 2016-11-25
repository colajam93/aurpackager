from django.contrib import admin

from manager.models import Package, Build, Artifact


class PackageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


admin.site.register(Package, PackageAdmin)


class BuildAdmin(admin.ModelAdmin):
    list_display = ('id', 'package', 'version', 'date', 'status')


admin.site.register(Build, BuildAdmin)


class ArtifactAdmin(admin.ModelAdmin):
    list_display = ('id', 'package', 'name')


admin.site.register(Artifact, ArtifactAdmin)
