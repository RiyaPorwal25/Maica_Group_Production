from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:
    """
    Global middleware that requires authentication for ALL URLs,
    except a small whitelist of public endpoints (login page, static files, PWA, etc.).

    Also adds no-cache headers to every response so the browser never caches
    authenticated pages. This prevents the "back button after logout" problem
    where the browser shows a cached copy of a protected page.
    """

    # Paths that are always accessible without login
    PUBLIC_PATHS = [
        '/',                    # Login page
        '/login/',              # Login page (explicit)
        '/logout/',             # Logout (so users can always log out)
        '/admin/login/',        # Django admin login
        '/static/',             # Static files (CSS, JS, images)
        '/manifest.json',       # PWA manifest
        '/serviceworker.js',    # PWA service worker
        '/offline/',            # PWA offline page
        '/favicon.ico',         # Favicon
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # If user is already authenticated, allow access
        if request.user.is_authenticated:
            response = self.get_response(request)
            return self._add_no_cache_headers(response)

        # Check if the requested path is public
        path = request.path
        for public_path in self.PUBLIC_PATHS:
            if path == public_path or path.startswith(public_path):
                response = self.get_response(request)
                return self._add_no_cache_headers(response)

        # Not authenticated and not a public path -> redirect to login
        return redirect('/')

    def _add_no_cache_headers(self, response):
        """
        Prevent the browser from caching any page. This forces the browser
        to re-request the page from the server when the user presses Back,
        so the middleware can redirect logged-out users to the login page.
        """
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response