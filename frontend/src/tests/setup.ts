import "@testing-library/jest-dom";
import { beforeAll, beforeEach, afterEach, afterAll, vi } from "vitest";
import { server } from "./mocks/server";

// Stub environment variables
vi.stubEnv("VITE_API_URL", "http://localhost:8000");

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value.toString(); },
    removeItem: (key: string) => { delete store[key]; },
    clear: () => { store = {}; },
  };
})();
Object.defineProperty(window, "localStorage", { value: localStorageMock });

// Mock window.location
const locationMock = { href: "" };
Object.defineProperty(window, "location", {
  value: locationMock,
  writable: true
});

// Mock ResizeObserver
class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}
Object.defineProperty(window, "ResizeObserver", { value: ResizeObserverMock });

Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => {},
  }),
});

// Setup MSW lifecycle
beforeAll(() => server.listen({ onUnhandledRequest: "warn" }));
beforeEach(() => {
  localStorage.setItem("omnitrader_api_key", "test-api-key");
});
afterEach(() => {
  server.resetHandlers();
  localStorage.clear();
});
afterAll(() => server.close());
