import { useState, useEffect, createContext, useContext, useCallback } from "react";
import { onAuthStateChanged, User } from "firebase/auth";
import { auth } from "@/firebase";
import { Outlet, useNavigate } from "react-router-dom";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  backendUser: any | null; // To store user data from your backend
  idToken: string | null;
}

const AuthContext = createContext<AuthContextType>({ user: null, loading: true, backendUser: null, idToken: null });

export const useAuth = () => useContext(AuthContext);

export const Root = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [idToken, setIdToken] = useState<string | null>(null);
  const [backendUser, setBackendUser] = useState(null);
  const [authChecked, setAuthChecked] = useState(false);
  const navigate = useNavigate();

  const syncUserWithBackend = useCallback(async (token: string) => {
    if (!token || authChecked) return;

    setAuthChecked(true); // Mark as checked to avoid re-running

    try {
      // First, try to get the user profile. This works if they are already registered.
      const tokenResponse = await fetch(`${import.meta.env.VITE_API_URL}/auth/token`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (tokenResponse.ok) {
        const userData = await tokenResponse.json();
        setBackendUser(userData);
      } else if (tokenResponse.status === 404) {
        // User not found in our DB, so let's register them.
        const registerResponse = await fetch(`${import.meta.env.VITE_API_URL}/auth/register`, {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
        });

        if (registerResponse.ok) {
          const newUser = await registerResponse.json();
          setBackendUser(newUser);
        } else {
          throw new Error("Failed to register user on the backend.");
        }
      }
    } catch (error) {
      console.error("Error syncing user with backend:", error);
      // Handle error, maybe sign out user and show an error message
    }
  }, [authChecked]);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (currentUser) => {
      setUser(currentUser);
      if (currentUser) {
        const token = await currentUser.getIdToken(true);
        setIdToken(token);
        await syncUserWithBackend(token);
      } else {
        // User logged out
        setIdToken(null);
        setBackendUser(null);
        setAuthChecked(false);
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, [syncUserWithBackend]);

  return (
    <AuthContext.Provider value={{ user, loading, backendUser, idToken }}>
      {loading ? <div>Loading...</div> : <Outlet />}
    </AuthContext.Provider>
  );
};