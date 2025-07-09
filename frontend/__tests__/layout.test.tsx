// frontend/tests/layout.test.tsx

import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import RootLayout from '../src/app/layout'; // テスト対象のRootLayoutコンポーネント

// 'next/font/google' モジュールをモック化します。
jest.mock('next/font/google', () => ({
    Geist: () => ({
        variable: 'mock-font-geist-sans',
    }),
    Geist_Mono: () => ({
        variable: 'mock-font-geist-mono',
    }),
}));

/**
 * RootLayoutのテストスイート
 */
describe('RootLayout', () => {

    /**
     * Test Case 1: 子要素が正しくレンダリングされるかの確認
     */
    test('renders children correctly', () => {
        render(
            <RootLayout>
                <div>
                    <h1>Test Child Heading</h1>
                    <p>This is a test child component.</p>
                </div>
            </RootLayout>
        );

        expect(screen.getByRole('heading', { name: /test child heading/i })).toBeInTheDocument();
        expect(screen.getByText('This is a test child component.')).toBeInTheDocument();
    });

    /**
     * Test Case 2: bodyタグに正しいクラス名が付与されているかの確認
     */
    test('applies font class names to the body tag', () => {
        // ★★★ 修正点: renderの返り値は使わない ★★★
        render(
            <RootLayout>
                <div />
            </RootLayout>
        );

        // ★★★ 修正点: グローバルのdocumentからbody要素を取得します ★★★
        const bodyElement = document.querySelector('body');

        expect(bodyElement).toBeInTheDocument();
        expect(bodyElement).toHaveClass('mock-font-geist-sans');
        expect(bodyElement).toHaveClass('mock-font-geist-mono');
        expect(bodyElement).toHaveClass('antialiased');
    });
});
