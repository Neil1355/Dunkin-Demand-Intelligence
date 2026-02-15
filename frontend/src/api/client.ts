/// <reference types="vite/client" />
/**
 * API Client for Dunkin Demand Intelligence Backend
 * Base URL: https://dunkin-demand-intelligence.onrender.com/api/v1
 */

const API_BASE = import.meta.env.VITE_API_URL || "https://dunkin-demand-intelligence.onrender.com/api/v1";

export interface User {
  id: number;
  name: string;
  email: string;
  store_id?: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  status: string;
  user?: {
    id: number;
    name: string;
    email: string;
    store_id?: number;
  };
  message?: string;
}

export interface SignupRequest {
  name: string;
  email: string;
  password: string;
}

export interface SignupResponse {
  status: string;
  user?: {
    id: number;
    name: string;
    email: string;
    store_id?: number;
  };
  message?: string;
}

export interface Product {
  product_id: number;
  product_name: string;
  product_type: string;
  is_active: boolean;
}

export interface ForecastResponse {
  forecast_value: number;
  confidence_interval?: {
    lower: number;
    upper: number;
  };
  [key: string]: any;
}

export interface HealthResponse {
  status: string;
  database: string;
  version: string;
}

class APIClient {
  private baseUrl: string;
  private currentUser: User | null = null;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
    // Load user from sessionStorage if available (temporary storage, cleared on page close)
    const storedUser = sessionStorage.getItem("user");
    if (storedUser) {
      try {
        this.currentUser = JSON.parse(storedUser);
      } catch (e) {
        console.warn("Could not parse stored user");
      }
    }
  }

  private async request<T>(
    endpoint: string,
    method: string,
    data?: any
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const options: RequestInit = {
      method: method,
      headers: {
        "Content-Type": "application/json",
      },
      // CRITICAL: Include credentials to send httpOnly cookies
      credentials: 'include',
    };

    if (data) {
      options.body = JSON.stringify(data);
    }

    try {
      console.debug(`API Request -> ${method} ${url}`, options);
      const response = await fetch(url, options);

      // Handle 401/403 - redirect to login (except for auth endpoints themselves)
      if (response.status === 401 || response.status === 403) {
        // Don't redirect if this is already an auth endpoint
        if (!endpoint.includes('/auth/login') && !endpoint.includes('/auth/signup')) {
          this.logout();
          window.location.href = "/login";
          throw new Error("Unauthorized - please log in again");
        }
      }

      if (!response.ok) {
        const errorText = await response.text();
        let userMessage = response.statusText;
        
        // Try to parse JSON error response for user-friendly message
        try {
          const errorJson = JSON.parse(errorText);
          if (errorJson.message) {
            userMessage = errorJson.message;
          }
        } catch (e) {
          // If not JSON, use the raw text if it's short enough
          if (errorText && errorText.length < 100) {
            userMessage = errorText;
          }
        }
        
        // Log technical details for debugging
        console.error(`API Error ${response.status} ${method} ${url}:`, errorText);
        
        // Throw user-friendly message
        throw new Error(userMessage);
      }

      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        return await response.json();
      }

      return (await response.text()) as unknown as T;
    } catch (error) {
      // If it's already our formatted error, just re-throw it
      if (error instanceof Error && !error.message.includes('Network error')) {
        throw error;
      }
      
      // Otherwise it's a network/fetch error
      console.error(`API Request Error [${method} ${url}]:`, error);
      throw new Error('Network error. Please check your connection and try again.');
    }
  }

  /**
   * Login with email and password
   * Authentication token is stored in httpOnly cookie by backend
   */
  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await this.request<LoginResponse>("/auth/login", "POST", {
      email,
      password,
    });

    // Store user info in sessionStorage only (not localStorage - more secure)
    if (response.status === "success" && response.user) {
      this.currentUser = response.user;
      sessionStorage.setItem("user", JSON.stringify(response.user));
      // Auth token is now in httpOnly cookie (not in sessionStorage)
    }

    return response;
  }

  /**
   * Signup new user
   * Authentication token is stored in httpOnly cookie by backend
   */
  async signup(
    name: string,
    email: string,
    password: string
  ): Promise<SignupResponse> {
    const response = await this.request<SignupResponse>("/auth/signup", "POST", {
      name,
      email,
      password,
    });

    // Store user info in sessionStorage only
    if (response.status === "success" && response.user) {
      this.currentUser = response.user;
      sessionStorage.setItem("user", JSON.stringify(response.user));
      // Auth token is now in httpOnly cookie
    }

    return response;
  }

  /**
   * Logout user - clears session and calls backend to clear cookies
   */
  async logout(): Promise<void> {
    try {
      await this.request<any>("/auth/logout", "POST");
    } catch (e) {
      console.warn("Logout request failed:", e);
    }
    
    // Clear client-side session
    this.currentUser = null;
    sessionStorage.removeItem("user");
    // httpOnly cookies are cleared by backend
  }

  /**
   * Get all products
   */
  async getProducts(): Promise<Product[]> {
    return this.request<Product[]>("/products/list", "GET");
  }

  /**
   * Get forecast for a store
   */
  async getForecast(
    storeId: number,
    targetDate?: string
  ): Promise<ForecastResponse> {
    const params = new URLSearchParams();
    params.append("store_id", storeId.toString());
    if (targetDate) {
      params.append("target_date", targetDate);
    }
    return this.request<ForecastResponse>(`/forecast?${params.toString()}`, "GET");
  }

  /**
   * Get inventory
   */
  async getInventory(): Promise<any> {
    return this.request<any>("/inventory", "GET");
  }

  /**
   * Health check
   */
  async health(): Promise<HealthResponse> {
    return this.request<HealthResponse>("/health", "GET");
  }

  /**
   * Get logged-in user from session memory
   */
  getUser(): User | null {
    return this.currentUser;
  }

  /**
   * Check if user is logged in
   * httpOnly cookies are automatically sent and validated by backend
   */
  isLoggedIn(): boolean {
    return this.currentUser !== null;
  }
}

export const apiClient = new APIClient();