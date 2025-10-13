// Utility formatters for the mobile app

export function formatCurrencyBRL(value: unknown): string {
  let num: number = 0;
  if (typeof value === 'number') {
    num = Number.isFinite(value) ? value : 0;
  } else if (value != null) {
    const parsed = parseFloat(String(value).replace(',', '.'));
    num = Number.isFinite(parsed) ? parsed : 0;
  }

  try {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(num);
  } catch {
    // Fallback in case Intl is not available for some reason
    return `R$ ${num.toFixed(2)}`;
  }
}
