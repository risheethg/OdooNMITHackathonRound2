"use client";

import { useState, useEffect, useCallback } from "react";
import { onAuthStateChanged, User } from "firebase/auth";
import { auth } from "@/lib/firebase"; // Assuming firebase config is in lib
import { useRouter } from "next/navigation";
import { Login } from "@/components/Login";

export default function HomePage() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [idToken, setIdToken] = useState<string | null>(null);
  const [backendUser, setBackendUser] = useState(null); // To store user data from our backend
  const [authChecked, setAuthChecked] = useState(false); // To prevent multiple API calls
  const router = useRouter();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (currentUser) => {
      setUser(currentUser);
      if (currentUser) {
        try {
          // Force refresh to get the latest claims if they have changed.
          const token = await currentUser.getIdToken(true);
          setIdToken(token);
        } catch (error) {
          console.error("Error getting ID token:", error);
          setIdToken(null);
          setLoading(false);
        }
      }
      setLoading(false); // Set loading to false after user and token are resolved
    });

    // Cleanup subscription on unmount
    return () => unsubscribe();
  }, [router]);

  const syncUserWithBackend = useCallback(async () => {
    if (!idToken || authChecked) return;

    setLoading(true);
    setAuthChecked(true); // Mark as checked to avoid re-running

    try {
      // First, try to get the user profile. This works if they are already registered.
      const tokenResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/token`, {
        method: "POST",
        headers: { Authorization: `Bearer ${idToken}` },
      });

      if (tokenResponse.ok) {
        const userData = await tokenResponse.json();
        setBackendUser(userData);
        router.push("/dashboard");
      } else if (tokenResponse.status === 404) {
        // User not found in our DB, so let's register them.
        const registerResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/register`, {
          method: "POST",
          headers: { Authorization: `Bearer ${idToken}` },
        });

        if (registerResponse.ok) {
          const newUser = await registerResponse.json();
          setBackendUser(newUser);
          router.push("/dashboard");
        } else {
          throw new Error("Failed to register user on the backend.");
        }
      }
    } catch (error) {
      console.error("Error syncing user with backend:", error);
      // Handle error, maybe sign out user and show an error message
    } finally {
      setLoading(false);
    }
  }, [idToken, router, authChecked]);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (user) {
    // You can now use the idToken for authenticated API calls
    // Once we have a user and a token, sync with the backend.
    syncUserWithBackend();

    // Show a loading/redirecting message while we sync and redirect.
    return <div>Authenticating...</div>;
  }

  // No user is logged in, show the Login component
  return <Login />;
}