import * as Sentry from '@sentry/astro'

export function reportError(error: unknown, context?: Record<string, unknown>) {
  console.error(error)

  if (context) {
    Sentry.captureException(error, { extra: context })
  } else {
    Sentry.captureException(error)
  }
}
