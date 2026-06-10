export type AnalyticsPayload = Record<string, string | number | boolean | null | undefined>;

declare global {
  interface Window {
    umami?: {
      track?: (eventName: string, eventData?: AnalyticsPayload) => void | Promise<void>;
    };
  }
}

export function trackEvent(eventName: string, eventData: AnalyticsPayload = {}) {
  if (typeof window === "undefined") return;

  const payload = {
    path: window.location.pathname,
    title: document.title,
    ...eventData,
  };

  try {
    window.umami?.track?.(eventName, payload);
  } catch (error) {
    if (process.env.NODE_ENV !== "production") {
      console.warn("Umami event failed", eventName, error);
    }
  }
}
