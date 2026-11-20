import type { CSSProperties, ReactNode } from "react";

export const page: CSSProperties = {
  maxWidth: 420,
  margin: "0 auto",
  padding: "24px 16px",
  fontFamily: "system-ui, -apple-system, Segoe UI, sans-serif",
};

export const field: CSSProperties = {
  display: "block",
  width: "100%",
  padding: "10px 12px",
  marginTop: 4,
  marginBottom: 12,
  fontSize: 16,
  borderRadius: 8,
  border: "1px solid #c9ccd3",
  boxSizing: "border-box",
};

export const button: CSSProperties = {
  width: "100%",
  padding: "12px 14px",
  fontSize: 16,
  borderRadius: 8,
  border: "none",
  background: "#0f6b5c",
  color: "#fff",
  cursor: "pointer",
};

export function Notice({
  tone,
  children,
}: {
  tone: "error" | "ok";
  children: ReactNode;
}) {
  const colors =
    tone === "error"
      ? { bg: "#fbe9e7", fg: "#8a1c0f" }
      : { bg: "#dcefe9", fg: "#0f6b5c" };
  return (
    <p
      role={tone === "error" ? "alert" : "status"}
      style={{
        background: colors.bg,
        color: colors.fg,
        padding: "10px 12px",
        borderRadius: 8,
      }}
    >
      {children}
    </p>
  );
}
