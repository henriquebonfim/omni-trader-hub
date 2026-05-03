import { jsPDF } from 'jspdf';
import 'jspdf-autotable';

// Extend jsPDF with autotable for TS
interface jsPDFWithPlugin extends jsPDF {
  autoTable: (options: any) => jsPDF;
}

export const exportPerformanceReport = (stats: any, trades: any[]) => {
  const doc = new jsPDF() as jsPDFWithPlugin;
  const timestamp = new Date().toLocaleString();

  // Header
  doc.setFontSize(20);
  doc.setTextColor(40, 40, 40);
  doc.text('OmniTrader Performance Report', 14, 22);
  
  doc.setFontSize(10);
  doc.setTextColor(100, 100, 100);
  doc.text(`Generated on: ${timestamp}`, 14, 30);

  // Stats Section
  doc.setFontSize(14);
  doc.setTextColor(0, 0, 0);
  doc.text('Summary Statistics', 14, 45);

  const statsData = [
    ['Sharpe Ratio', stats.sharpe_ratio.toString()],
    ['Max Drawdown', `${(stats.max_drawdown * 100).toFixed(2)}%`],
    ['Profit Factor', stats.profit_factor.toString()],
    ['Win Rate', `${stats.win_rate}%`],
    ['Total Trades', stats.total_trades.toString()]
  ];

  doc.autoTable({
    startY: 50,
    head: [['Metric', 'Value']],
    body: statsData,
    theme: 'striped',
    headStyles: { fillStyle: [33, 150, 243] }
  });

  // Trades Section
  doc.setFontSize(14);
  doc.text('Recent Trade History', 14, (doc as any).lastAutoTable.finalY + 15);

  const tradeData = trades.slice(0, 20).map(t => [
    new Date(t.timestamp).toLocaleString(),
    t.symbol,
    t.side,
    t.price.toFixed(2),
    t.size.toFixed(4),
    t.pnl ? `${t.pnl >= 0 ? '+' : ''}${t.pnl.toFixed(2)}` : '0.00'
  ]);

  doc.autoTable({
    startY: (doc as any).lastAutoTable.finalY + 20,
    head: [['Time', 'Symbol', 'Side', 'Price', 'Size', 'PnL']],
    body: tradeData,
    theme: 'grid',
    headStyles: { fillStyle: [40, 40, 40] }
  });

  // Footer
  const pageCount = (doc as any).internal.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFontSize(8);
    doc.text(`Page ${i} of ${pageCount} - OmniTrader Internal Report`, 14, doc.internal.pageSize.getHeight() - 10);
  }

  doc.save(`OmniTrader_Report_${new Date().getTime()}.pdf`);
};
