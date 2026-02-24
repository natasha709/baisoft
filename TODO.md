co# Fix Middleware Order Issue

## Problem
`APILoggingMiddleware` and `APIErrorHandlerMiddleware` try to access `request.user` before Django's `AuthenticationMiddleware` has added it to the request object.

## Tasks
- [x] Reorder MIDDLEWARE in settings.py to place AuthenticationMiddleware before custom middleware
