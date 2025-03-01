import React from 'react'; //  ^18.0.0
import { render, screen, fireEvent } from '@testing-library/react'; //  ^14.0.0
import userEvent from '@testing-library/user-event'; //  ^14.0.0
import { renderWithProviders } from '../../testUtils';
import Button from '../../../components/common/Button';

describe('Button component', () => {
  it('renders correctly with default props', () => {
    // Arrange: Render the Button component with default props and text content
    renderWithProviders(<Button>Click me</Button>);

    // Act: (No explicit action needed for rendering)

    // Assert: Verify that the button is in the document
    const buttonElement = screen.getByRole('button', { name: 'Click me' });
    expect(buttonElement).toBeInTheDocument();

    // Assert: Verify that the button has the primary variant styling
    expect(buttonElement).toHaveStyle('background-color: #2C5282');

    // Assert: Verify that the button has the medium size styling
    expect(buttonElement).toHaveStyle('padding: 8px 16px');

    // Assert: Verify that the button displays the correct text content
    expect(buttonElement).toHaveTextContent('Click me');
  });

  it('renders correctly with different variants', () => {
    // Arrange: Render the Button component with 'primary' variant
    renderWithProviders(<Button variant="primary">Primary</Button>);
    const primaryButton = screen.getByRole('button', { name: 'Primary' });

    // Assert: Verify that the button has the primary styling
    expect(primaryButton).toHaveStyle('background-color: #2C5282');

    // Arrange: Render the Button component with 'secondary' variant
    renderWithProviders(<Button variant="secondary">Secondary</Button>);
    const secondaryButton = screen.getByRole('button', { name: 'Secondary' });

    // Assert: Verify that the button has the secondary styling
    expect(secondaryButton).toHaveStyle('background-color: #38A169');

    // Arrange: Render the Button component with 'outline' variant
    renderWithProviders(<Button variant="outline">Outline</Button>);
    const outlineButton = screen.getByRole('button', { name: 'Outline' });

    // Assert: Verify that the button has the outline styling
    expect(outlineButton).toHaveStyle('background-color: transparent');

    // Arrange: Render the Button component with 'text' variant
    renderWithProviders(<Button variant="text">Text</Button>);
    const textButton = screen.getByRole('button', { name: 'Text' });

    // Assert: Verify that the button has the text styling
    expect(textButton).toHaveStyle('background-color: transparent');
  });

  it('renders correctly with different sizes', () => {
    // Arrange: Render the Button component with 'small' size
    renderWithProviders(<Button size="small">Small</Button>);
    const smallButton = screen.getByRole('button', { name: 'Small' });

    // Assert: Verify that the button has the small size styling
    expect(smallButton).toHaveStyle('padding: 4px 8px');

    // Arrange: Render the Button component with 'medium' size
    renderWithProviders(<Button size="medium">Medium</Button>);
    const mediumButton = screen.getByRole('button', { name: 'Medium' });

    // Assert: Verify that the button has the medium size styling
    expect(mediumButton).toHaveStyle('padding: 8px 16px');

    // Arrange: Render the Button component with 'large' size
    renderWithProviders(<Button size="large">Large</Button>);
    const largeButton = screen.getByRole('button', { name: 'Large' });

    // Assert: Verify that the button has the large size styling
    expect(largeButton).toHaveStyle('padding: 12px 32px');
  });

  it('renders correctly with different colors', () => {
    // Arrange: Render the Button component with 'primary' color
    renderWithProviders(<Button color="primary">Primary</Button>);
    const primaryButton = screen.getByRole('button', { name: 'Primary' });

    // Assert: Verify that the button has the primary color styling
    expect(primaryButton).toHaveStyle('background-color: #2C5282');

    // Arrange: Render the Button component with 'secondary' color
    renderWithProviders(<Button color="secondary">Secondary</Button>);
    const secondaryButton = screen.getByRole('button', { name: 'Secondary' });

    // Assert: Verify that the button has the secondary color styling
    expect(secondaryButton).toHaveStyle('background-color: #38A169');

    // Arrange: Render the Button component with 'success' color
    renderWithProviders(<Button color="success">Success</Button>);
    const successButton = screen.getByRole('button', { name: 'Success' });

    // Assert: Verify that the button has the success color styling
    expect(successButton).toHaveStyle('background-color: #38A169');

    // Arrange: Render the Button component with 'warning' color
    renderWithProviders(<Button color="warning">Warning</Button>);
    const warningButton = screen.getByRole('button', { name: 'Warning' });

    // Assert: Verify that the button has the warning color styling
    expect(warningButton).toHaveStyle('background-color: #DD6B20');

    // Arrange: Render the Button component with 'error' color
    renderWithProviders(<Button color="error">Error</Button>);
    const errorButton = screen.getByRole('button', { name: 'Error' });

    // Assert: Verify that the button has the error color styling
    expect(errorButton).toHaveStyle('background-color: #E53E3E');
  });

  it('handles click events correctly', () => {
    // Arrange: Create a mock function for the onClick handler
    const onClickMock = jest.fn();

    // Arrange: Render the Button component with the mock onClick handler
    renderWithProviders(<Button onClick={onClickMock}>Click me</Button>);

    // Act: Simulate a user clicking on the button
    const buttonElement = screen.getByRole('button', { name: 'Click me' });
    fireEvent.click(buttonElement);

    // Assert: Verify that the mock function was called once
    expect(onClickMock).toHaveBeenCalledTimes(1);
  });

  it('is disabled when disabled prop is true', () => {
    // Arrange: Render the Button component with disabled={true}
    renderWithProviders(<Button disabled={true}>Click me</Button>);

    // Act: (No explicit action needed for rendering)

    // Assert: Verify that the button has the disabled attribute
    const buttonElement = screen.getByRole('button', { name: 'Click me' });
    expect(buttonElement).toBeDisabled();

    // Arrange: Create a mock function for the onClick handler
    const onClickMock = jest.fn();

    // Arrange: Render the Button component with disabled={true} and the mock onClick handler
    renderWithProviders(<Button disabled={true} onClick={onClickMock}>Click me</Button>);

    // Act: Simulate a user clicking on the button
    fireEvent.click(buttonElement);

    // Assert: Verify that the mock function was not called
    expect(onClickMock).not.toHaveBeenCalled();
  });

  it('has fullWidth style when fullWidth prop is true', () => {
    // Arrange: Render the Button component with fullWidth={true}
    renderWithProviders(<Button fullWidth={true}>Click me</Button>);

    // Act: (No explicit action needed for rendering)

    // Assert: Verify that the button has the fullWidth styling
    const buttonElement = screen.getByRole('button', { name: 'Click me' });
    expect(buttonElement).toHaveStyle('width: 100%');
  });

  it('has correct type attribute', () => {
    // Arrange: Render the Button component with type='submit'
    renderWithProviders(<Button type="submit">Submit</Button>);

    // Act: (No explicit action needed for rendering)

    // Assert: Verify that the button has type='submit' attribute
    const submitButton = screen.getByRole('button', { name: 'Submit' });
    expect(submitButton).toHaveAttribute('type', 'submit');

    // Arrange: Render the Button component with type='reset'
    renderWithProviders(<Button type="reset">Reset</Button>);

    // Act: (No explicit action needed for rendering)

    // Assert: Verify that the button has type='reset' attribute
    const resetButton = screen.getByRole('button', { name: 'Reset' });
    expect(resetButton).toHaveAttribute('type', 'reset');

    // Arrange: Render the Button component with type='button'
    renderWithProviders(<Button type="button">Button</Button>);

    // Act: (No explicit action needed for rendering)

    // Assert: Verify that the button has type='button' attribute
    const buttonButton = screen.getByRole('button', { name: 'Button' });
    expect(buttonButton).toHaveAttribute('type', 'button');
  });

  it('applies additional className when provided', () => {
    // Arrange: Render the Button component with className='test-class'
    renderWithProviders(<Button className="test-class">Click me</Button>);

    // Act: (No explicit action needed for rendering)

    // Assert: Verify that the button has the 'test-class' class
    const buttonElement = screen.getByRole('button', { name: 'Click me' });
    expect(buttonElement).toHaveClass('test-class');
  });

  it('has correct accessibility attributes', () => {
    // Arrange: Render the Button component with aria-label='Test button'
    renderWithProviders(<Button aria-label="Test button">Click me</Button>);

    // Act: (No explicit action needed for rendering)

    // Assert: Verify that the button has aria-label='Test button'
    const buttonElement = screen.getByRole('button', { name: 'Click me' });
    expect(buttonElement).toHaveAttribute('aria-label', 'Test button');

    // Arrange: Render the Button component with aria={{ pressed: 'true' }}
    renderWithProviders(<Button aria={{ pressed: 'true' }}>Click me</Button>);

    // Act: (No explicit action needed for rendering)

    // Assert: Verify that the button has aria-pressed='true'
    const buttonElement2 = screen.getByRole('button', { name: 'Click me' });
    expect(buttonElement2).toHaveAttribute('aria-pressed', 'true');
  });
});