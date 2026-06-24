export default function Card({ children, hover = false, className = "", style = {}, ...props }) {
  return (
    <div className={`card ${hover ? "card-hover" : ""} ${className}`} style={style} {...props}>
      {children}
    </div>
  );
}
