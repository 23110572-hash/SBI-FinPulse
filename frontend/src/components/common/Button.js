export default function Button({ children, variant = "primary", size = "", block = false, className = "", ...props }) {
  return (
    <button
      className={`btn btn-${variant} ${size === "sm" ? "btn-sm" : ""} ${block ? "btn-block" : ""} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
