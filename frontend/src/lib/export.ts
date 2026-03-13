import type { Trade } from '@/domains/trade/types';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import * as XLSX from 'xlsx';

function tradeToRow(t: Trade) {
  return {
    Time: new Date(t.timestamp).toLocaleString(),
    Symbol: t.symbol,
    Side: t.side.toUpperCase(),
    Action: t.action,
    Strategy: t.strategy,
    Price: t.price.toFixed(2),
    Size: t.size.toFixed(4),
    PnL: (t.pnl ?? 0).toFixed(2),
    'PnL %': (t.pnl_pct ?? 0).toFixed(2),
    Fee: t.fee.toFixed(2),
    Reason: t.reason,
    Bot: t.bot_id,
  };
}

export function exportToCSV(trades: Trade[], filename = 'trade-history') {
  const ws = XLSX.utils.json_to_sheet(trades.map(tradeToRow));
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'Trades');
  XLSX.writeFile(wb, `${filename}.csv`, { bookType: 'csv' });
}

export function exportToExcel(trades: Trade[], filename = 'trade-history') {
  const ws = XLSX.utils.json_to_sheet(trades.map(tradeToRow));
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'Trades');
  XLSX.writeFile(wb, `${filename}.xlsx`);
}

export function exportToPDF(trades: Trade[], filename = 'trade-history') {
  const doc = new jsPDF({ orientation: 'landscape' });
  doc.setFontSize(14);
  doc.text('Trade History', 14, 15);
  const columns = ['Time', 'Symbol', 'Side', 'Strategy', 'Price', 'PnL', 'PnL %'];
  const rows = trades.map(t => [
    new Date(t.timestamp).toLocaleString(),
    t.symbol,
    t.side.toUpperCase(),
    t.strategy,
    `$${t.price.toFixed(2)}`,
    `$${(t.pnl ?? 0).toFixed(2)}`,
    `${(t.pnl_pct ?? 0).toFixed(2)}%`,
  ]);
  autoTable(doc, {
    head: [columns],
    body: rows,
    startY: 22,
    styles: { fontSize: 8 },
    headStyles: { fillColor: [40, 50, 70] },
  });
  doc.save(`${filename}.pdf`);
}
