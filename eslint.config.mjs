import eslintConfig from '@eslint-sets/eslint-config'

export default eslintConfig({
	type: 'lib',
	ignores: ['skills/**', 'eval-viewer/**', '.venv/**'],
	markdown: false,
	python: true,
	react: false,
	rules: {
		'style/indent-binary-ops': 'off',
	},
	stylistic: {
		indent: 'tab',
	},
	typescript: true,
})
