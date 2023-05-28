import logo from './logo.svg';
import './App.css';
import { useEffect } from 'react'

function App() {
  const credentials = { username: 'testuser', password: 'testpass123' }
  // useEffect(() => {
  //   fetch('http://localhost:8000/api/v1/dj-rest-auth/login/')
  //     .then(response => response.json())
  //     .then(data => console.log(data))
  // }, [])

  async function handleLogin() {
    try {
      const response = await fetch('http://localhost:8000/api/v1/dj-rest-auth/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (response.ok) {
        // POST request was successful
        const responseData = await response.json();
        console.log('Response data:', responseData);
      } else {
        // Handle the error case
        console.error('Error:', response.status);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div>
      <button onClick={handleLogin} >Login</button>
    </div>
  );
}

export default App;
