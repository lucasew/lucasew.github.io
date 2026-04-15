import * as Sentry from '@sentry/astro';

/**
 * Centralized error reporting function.
 * Ensures all unexpected errors are reported to Sentry with context.
 */
export function reportError(error: unknown, context?: Record<string, unknown>): void {
  Sentry.captureException(error, { extra: context });
  console.error("Reported error:", error, context);
}
