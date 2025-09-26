import { render, screen } from '@testing-library/react';
import App from './App';

test('renders page header', () => {
  render(<App />);
  const headerElement = screen.getByText(/Chercher une Paire de Trading USDC/i);
  expect(headerElement).toBeInTheDocument();
});
