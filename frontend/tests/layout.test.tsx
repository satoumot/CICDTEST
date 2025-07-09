// __tests__/layout.test.tsx

import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import RootLayout from '../src/app/layout'; // テスト対象のRootLayoutコンポーネント

// 'next/font/google' モジュールをモック化します。
// Jest環境ではフォントの読み込みは実行されないため、
// フォントオブジェクトが持つ 'variable' プロパティを模倣した
// ダミーのオブジェクトを返すように設定します。
jest.mock('next/font/google', () => ({
    Geist: () => ({
        variable: 'mock-font-geist-sans', // モック用のクラス名
    }),
    Geist_Mono: () => ({
        variable: 'mock-font-geist-mono', // モック用のクラス名
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
        // RootLayoutを、テスト用のシンプルな子要素を渡してレンダリングします。
        render(
            <RootLayout>
                <div>
                    <h1>Test Child Heading</h1>
                    <p>This is a test child component.</p>
                </div>
            </RootLayout>
        );

        // 渡した子要素の見出しと段落がドキュメント内に表示されていることを確認します。
        expect(screen.getByRole('heading', { name: /test child heading/i })).toBeInTheDocument();
        expect(screen.getByText('This is a test child component.')).toBeInTheDocument();
    });

    /**
     * Test Case 2: bodyタグに正しいクラス名が付与されているかの確認
     */
    test('applies font class names to the body tag', () => {
        // render関数は `container` を返し、これを通じてレンダリングされたDOM全体にアクセスできます。
        const { container } = render(
            <RootLayout>
                <div />
            </RootLayout>
        );

        // containerからbody要素を取得します。
        const bodyElement = container.querySelector('body');

        // body要素が存在し、モック化したフォントのクラス名と'antialiased'クラスが
        // 含まれていることを確認します。
        expect(bodyElement).toBeInTheDocument();
        expect(bodyElement).toHaveClass('mock-font-geist-sans');
        expect(bodyElement).toHaveClass('mock-font-geist-mono');
        expect(bodyElement).toHaveClass('antialiased');
    });
});
