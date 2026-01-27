import axios from 'axios';
import { getCookie } from './cookies';

/**
 * PRODUCTION API CONFIGURATION
 * This file is the single source of truth for backend communication.
 * Environment variables are injected at BUILD TIME by Vite.
 */

const VITE_API_URL = import.meta.env.VITE_API_URL;

// NUCLEAR PROD VALIDATION
if (!VITE_API_URL || (import.meta.env.PROD && VITE_API_URL.includes("localhost"))) {
    const errorMsg = "CRITICAL ERROR: VITE_API_URL is missing or contains 'localhost'. " +
                    "Production builds require a valid external API URL. " +
                    "Value found: " + VITE_API_URL;
    console.error(errorMsg);
    throw new Error(errorMsg);
}

const BASE_URL = VITE_API_URL.replace(/\/$/, "");

const api = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// AUTH INTERCEPTOR - Injects JWT into every request
api.interceptors.request.use(
    (config) => {
        const token = getCookie('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

export default api;

