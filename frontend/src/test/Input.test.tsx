import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Input } from '@/components/common/Input';
import userEvent from '@testing-library/user-event';

describe('Input', () => {
  it('renders with label', () => {
    render(<Input label="邮箱" />);
    expect(screen.getByLabelText('邮箱')).toBeInTheDocument();
  });

  it('displays error message', () => {
    render(<Input label="邮箱" error="邮箱格式不正确" />);
    expect(screen.getByText('邮箱格式不正确')).toBeInTheDocument();
  });

  it('accepts text input', async () => {
    const user = userEvent.setup();
    render(<Input label="邮箱" />);
    const input = screen.getByLabelText('邮箱');
    await user.type(input, 'test@example.com');
    expect(input).toHaveValue('test@example.com');
  });
});
