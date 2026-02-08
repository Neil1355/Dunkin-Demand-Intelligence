/// <reference types="vite/client" />
/**
 * API Client for Dunkin Demand Intelligence Backend
 * Base URL: https://dunkin-demand-intelligence.onrender.com/api/v1
 */

const API_BASE = import.meta.env.VITE_API_URL || "https://dunkin-demand-intelligence.onrender.com/api/v1";

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
  };
  message?: string;
}

export interface SignupRequest {
  name: string;
  email: string;
  password: string;
  store_address: string;
  store_number: string;
}

export interface SignupResponse {
  status: string;
  user?: {
    id: number;
    name: string;
    email: string;
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

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
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
    };

    if (data) {
      options.body = JSON.stringify(data);
    }

    try {
      console.debug(`API Request -> ${method} ${url}`, options);
      const response = await fetch(url, { ...options, mode: 'cors' });

      // Handle 401/403 - redirect to login
      if (response.status === 401 || response.status === 403) {
        localStorage.removeItem("user");
        localStorage.removeItem("auth_token");
        window.location.href = "/login";
        throw new Error("Unauthorized - please log in again");
      }

      if (!response.ok) {
        const errorText = await response.text();
        const msg = `API Error ${response.status} ${method} ${url}: ${errorText || response.statusText}`;
        console.error(msg);
        throw new Error(msg);
      }

      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        return await response.json();
      }

      return (await response.text()) as unknown as T;
    } catch (error) {
      console.error(`API Request Error [${method} ${url}]:`, error);
      throw new Error(`Network error while calling ${method} ${url}: ${error}`);
    }
  }

  /**
   * Login with email and password
   */
  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await this.request<LoginResponse>("/auth/login", "POST", {
      email,
      password,
    });

    // Store user info in localStorage
    if (response.status === "success" && response.user) {
      localStorage.setItem("user", JSON.stringify(response.user));
      localStorage.setItem("auth_token", response.user.id.toString());
    }

    return response;
  }

  /**
   * Signup new user
   */
  async signup(
    name: string,
    email: string,
    password: string,
    storeAddress: string,
    storeNumber: string
  ): Promise<SignupResponse> {
    const response = await this.request<SignupResponse>("/auth/signup", "POST", {
      name,
      email,
      password,
      store_address: storeAddress,
      store_number: storeNumber,
    });

    // Store user info in localStorage
    if (response.status === "success" && response.user) {
      localStorage.setItem("user", JSON.stringify(response.user));
      localStorage.setItem("auth_token", response.user.id.toString());
    }

    return response;
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
   * Get logged-in user from localStorage
   */
  getUser() {
    const userStr = localStorage.getItem("user");
    return userStr ? JSON.parse(userStr) : null;
  }

  /**
   * Clear user session
   */
  logout() {
    localStorage.removeItem("user");
    localStorage.removeItem("auth_token");
  }

  /**
   * Check if user is logged in
   */
  isLoggedIn(): boolean {
    return !!localStorage.getItem("auth_token");
  }
}

export const apiClient = new APIClient();