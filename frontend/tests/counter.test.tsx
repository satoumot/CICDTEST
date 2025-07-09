// Counter.test.tsx

import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Counter from '../src/app/counter'; // Counterコンポーネントをインポート

/**
 * Counterコンポーネントのテストスイート
 */
describe('Counter Component', () => {

    /**
     * Test Case 1: 初期表示の確認
     * コンポーネントが正しくレンダリングされ、初期カウントが0であることをテストします。
     */
    test('renders initial state correctly', () => {
        // コンポーネントをレンダリング
        render(<Counter />);

        // 見出しが表示されていることを確認
        expect(screen.getByRole('heading', { name: /client component counter/i })).toBeInTheDocument();

        // 初期カウントが "0" であることを確認
        expect(screen.getByText('You clicked 0 times')).toBeInTheDocument();

        // ボタンが表示されていることを確認
        expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
    });

    /**
     * Test Case 2: ボタンクリックでカウントが増えることの確認
     * ボタンを1回クリックすると、カウントが2になることをテストします。
     */
    test('increments count by 2 when button is clicked once', async () => {
        const user = userEvent.setup();
        
        // コンポーネントをレンダリング
        render(<Counter />);

        // ボタンを取得
        const button = screen.getByRole('button', { name: /click me/i });

        // ボタンをクリック
        await user.click(button);

        // カウントが "2" に更新されていることを確認
        expect(screen.getByText('You clicked 1 times')).toBeInTheDocument();
    });

    /**
     * Test Case 3: ボタンを複数回クリックした際の動作確認
     * ボタンを3回クリックすると、カウントが6になることをテストします。
     */
    test('increments count correctly on multiple clicks', async () => {
        const user = userEvent.setup();
        
        // コンポーネントをレンダリング
        render(<Counter />);

        // ボタンを取得
        const button = screen.getByRole('button', { name: /click me/i });

        // ボタンを3回クリック
        await user.click(button);
        await user.click(button);
        await user.click(button);

        // カウントが "6" に更新されていることを確認
        expect(screen.getByText('You clicked 6 times')).toBeInTheDocument();
    });
});