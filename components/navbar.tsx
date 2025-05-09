"use client";

import { SignedIn, UserButton } from "@clerk/nextjs";
import { useSession } from "@/lib/session-context";

export const Navbar = () => {
  const { sessionId, isLoading } = useSession();

  return (
    <div className="p-2 flex flex-row gap-2 justify-between items-center">
      <div className="flex items-center gap-2">
        <SignedIn>
          <UserButton />
        </SignedIn>
      </div>

      <div className="text-sm text-gray-400">
        {isLoading ? (
          "Loading session..."
        ) : sessionId ? (
          <span>Session ID: {sessionId}</span>
        ) : (
          <SignedIn>
            <span>No active session</span>
          </SignedIn>
        )}
      </div>
    </div>
  );
};
