const isDev = import.meta.env.DEV;

export const logger = {
  info: (...args: unknown[]) => {
    if (isDev) {
      console.info('[AirAd]', ...args);
    }
  },
  warn: (...args: unknown[]) => {
    if (isDev) {
      console.warn('[AirAd]', ...args);
    }
  },
  error: (...args: unknown[]) => {
    console.error('[AirAd]', ...args);
  },
};
