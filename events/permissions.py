from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        
        return self.author == request.user
    

class isAuthor(BasePermission):

    
    def has_permission(self, request, view):
        return getattr(request.user, 'is_authenticated', False) and getattr(request.user, 'is_creator', False)


    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        
        return getattr(request.user, "is_creator", False)