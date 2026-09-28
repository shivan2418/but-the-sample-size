/** @type {import("prettier").Config} */
const config = {
	useTabs: true,
	singleQuote: true,
	trailingComma: 'none',
	printWidth: 100,
	plugins: ['prettier-plugin-svelte', 'prettier-plugin-tailwindcss'],
	tailwindStylesheet: './src/prototypes/visual-style/tw.css',
	overrides: [{ files: '*.svelte', options: { parser: 'svelte' } }]
};

export default config;
