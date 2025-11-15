import { withAuth } from "next-auth/middleware";
import { NextResponse } from "next/server";

export default withAuth(
  function middleware(req) {
    const token = req.nextauth.token;
    const isAuth = !!token;
    const isAuthPage = req.nextUrl.pathname === "/";
    const isProtectedRoute = ["/dashboard", "/plan", "/chat", "/clubs"].some(
      (route) => req.nextUrl.pathname.startsWith(route)
    );

    // If user is authenticated and trying to access landing page, redirect to dashboard
    if (isAuthPage && isAuth) {
      return NextResponse.redirect(new URL("/dashboard", req.url));
    }

    // If user is not authenticated and trying to access protected routes, redirect to landing
    if (isProtectedRoute && !isAuth) {
      const redirectUrl = new URL("/", req.url);
      redirectUrl.searchParams.set("callbackUrl", req.nextUrl.pathname);
      return NextResponse.redirect(redirectUrl);
    }

    return NextResponse.next();
  },
  {
    callbacks: {
      authorized: () => true, // We handle authorization logic in the middleware function above
    },
  }
);

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    "/((?!api|_next/static|_next/image|favicon.ico).*)",
  ],
};
