/// <reference types="vite/client" />

// Add app-specific env types so `import.meta.env.VITE_API_URL` is known to TS
interface ImportMetaEnv {
	readonly VITE_API_URL?: string;
	// add other env variables here as needed
}

interface ImportMeta {
	readonly env: ImportMetaEnv;
}
