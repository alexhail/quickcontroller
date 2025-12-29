const registeredApps = new Map()

export function registerApp(manifest) {
  // manifest: { appId, displayName, icon, defaultApp, routes, subscriptions }
  if (registeredApps.has(manifest.appId)) {
    console.warn(`App '${manifest.appId}' already registered`)
    return
  }
  registeredApps.set(manifest.appId, manifest)
}

export function getApp(appId) {
  return registeredApps.get(appId)
}

export function getAllApps() {
  return Array.from(registeredApps.values())
}

// Initialize and register all apps
export async function initializeApps() {
  // Import and register Command Center app
  const commandCenterApp = await import('../command_center/index.js')
  registerApp(commandCenterApp.default)

  // Future apps will be imported and registered here
}
