interface LoginData {
  email: string;
  password: string;
}

interface RegisterData {
  email: string;
  password: string;
  role: string;
}

interface User {
  id: string;
  email: string;
  role: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class AuthService {
  private token: string | null = null;
  private user: User | null = null;

  constructor() {
    // Load token and user from localStorage on initialization
    this.token = localStorage.getItem('access_token');
    const userData = localStorage.getItem('user');
    if (userData) {
      try {
        this.user = JSON.parse(userData);
      } catch {
        localStorage.removeItem('user');
      }
    }
  }

  async login(data: LoginData): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Login failed');
    }

    const result = await response.json();
    
    // Check if the response has the expected structure
    // Backend returns "status": "success" not "success": true
    if (result.status !== "success" || !result.data) {
      throw new Error(result.message || 'Login failed - invalid response');
    }
    
    const authData = result.data as AuthResponse;

    // Validate that we have the required fields
    if (!authData.access_token) {
      throw new Error('No access token received');
    }

    // Store token and user data
    this.token = authData.access_token;
    this.user = authData.user;
    localStorage.setItem('access_token', authData.access_token);
    localStorage.setItem('user', JSON.stringify(authData.user));

    return authData;
  }

  async register(data: RegisterData): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Registration failed');
    }

    const result = await response.json();
    
    // Check if registration was successful
    if (result.status !== "success") {
      throw new Error(result.message || 'Registration failed');
    }
    
    return result;
  }

  async getCurrentUser(): Promise<User> {
    if (!this.token) {
      throw new Error('No authentication token');
    }

    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        this.logout();
      }
      const error = await response.json();
      throw new Error(error.message || 'Failed to get user profile');
    }

    const result = await response.json();
    this.user = result.data;
    localStorage.setItem('user', JSON.stringify(result.data));
    return result.data;
  }

  logout(): void {
    this.token = null;
    this.user = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  }

  getToken(): string | null {
    return this.token;
  }

  getUser(): User | null {
    return this.user;
  }

  isAuthenticated(): boolean {
    return this.token !== null && this.user !== null;
  }

  // Helper method to make authenticated API calls
  async authenticatedFetch(url: string, options: RequestInit = {}): Promise<Response> {
    if (!this.token) {
      throw new Error('No authentication token');
    }

    const headers = {
      'Authorization': `Bearer ${this.token}`,
      'Content-Type': 'application/json',
      ...options.headers,
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      this.logout();
      throw new Error('Authentication expired');
    }

    return response;
  }
}

export const authService = new AuthService();
export type { User, LoginData, RegisterData, AuthResponse };