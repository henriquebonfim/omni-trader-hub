import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Brain, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  RefreshCw,
  Activity,
  ShieldAlert
} from 'lucide-react';
import { AIOverview, fetchAIOverview, triggerAIOverview } from '../../domains/intelligence/api';
import { cn } from '@/core/utils';

export const AIOverviewCard: React.FC = () => {
  const [data, setData] = useState<AIOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const overview = await fetchAIOverview();
      setData(overview);
      setError(null);
    } catch (err) {
      setError('AI Insight unavailable. Trigger a new generation.');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await triggerAIOverview();
      // Wait a bit for the worker to start
      setTimeout(loadData, 5000);
    } catch (err) {
      setError('Failed to trigger generation.');
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 60000); // Poll every minute
    return () => clearInterval(interval);
  }, []);

  if (loading && !data) {
    return (
      <div className="h-64 w-full bg-glass rounded-xl flex flex-col items-center justify-center space-y-4 animate-pulse">
        <Brain className="w-12 h-12 text-muted-foreground opacity-20" />
        <div className="h-4 w-48 bg-muted rounded"></div>
      </div>
    );
  }

  const sentimentColor = data?.sentiment === 'Bullish' ? 'text-success' : data?.sentiment === 'Bearish' ? 'text-danger' : 'text-accent';
  const riskColor = (data?.risk_score || 0) > 0.7 ? 'text-danger' : (data?.risk_score || 0) > 0.4 ? 'text-warning' : 'text-success';

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-glass rounded-xl p-6 relative overflow-hidden group"
    >
      {/* Background Decorative Element */}
      <div className="absolute -right-12 -top-12 w-48 h-48 bg-primary/5 rounded-full blur-3xl group-hover:bg-primary/10 transition-colors" />
      
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-primary/10 rounded-lg">
            <Brain className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h3 className="font-semibold text-lg">AI Intelligence Core</h3>
            <p className="text-xs text-muted-foreground">Latest market narrative & signals</p>
          </div>
        </div>
        
        <button 
          onClick={handleRefresh}
          disabled={refreshing}
          className="p-2 hover:bg-white/5 rounded-full transition-colors disabled:opacity-50"
        >
          <RefreshCw className={cn("w-4 h-4 text-muted-foreground", refreshing && "animate-spin")} />
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Sentiment Signal */}
        <div className="flex flex-col space-y-1">
          <span className="text-xs text-muted-foreground uppercase tracking-wider">Sentiment</span>
          <div className={cn("flex items-center space-x-2 font-bold text-xl", sentimentColor)}>
            {data?.sentiment === 'Bullish' ? <TrendingUp className="w-5 h-5" /> : data?.sentiment === 'Bearish' ? <TrendingDown className="w-5 h-5" /> : <Activity className="w-5 h-5" />}
            <span>{data?.sentiment || 'Neutral'}</span>
          </div>
        </div>

        {/* Risk Level */}
        <div className="flex flex-col space-y-1">
          <span className="text-xs text-muted-foreground uppercase tracking-wider">Risk Level</span>
          <div className={cn("flex items-center space-x-2 font-bold text-xl", riskColor)}>
            <ShieldAlert className="w-5 h-5" />
            <span>{Math.round((data?.risk_score || 0) * 100)}%</span>
          </div>
        </div>

        {/* Generation Time */}
        <div className="flex flex-col space-y-1">
          <span className="text-xs text-muted-foreground uppercase tracking-wider">Last Analysis</span>
          <span className="text-xl font-mono">
            {data?.timestamp ? new Date(data.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '--:--'}
          </span>
        </div>
      </div>

      <div className="space-y-4">
        <div className="text-sm leading-relaxed text-foreground/80 whitespace-pre-wrap italic">
          "{data?.narrative || 'No narrative available.'}"
        </div>

        {data?.anomalies && data.anomalies.length > 0 && (
          <div className="pt-4 border-t border-white/5">
            <h4 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-3 flex items-center">
              <AlertTriangle className="w-3 h-3 mr-2 text-warning" />
              Detected Anomalies
            </h4>
            <div className="space-y-2">
              {data.anomalies.map((anomaly, idx) => (
                <div key={idx} className="bg-white/3 rounded-lg p-3 border border-white/5 hover:border-white/10 transition-colors">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium">{anomaly.title}</span>
                    <span className={cn(
                      "text-[10px] px-1.5 py-0.5 rounded-full uppercase font-bold",
                      anomaly.impact_score > 0.7 ? "bg-danger/20 text-danger" : "bg-warning/20 text-warning"
                    )}>
                      Impact: {Math.round(anomaly.impact_score * 10)}/10
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground leading-normal">
                    {anomaly.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      
      {error && !data && (
        <div className="mt-4 p-4 bg-danger/10 border border-danger/20 rounded-lg flex items-center space-x-3">
          <AlertTriangle className="w-5 h-5 text-danger" />
          <span className="text-sm text-danger">{error}</span>
        </div>
      )}
    </motion.div>
  );
};
