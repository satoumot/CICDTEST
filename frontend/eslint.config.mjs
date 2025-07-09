import { dirname } from 'path';
import { fileURLToPath } from 'url';
import { FlatCompat } from '@eslint/eslintrc';
import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';
import eslintConfigPrettier from 'eslint-config-prettier';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
    baseDirectory: __dirname,
});

export default tseslint.config(
    {
        files: ['**/*.{ts,tsx}'],
    },
    {
        ignores: ['**/.next/**/*', '*.config.mjs'],
    },
    eslint.configs.recommended,
    ...compat.extends('next/core-web-vitals'),
    {
        plugins: {
            '@typescript-eslint': tseslint.plugin,
        },
        languageOptions: {
            parser: tseslint.parser,
            parserOptions: {
                project: true,
                tsconfigRootDir: __dirname,
            },
        },
        rules: {
            '@typescript-eslint/naming-convention': [
                'error',
                {
                    selector: 'variable',
                    format: ['strictCamelCase', 'PascalCase'],
                },
                {
                    selector: 'function',
                    format: ['strictCamelCase', 'PascalCase'],
                },
                {
                    selector: 'class',
                    format: ['StrictPascalCase'],
                },
                {
                    selector: 'classMethod',
                    format: ['strictCamelCase'],
                },
                {
                    selector: 'classProperty',
                    format: ['strictCamelCase'],
                },
                {
                    selector: 'interface',
                    format: ['StrictPascalCase'],
                },
                {
                    selector: 'typeAlias',
                    format: ['StrictPascalCase'],
                },
                {
                    selector: 'typeMethod',
                    format: ['strictCamelCase'],
                },
                {
                    selector: 'typeProperty',
                    format: ['strictCamelCase'],
                },
                {
                    selector: 'enum',
                    format: ['StrictPascalCase'],
                },
                {
                    selector: 'enumMember',
                    format: ['StrictPascalCase'],
                },
            ],
        },
    },
    {
        files: ['src/**/*.{js,jsx,ts,tsx}'],
        languageOptions: {
            globals: {
                React: 'readonly',
            },
        },
    },
    eslintConfigPrettier,
);
