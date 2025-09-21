import { useState, useEffect, createContext, useContext } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import { authService, User } from "@/services/auth";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, role: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({ 
  user: null, 
  loading: true, 
  token: null,
  login: async () => {},
  register: async () => {},
  logout: () => {}
});

export const useAuth = () => useContext(AuthContext);

export const Root = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const storedToken = authService.getToken();
        const storedUser = authService.getUser();

        if (storedToken && storedUser) {
          // Verify the token is still valid
          try {
            const currentUser = await authService.getCurrentUser();
            setUser(currentUser);
            setToken(storedToken);
          } catch (error) {
            // Token is invalid, clear stored data
            authService.logout();
            setUser(null);
            setToken(null);
          }
        }
      } catch (error) {
        console.error("Error initializing auth:", error);
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const authData = await authService.login({ email, password });
      setUser(authData.user);
      setToken(authData.access_token);
      navigate("/");
    } catch (error) {
      throw error;
    }
  };

  const register = async (email: string, password: string, role: string) => {
    try {
      await authService.register({ email, password, role });
      // After successful registration, user needs to login
      navigate("/login");
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
    setToken(null);
    navigate("/login");
  };

  return (
    <AuthContext.Provider value={{ user, loading, token, login, register, logout }}>
      {loading ? <div>Loading...</div> : <Outlet />}
    </AuthContext.Provider>
  );
};