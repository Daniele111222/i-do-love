import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Input } from '@/components/ui/input';

describe('Input', () => {
  it('renders with aria label', () => {
    render(<Input aria-label="搜索" />);
    expect(screen.getByLabelText('搜索')).toBeInTheDocument();
  });

  it('accepts text input', async () => {
    const user = userEvent.setup();
    render(<Input aria-label="关键词" />);

    const input = screen.getByLabelText('关键词');
    await user.type(input, 'ai news');

    expect(input).toHaveValue('ai news');
  });
});
