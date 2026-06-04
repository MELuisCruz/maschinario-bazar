// Shared geometric line icons (1.6px stroke, currentColor)
const Icon = {
  scan: (p) => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}>
      <path d="M3 7V4h3M21 7V4h-3M3 17v3h3M21 17v3h-3" />
      <path d="M6 8v8M9 8v8M12 8v8M15 8v8M18 8v8" strokeWidth="1.3" />
    </svg>
  ),
  cart: (p) => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}>
      <path d="M3 4h2l2.2 11h10l2-7H6" /><circle cx="9" cy="20" r="1.4" /><circle cx="17" cy="20" r="1.4" />
    </svg>
  ),
  box: (p) => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}>
      <path d="M3 7l9-4 9 4v10l-9 4-9-4V7z" /><path d="M3 7l9 4 9-4M12 11v10" />
    </svg>
  ),
  cut: (p) => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}>
      <rect x="3" y="5" width="18" height="14" rx="1.5" /><path d="M3 10h18M8 5v14" />
    </svg>
  ),
  search: (p) => (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...p}>
      <circle cx="11" cy="11" r="7" /><path d="m20 20-3.2-3.2" />
    </svg>
  ),
  trash: (p) => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}>
      <path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13" />
    </svg>
  ),
  cash: (p) => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}>
      <rect x="2" y="6" width="20" height="12" rx="1.5" /><circle cx="12" cy="12" r="2.6" /><path d="M5 9v6M19 9v6" strokeWidth="1.2" />
    </svg>
  ),
  card: (p) => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}>
      <rect x="2" y="5" width="20" height="14" rx="2" /><path d="M2 9h20M5 15h5" />
    </svg>
  ),
  check: (p) => (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" {...p}>
      <path d="M5 12.5l4.5 4.5L19 7.5" />
    </svg>
  ),
  checkSm: (p) => (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" {...p}>
      <path d="M5 12.5l4.5 4.5L19 7.5" />
    </svg>
  ),
  plus: (p) => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" {...p}>
      <path d="M12 5v14M5 12h14" />
    </svg>
  ),
  alert: (p) => (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...p}>
      <path d="M12 3 2 20h20L12 3z" /><path d="M12 10v4M12 17v.5" />
    </svg>
  ),
  ret: (p) => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}>
      <path d="M9 14 4 9l5-5" /><path d="M4 9h11a5 5 0 0 1 5 5v0a5 5 0 0 1-5 5H8" />
    </svg>
  ),
  report: (p) => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}>
      <path d="M4 20V4" /><path d="M4 20h16" /><path d="M8 20v-6M13 20V8M18 20v-9" />
    </svg>
  ),
  printer: (p) => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}>
      <path d="M6 9V3h12v6" /><path d="M6 18H4a2 2 0 0 1-2-2v-4a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2h-2" />
      <rect x="6" y="14" width="12" height="7" rx="1" /><path d="M9 17h6" strokeWidth="1.2" />
    </svg>
  ),
  cal: (p) => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}>
      <rect x="3" y="5" width="18" height="16" rx="1.5" /><path d="M3 9h18M8 3v4M16 3v4" />
    </svg>
  ),
  user: (p) => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}>
      <circle cx="12" cy="8" r="3.4" /><path d="M5 20a7 7 0 0 1 14 0" />
    </svg>
  ),
  export: (p) => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}>
      <path d="M12 15V3m0 0 4 4m-4-4-4 4" /><path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" />
    </svg>
  ),
};
window.Icon = Icon;
