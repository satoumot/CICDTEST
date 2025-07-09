'use client'; // 👈 これがクライアントコンポーネントであることの宣言です

import { useState } from 'react';

export default function Counter() {
    const [count, setCount] = useState(0);

    return (
        <div
            style={{
                marginTop: '20px',
                border: '1px solid grey',
                padding: '10px',
            }}
        >
            <h2>Client Component Counter</h2>
            <p>You clicked {count} times</p>
            <button onClick={() => setCount(count + 2)}>Click me</button>
        </div>
    );
}
