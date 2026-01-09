"""
Error handler views for Quiporder.

These views are triggered by Django when specific HTTP errors occur.
They render custom error pages with user-friendly messaging.
"""

from django.shortcuts import render


def error_403(request, exception):
    """
    Handle 403 Forbidden errors.

    Triggered when user doesn't have permission to access a resource.

    Args:
        request: HttpRequest object
        exception: The exception that triggered this view

    Returns:
        HttpResponse with 403 status code
    """
    return render(request, 'errors/403.html', status=403)


def error_404(request, exception):
    """
    Handle 404 Not Found errors.

    Triggered when requested URL doesn't exist.

    Args:
        request: HttpRequest object
        exception: The exception that triggered this view

    Returns:
        HttpResponse with 404 status code
    """
    return render(request, 'errors/404.html', status=404)


def error_405(request, exception):
    """
    Handle 405 Method Not Allowed errors.

    Triggered when HTTP method (GET/POST/etc) is not allowed for endpoint.

    Args:
        request: HttpRequest object
        exception: The exception that triggered this view

    Returns:
        HttpResponse with 405 status code
    """
    return render(request, 'errors/405.html', status=405)


def error_500(request):
    """
    Handle 500 Internal Server Error.

    Triggered when unhandled exception occurs in application code.
    Note: This view receives no exception parameter.

    Args:
        request: HttpRequest object

    Returns:
        HttpResponse with 500 status code
    """
    return render(request, 'errors/500.html', status=500)
