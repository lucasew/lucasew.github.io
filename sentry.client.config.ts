import * as Sentry from '@sentry/astro'

const dsn =
  import.meta.env.PUBLIC_SENTRY_DSN ??
  'https://df310b7f294d8efd87f5d28526f5189d@o4508616651505664.ingest.us.sentry.io/4510216273330176'

Sentry.init({
  dsn,
  enabled: import.meta.env.PROD,
  tracesSampleRate: 0.1,
})
