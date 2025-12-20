import { Toaster as HotToaster } from "react-hot-toast";

/**
 * Toast notification component using react-hot-toast
 * Provides a consistent design for all toast notifications
 */
export const Toaster = () => {
  return (
    <HotToaster
      position="top-right"
      toastOptions={{
        duration: 4000,
        style: {
          background: "var(--toast-bg)",
          color: "var(--toast-color)",
          padding: "16px",
          borderRadius: "12px",
          boxShadow:
            "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)",
          maxWidth: "500px",
        },
        success: {
          iconTheme: {
            primary: "#16a34a",
            secondary: "#fff",
          },
          style: {
            background: "#f0fdf4",
            color: "#166534",
            border: "1px solid #bbf7d0",
          },
        },
        error: {
          iconTheme: {
            primary: "#dc2626",
            secondary: "#fff",
          },
          style: {
            background: "#fef2f2",
            color: "#991b1b",
            border: "1px solid #fecaca",
          },
        },
        loading: {
          iconTheme: {
            primary: "#0284c7",
            secondary: "#fff",
          },
          style: {
            background: "#f0f9ff",
            color: "#075985",
            border: "1px solid #bae6fd",
          },
        },
      }}
    />
  );
};

export default Toaster;
