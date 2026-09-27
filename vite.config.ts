import { defineConfig } from 'vitest/config';
import adapter from '@sveltejs/adapter-static';
import { sveltekit } from '@sveltejs/kit/vite';
import path from 'node:path';
import { storybookTest } from '@storybook/addon-vitest/vitest-plugin';
import { playwright } from '@vitest/browser-playwright';

export default defineConfig({
	plugins: [
		sveltekit({
			compilerOptions: {
				// Force runes mode for the project, except for libraries. Can be removed in svelte 6.
				runes: ({ filename }) =>
					filename.split(/[/\\]/).includes('node_modules') ? undefined : true
			},
			adapter: adapter(),
			paths: {
				// A GitHub Pages project site is served from /<repo>/. The deploy build sets
				// BASE_PATH=/but-the-sample-size; dev and Storybook serve from the root.
				base: (process.env.BASE_PATH ?? '') as '' | `/${string}`
			}
		})
	],
	test: {
		expect: { requireAssertions: true },
		projects: [
			{
				extends: './vite.config.ts',
				test: {
					name: 'unit',
					environment: 'node',
					include: ['src/**/*.{test,spec}.{js,ts}'],
					exclude: ['src/**/*.svelte.{test,spec}.{js,ts}']
				}
			},
			{
				// Renders every story in headless Chromium: a story that throws fails `pnpm test:stories`.
				// See https://storybook.js.org/docs/writing-tests/integrations/vitest-addon
				extends: true,
				plugins: [storybookTest({ configDir: path.join(import.meta.dirname, '.storybook') })],
				test: {
					name: 'storybook',
					browser: {
						enabled: true,
						headless: true,
						// Chromium runs in Playwright's official Docker image (scripts/playwright-server.sh);
						// '<loopback>' routes its requests for localhost back to this machine's Vitest server.
						// CHROMIUM_EXECUTABLE launches a preinstalled Chromium instead, for Claude Code cloud
						// sessions, which have one at /opt/pw-browsers/chromium and no Docker.
						provider: process.env.CHROMIUM_EXECUTABLE
							? playwright({ launchOptions: { executablePath: process.env.CHROMIUM_EXECUTABLE } })
							: playwright({
									connectOptions: {
										wsEndpoint: `ws://127.0.0.1:${process.env.PLAYWRIGHT_PORT ?? 53333}/`,
										exposeNetwork: '<loopback>'
									}
								}),
						instances: [{ browser: 'chromium' }]
					}
				}
			}
		]
	}
});
