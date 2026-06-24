"use client";
import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";

export default function Modal({ open, onClose, title, children, width = 520 }) {
  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          style={{
            position: "fixed", inset: 0, background: "rgba(26,35,126,0.35)",
            backdropFilter: "blur(4px)", display: "flex", alignItems: "center",
            justifyContent: "center", zIndex: 1000, padding: 16,
          }}
        >
          <motion.div
            initial={{ scale: 0.92, y: 20, opacity: 0 }}
            animate={{ scale: 1, y: 0, opacity: 1 }}
            exit={{ scale: 0.95, opacity: 0 }}
            transition={{ type: "spring", stiffness: 280, damping: 26 }}
            onClick={(e) => e.stopPropagation()}
            className="card"
            style={{ width, maxWidth: "100%", maxHeight: "85vh", overflow: "auto" }}
          >
            <div className="flex items-center justify-between" style={{ marginBottom: 16 }}>
              <h3 style={{ fontSize: "var(--text-xl)" }}>{title}</h3>
              <button onClick={onClose} style={{ color: "var(--text-tertiary)" }}>
                <X size={20} />
              </button>
            </div>
            {children}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
