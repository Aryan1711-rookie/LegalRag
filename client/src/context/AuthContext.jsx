
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";

import {
  loginUser,
  logoutUser,
  getCurrentUser,
} from "../services/auth";

// Create authentication context
const AuthContext = createContext(null);

// Context provider
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [authError, setAuthError] = useState(null);

  // Restore existing session
  const refreshUser = useCallback(async () => {
    setIsLoading(true);
    setAuthError(null);

    try {
      const currentUser = await getCurrentUser();
      setUser(currentUser);
      return currentUser;
    } catch (error) {
      setAuthError(error.message);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Restore session when application starts
  useEffect(() => {
    let isMounted = true;

    async function initializeAuth() {
      try {
        const currentUser = await getCurrentUser();

        if (isMounted) {
          setUser(currentUser);
        }
      } catch (error) {
        if (isMounted) {
          setAuthError(error.message);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    initializeAuth();

    return () => {
      isMounted = false;
    };
  }, []);

  // Login
  const login = useCallback(async (credentials) => {
    setIsLoading(true);
    setAuthError(null);

    try {
      await loginUser(credentials);

      const currentUser = await getCurrentUser();

      if (!currentUser) {
        throw new Error("Unable to retrieve authenticated user.");
      }

      setUser(currentUser);

      return currentUser;
    } catch (error) {
      setAuthError(error.message);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Logout
  const logout = useCallback(() => {
    logoutUser();
    setUser(null);
    setAuthError(null);
  }, []);

  const value = {
    user,
    isLoading,
    isAuthenticated: Boolean(user),
    authError,
    login,
    logout,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook
export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used inside an AuthProvider.");
  }

  return context;
}
