import type { Preview } from '@storybook/sveltekit';

const preview: Preview = {
	parameters: {
		controls: {
			matchers: {
				color: /(background|color)$/i,
				date: /Date$/i
			}
		},

		// The reader arrives on a phone: stories open at phone width.
		viewport: {
			options: {
				phone: { name: 'Phone', styles: { width: '390px', height: '844px' }, type: 'mobile' },
				smallPhone: {
					name: 'Small phone',
					styles: { width: '320px', height: '568px' },
					type: 'mobile'
				},
				tablet: { name: 'Tablet', styles: { width: '820px', height: '1180px' }, type: 'tablet' },
				desktop: { name: 'Desktop', styles: { width: '1280px', height: '800px' }, type: 'desktop' }
			}
		},

		a11y: {
			// 'todo' - show a11y violations in the test UI only
			// 'error' - fail CI on a11y violations
			// 'off' - skip a11y checks entirely
			test: 'todo'
		}
	},
	initialGlobals: {
		viewport: { value: 'phone', isRotated: false }
	}
};

export default preview;
