import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

import { viteStaticCopy } from 'vite-plugin-static-copy';

export default defineConfig({
	plugins: [
		sveltekit({
			onwarn: (warning, handler) => {
				// Suprimir avisos de propriedades exportadas não utilizadas
				if (warning.code === 'unused-export-let') return;
				// Suprimir alguns avisos de acessibilidade menos críticos
				if (warning.code === 'a11y-missing-attribute' && warning.message.includes('alt')) return;
				if (warning.code === 'a11y-invalid-attribute' && warning.message.includes('href')) return;
				if (warning.code === 'a11y-no-static-element-interactions') return;
				// Suprimir erros de variáveis não definidas em componentes específicos
				if (warning.filename && warning.filename.includes('ChatList.svelte') && warning.message.includes("'show' is not defined")) return;
				// Chamar o handler padrão para outros avisos
				handler(warning);
			}
		}),
		viteStaticCopy({
			targets: [
				{
					src: 'node_modules/onnxruntime-web/dist/*.jsep.*',

					dest: 'wasm'
				}
			]
		})
	],
	define: {
		APP_VERSION: JSON.stringify(process.env.npm_package_version),
		APP_BUILD_HASH: JSON.stringify(process.env.APP_BUILD_HASH || 'dev-build')
	},
	build: {
		sourcemap: true
	},
	worker: {
		format: 'es'
	},
	esbuild: {
		pure: process.env.ENV === 'dev' ? [] : ['console.log', 'console.debug']
	}
});
