// __tests__/page.test.tsx

import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import Home from '../src/app/page'; // テスト対象のHomeコンポーネント

// 'next/image'をモック化します。
// JestはNext.jsの画像最適化を処理できないため、
// これを通常の<img>タグとして扱うようにします。
jest.mock('next/image', () => ({
    __esModule: true,
    default: (props: any) => {
        // eslint-disable-next-line @next/next/no-img-element
        return <img {...props} />;
    },
}));

// 'counter'コンポーネントをモック化します。
// Homeコンポーネントのテストでは、Counterコンポーネント自体の機能はテストしません。
// (それはCounter.test.tsxの役割です)
// ここでは、Counterが正しく配置されているかだけを確認します。
jest.mock('./counter', () => ({
    __esModule: true,
    default: () => {
        return <div data-testid="mock-counter">Mock Counter</div>;
    }
}));


/**
 * Homeページのテストスイート
 */
describe('Home Page', () => {

    /**
     * Test Case 1: 主要な要素が正しくレンダリングされるかの確認
     */
    test('renders all major elements correctly', () => {
        // Homeコンポーネントをレンダリング
        render(<Home />);

        // 1. Next.jsのロゴが表示されているか (altテキストで確認)
        const nextLogo = screen.getByAltText('Next.js logo');
        expect(nextLogo).toBeInTheDocument();

        // 2. Counterコンポーネント（モック版）が表示されているか
        // 上記のモックで `data-testid` を設定したので、それを使って要素を取得します。
        expect(screen.getByTestId('mock-counter')).toBeInTheDocument();
        expect(screen.getByText('Mock Counter')).toBeInTheDocument();

        // 3. "Get started"のテキストが表示されているか
        // getByTextは部分一致も可能です。
        expect(screen.getByText(/get started by editing/i)).toBeInTheDocument();
        // codeタグ内のファイルパスも確認
        expect(screen.getByText('src/app/page.tsx')).toBeInTheDocument();

        // 4. 主要なリンクが表示されているか (アクセシブルな名前、つまりリンクのテキストで確認)
        expect(screen.getByRole('link', { name: /deploy now/i })).toBeInTheDocument();
        expect(screen.getByRole('link', { name: /read our docs/i })).toBeInTheDocument();
        expect(screen.getByRole('link', { name: /learn/i })).toBeInTheDocument();
        expect(screen.getByRole('link', { name: /examples/i })).toBeInTheDocument();
        expect(screen.getByRole('link', { name: /go to nextjs.org/i })).toBeInTheDocument();

        // 5. Vercelのロゴが表示されているか (altテキストで確認)
        const vercelLogo = screen.getByAltText('Vercel logomark');
        expect(vercelLogo).toBeInTheDocument();
    });

    /**
     * Test Case 2: リンクの遷移先(href)が正しいかの確認
     */
    test('has correct links', () => {
        render(<Home />);

        // "Deploy now" リンクのhref属性を確認
        const deployLink = screen.getByRole('link', { name: /deploy now/i });
        expect(deployLink).toHaveAttribute('href', expect.stringContaining('vercel.com/new'));

        // "Read our docs" リンクのhref属性を確認
        const docsLink = screen.getByRole('link', { name: /read our docs/i });
        expect(docsLink).toHaveAttribute('href', expect.stringContaining('nextjs.org/docs'));
    });
});
