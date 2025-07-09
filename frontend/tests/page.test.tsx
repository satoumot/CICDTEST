// frontend/tests/page.test.tsx

import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import Home from '../src/app/page'; // テスト対象のHomeコンポーネント

// 'next/image'をモック化します。
jest.mock('next/image', () => ({
    __esModule: true,
    default: (props: any) => {
        // eslint-disable-next-line @next/next/no-img-element
        return <img {...props} />;
    },
}));

// 'counter'コンポーネントをモック化します。
// ★★★ 修正点: 正しい相対パスを指定します ★★★
jest.mock('../src/app/counter', () => ({
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
        expect(screen.getByTestId('mock-counter')).toBeInTheDocument();
        expect(screen.getByText('Mock Counter')).toBeInTheDocument();

        // 3. "Get started"のテキストが表示されているか
        expect(screen.getByText(/get started by editing/i)).toBeInTheDocument();
        expect(screen.getByText('src/app/page.tsx')).toBeInTheDocument();

        // 4. 主要なリンクが表示されているか
        expect(screen.getByRole('link', { name: /deploy now/i })).toBeInTheDocument();
        expect(screen.getByRole('link', { name: /read our docs/i })).toBeInTheDocument();
        
        // 5. Vercelのロゴが表示されているか
        const vercelLogo = screen.getByAltText('Vercel logomark');
        expect(vercelLogo).toBeInTheDocument();
    });
});
