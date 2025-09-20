"use client";

import { useState, useEffect } from "react";
import { onAuthStateChanged, User } from "firebase/auth";
import { auth } from "@/lib/firebase"; // Assuming firebase config is in lib
import { useRouter } from "next/navigation";
import { Login } from "@/components/Login";

export default function HomePage() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      setLoading(false);
    });

    // Cleanup subscription on unmount
    return () => unsubscribe();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (user) {
    // User is logged in, redirect to a protected route like a dashboard
    // Make sure you have a '/dashboard' page or change this to your desired route
    router.push("/dashboard");
    return <div>Redirecting to dashboard...</div>; // Or a loading spinner
  }

  // No user is logged in, show the Login component
  return <Login />;
}