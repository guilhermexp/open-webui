import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import { execSync } from 'child_process';

// Get git commit hash for build version
let commitHash = 'dev';
try {
	commitHash = execSync('git rev-parse --short HEAD').toString().trim();
} catch (error) {
	console.warn('Could not get git commit hash:', error);
}

export default defineConfig({
	plugins: [sveltekit()],
	define: {
		APP_VERSION: JSON.stringify('0.6.18'),
		APP_BUILD_HASH: JSON.stringify(commitHash)
	},
	server: {
		port: 5173,
		proxy: {
			'/api': {
				target: 'http://localhost:8084',
				changeOrigin: true,
        secure: false
      },
      // Proxy backend websockets for Socket.IO
      '/ws': {
        target: 'http://localhost:8084',
        changeOrigin: true,
        ws: true
      },
      // Proxy backend static files (favicons, assets) during dev
      '/static': {
        target: 'http://localhost:8084',
        changeOrigin: true
      },
      '/favicon.png': {
        target: 'http://localhost:8084',
        changeOrigin: true
			}
		}
	}
});
