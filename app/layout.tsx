{
  /* // @ts-ignore */
}
import "./globals.css";
import { GeistSans } from "geist/font/sans";
import { Toaster } from "sonner";
import { cn } from "@/lib/utils";
import { Navbar } from "@/components/navbar";
import {
  ClerkProvider,
  SignInButton,
  SignUpButton,
  SignedIn,
  SignedOut,
  UserButton,
} from "@clerk/nextjs";
import { SessionProvider } from "@/lib/session-context";

export const metadata = {
  title: "AI SDK Python Streaming Preview",
  description:
    "Use the Data Stream Protocol to stream chat completions from a Python endpoint (FastAPI) and display them using the useChat hook in your Next.js application.",
  openGraph: {
    images: [
      {
        url: "/og?title=AI SDK Python Streaming Preview",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    images: [
      {
        url: "/og?title=AI SDK Python Streaming Preview",
      },
    ],
  },
};

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider
      dynamic
      publishableKey="pk_test_dXNhYmxlLWJvYmNhdC02MS5jbGVyay5hY2NvdW50cy5kZXYk"
    >
      <html lang="en" suppressHydrationWarning>
        <head></head>
        <body className={cn(GeistSans.className, "antialiased dark")}>
          <SessionProvider>
            <Toaster position="top-center" richColors />
            <Navbar />
            {children}
          </SessionProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}
