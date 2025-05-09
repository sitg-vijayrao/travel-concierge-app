"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { useAuth, useUser } from "@clerk/nextjs";

interface SessionContextType {
  sessionId: string | null;
  setSessionId: (sessionId: string | null) => void;
  isLoading: boolean;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export function SessionProvider({ children }: { children: ReactNode }) {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { userId, isLoaded, isSignedIn } = useAuth();
  const { user } = useUser();

  useEffect(() => {
    // Load session from localStorage on initial render
    const storedSession = localStorage.getItem("sessionId");
    if (storedSession) {
      setSessionId(storedSession);
    }
    setIsLoading(false);
  }, []);

  useEffect(() => {
    // Create a new session when user logs in
    const createSession = async () => {
      if (isLoaded && isSignedIn && userId) {
        try {
          setIsLoading(true);
          const res = await fetch(
            `https://trvlcapi-164205107694.us-central1.run.app/api/v1/create_session/`,
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                user_id: user?.emailAddresses[0].emailAddress,
              }),
            }
          );

          const data = await res.json();
          if (data.session_id) {
            setSessionId(data.session_id);
            localStorage.setItem("sessionId", data.session_id);
          }
        } catch (error) {
          console.error("Error creating session:", error);
        } finally {
          setIsLoading(false);
        }
      } else if (isLoaded && !isSignedIn) {
        // Clear session when user logs out
        setSessionId(null);
        localStorage.removeItem("sessionId");
      }
    };

    createSession();
  }, [isLoaded, isSignedIn, userId]);

  // Save session to localStorage whenever it changes
  useEffect(() => {
    if (sessionId) {
      localStorage.setItem("sessionId", sessionId);
    }
  }, [sessionId]);

  return (
    <SessionContext.Provider value={{ sessionId, setSessionId, isLoading }}>
      {children}
    </SessionContext.Provider>
  );
}

export function useSession() {
  const context = useContext(SessionContext);
  if (context === undefined) {
    throw new Error("useSession must be used within a SessionProvider");
  }
  return context;
}
