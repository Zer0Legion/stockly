import { useEffect, useState } from 'react';

// Read the public API URL from environment (NEXT_PUBLIC_* is exposed to the browser)
const API_URL = process.env.NEXT_PUBLIC_API_URL;

export default function Home() {
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetch(`${API_URL}/`)
      .then((response) => response.json())
      .then((data) => setMessage(data.data))
      .catch((error) => console.error('Error fetching backend:', error));
  }, []);

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', padding: '2rem' }}>
      <h1>Welcome to FastAPI + Firebase + Next.js</h1>
      <p>This is your home page served by Next.js frontend.</p>
      <p>Backend Message: {message}</p>
    </div>
  );
}