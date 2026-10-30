import type { DocStatus } from "../types";
import { statusLabel } from "../utils/format";

export default function StatusBadge({ status }: { status: DocStatus }) {
  return <span className={`badge ${status}`}>{statusLabel[status]}</span>;
}
