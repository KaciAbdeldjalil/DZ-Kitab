import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  
  // NUCLEAR BUILD-TIME VALIDATION
  if (mode !== 'development' && (!env.VITE_API_URL || env.VITE_API_URL.includes("localhost"))) {
    console.error("\n\n################################################################");
    console.error("BUILD FAILURE: VITE_API_URL is missing or set to localhost!");
    console.error("Production builds must have a valid external API URL.");
    console.error("Found VITE_API_URL=" + env.VITE_API_URL);
    console.error("################################################################\n\n");
    process.exit(1);
  }

  return {
    plugins: [react()],
  }
})
