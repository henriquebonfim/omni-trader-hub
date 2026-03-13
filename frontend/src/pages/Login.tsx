import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/shared/ui/button';
import { Input } from '@/shared/ui/input';
import { Card } from '@/shared/ui/card';
import { setApiKey, getStoredApiKey } from '@/core/api';

export default function Login() {
  const navigate = useNavigate();
  const [apiKey, setInputApiKey] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // If already logged in, redirect to dashboard
  useEffect(() => {
    const existingKey = getStoredApiKey();
    if (existingKey) {
      navigate('/');
    }
  }, [navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!apiKey.trim()) {
      setError('Please enter an API key');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      // Verify the key by making a test request to /api/health
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || ''}/api/health`,
        {
          headers: {
            'Authorization': `Bearer ${apiKey.trim()}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (response.ok) {
        // Key is valid, store it
        setApiKey(apiKey.trim());
        navigate('/');
      } else if (response.status === 401) {
        setError('Invalid API key. Please try again.');
      } else {
        setError(`Error: ${response.status} ${response.statusText}`);
      }
    } catch (err) {
      setError('Failed to connect to API. Please check the server.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSkip = () => {
    // Allow users to skip if API key is optional (unauthenticated endpoints only)
    setApiKey('');
    navigate('/');
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 px-4">
      <Card className="w-full max-w-md border border-slate-700 bg-slate-800 shadow-2xl">
        <div className="space-y-6 p-8">
          {/* Header */}
          <div className="text-center space-y-2">
            <h1 className="text-3xl font-bold text-white">OmniTrader</h1>
            <p className="text-sm text-slate-400">Enter your API key to access the dashboard</p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="apiKey" className="block text-sm font-medium text-slate-300 mb-2">
                API Key
              </label>
              <Input
                id="apiKey"
                type="password"
                placeholder="Paste your API key here"
                value={apiKey}
                onChange={(e) => setInputApiKey(e.target.value)}
                disabled={isLoading}
                className="bg-slate-700 border-slate-600 text-white placeholder:text-slate-500"
              />
              <p className="text-xs text-slate-400 mt-2">
                Find your API key in the backend logs or leave empty to use unauthenticated mode
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="p-3 rounded-lg bg-red-900/20 border border-red-700 text-red-300 text-sm">
                {error}
              </div>
            )}

            {/* Buttons */}
            <div className="space-y-2 pt-2">
              <Button
                type="submit"
                disabled={isLoading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium"
              >
                {isLoading ? 'Validating...' : 'Sign In'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={handleSkip}
                disabled={isLoading}
                className="w-full text-slate-300 border-slate-600 hover:bg-slate-700"
              >
                Skip (Unauthenticated)
              </Button>
            </div>
          </form>

          {/* Info Box */}
          <div className="p-3 rounded-lg bg-slate-700/50 border border-slate-600 text-xs text-slate-300">
            <p className="font-semibold text-slate-200 mb-1">How to get your API key:</p>
            <ol className="space-y-1 list-decimal list-inside">
              <li>Check the backend container logs on startup</li>
              <li>Look for "AUTO-GENERATED API KEY"</li>
              <li>Or set OMNITRADER_API_KEY in your .env file</li>
            </ol>
          </div>
        </div>
      </Card>
    </div>
  );
}
