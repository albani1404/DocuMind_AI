export const formatBytes = (n: number) =>
  n < 1024 ? `${n} B` : n < 1048576 ? `${(n / 1024).toFixed(1)} KB` : `${(n / 1048576).toFixed(1)} MB`;
export const formatDate = (s: string) =>
  new Date(s + (s.endsWith("Z") ? "" : "Z")).toLocaleString("id-ID", { dateStyle: "medium", timeStyle: "short" });
export const statusLabel: Record<string, string> = {
  uploaded: "Menunggu", processing: "Diproses", indexed: "Terindeks", failed: "Gagal",
};
