import * as Sentry from '@sentry/astro';

/**
 * Centralized error reporting function.
 * Funnels all unexpected errors to Sentry if available, otherwise logs with context.
 *
 * @param error The error object to report.
 * @param context Optional additional context information.
 */
export function reportError(error: unknown, context?: Record<string, unknown>): void {
  const errorObj = error instanceof Error ? error : new Error(String(error));

  if (typeof Sentry.captureException === 'function') {
    Sentry.captureException(errorObj, { extra: context });
  } else {
    // Fallback if Sentry is not initialized
    console.error('Captured Error:', errorObj.message);
    if (context) {
      console.error('Error Context:', context);
    }
    console.error('Stack Trace:', errorObj.stack);
  }
}
