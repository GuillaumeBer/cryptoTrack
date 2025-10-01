import { render, screen } from '@testing-library/react';
import App from './App.jsx';

test('renders landing page header', () => {
  render(<App />);
  const headerElement = screen.getByText(/Crypto Dashboard/i);
  expect(headerElement).toBeInTheDocument();
});
