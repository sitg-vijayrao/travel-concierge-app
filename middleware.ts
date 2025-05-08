import { clerkMiddleware } from '@clerk/nextjs/server'

export default clerkMiddleware(async (auth, req, res) => {
  const session = (await auth()).sessionId;
  const isSignInPage = req.nextUrl.pathname === '/sign-in';
  
  if (session && isSignInPage) {
    // This might catch some login events
    const res = await fetch(`${req.nextUrl.origin}/api/handle-login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        userId: (await auth()).userId 
      })
    });
  }
  await auth.protect()
})


export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
}