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
					name: 'server',
					environment: 'node',
					include: ['src/**/*.{test,spec}.{js,ts}'],
					exclude: ['src/**/*.svelte.{test,spec}.{js,ts}']
				}
			},
			{
				// Renders every story in headless Chromium: a story that throws fails `pnpm test`.
				// See https://storybook.js.org/docs/writing-tests/integrations/vitest-addon
				extends: true,
				plugins: [storybookTest({ configDir: path.join(import.meta.dirname, '.storybook') })],
				test: {
					name: 'storybook',
					browser: {
						enabled: true,
						headless: true,
						// CHROMIUM_EXECUTABLE points at a preinstalled Chromium (e.g. /opt/pw-browsers/chromium in
						// Claude Code cloud sessions) instead of the one `playwright install` downloads.
						provider: playwright({
							launchOptions: { executablePath: process.env.CHROMIUM_EXECUTABLE || undefined }
						}),
						instances: [{ browser: 'chromium' }]
					}
				}
			}
		]
	}
});
