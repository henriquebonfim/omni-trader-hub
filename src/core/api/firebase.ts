import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";

const firebaseConfig = {
  apiKey: "AIzaSyBmPWZUs5dfwi1E7KkyXS6tjzW20er6cQg",
  authDomain: "omni-trader.firebaseapp.com",
  projectId: "omni-trader",
  storageBucket: "omni-trader.firebasestorage.app",
  messagingSenderId: "8451173174",
  appId: "1:8451173174:web:f95c85b5cb8ea9a8eba197",
  measurementId: "G-F8C9E0VVG8"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Analytics (only in browser environments)
export const analytics = typeof window !== "undefined" ? getAnalytics(app) : null;

export default app;