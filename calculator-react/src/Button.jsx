import { useContext } from "react";
import { ThemeContext } from "./ThemeContext";

export default function Button({ onClick, children, variant = "number", disabled = false }) {
  const theme = useContext(ThemeContext);
  const colors = {
    light: {
      number: "bg-gray-200 text-gray-900",
      utility: "bg-gray-300 text-gray-900",
      operator: "bg-orange-500 text-white",
      action: "bg-gray-200 text-gray-900",
    },
    dark: {
      number: "bg-gray-700 text-white",
      utility: "bg-gray-500 text-white",
      operator: "bg-orange-600 text-white",
      action: "bg-gray-700 text-white",
    },
  };

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={`${colors[theme][variant]} ${
        variant === "action"
          ? "rounded-full px-4 py-2 text-sm"
          : "h-16 w-16 rounded-full text-2xl font-bold"
      } flex items-center justify-center hover:opacity-80 disabled:opacity-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-orange-500`}
    >
      {children}
    </button>
  );
}
