type RuntimeConfig = {
  apiUrl?: string;
  wsUrl?: string;
};

declare global {
  interface Window {
    __ONESHOT_RUNTIME_CONFIG__?: RuntimeConfig;
  }
}

function toWebSocketUrl(value: string): string {
  if (value.startsWith("ws://") || value.startsWith("wss://")) {
    return value;
  }

  if (value.startsWith("https://")) {
    return `wss://${value.slice("https://".length)}`;
  }

  if (value.startsWith("http://")) {
    return `ws://${value.slice("http://".length)}`;
  }

  return value;
}

export function getRuntimeApiBase(): string {
  if (typeof window !== "undefined") {
    const configured = window.__ONESHOT_RUNTIME_CONFIG__?.apiUrl?.trim();
    if (configured) return configured;

    // Fallback to same-origin so deployed environments don't default to localhost.
    return window.location.origin;
  }

  return process.env.NEXT_PUBLIC_API_URL?.trim() || "http://localhost:8000";
}

export function getRuntimeWsBase(): string {
  if (typeof window !== "undefined") {
    const configuredWs = window.__ONESHOT_RUNTIME_CONFIG__?.wsUrl?.trim();
    if (configuredWs) return configuredWs;

    const configuredApi = window.__ONESHOT_RUNTIME_CONFIG__?.apiUrl?.trim();
    if (configuredApi) return toWebSocketUrl(configuredApi);

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${protocol}//${window.location.host}`;
  }

  const fromEnvWs = process.env.NEXT_PUBLIC_WS_URL?.trim();
  if (fromEnvWs) return fromEnvWs;

  const fromEnvApi = process.env.NEXT_PUBLIC_API_URL?.trim();
  if (fromEnvApi) return toWebSocketUrl(fromEnvApi);

  return "ws://localhost:8000";
}

export {};