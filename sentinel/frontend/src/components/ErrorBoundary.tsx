import React, { Component, ErrorInfo, ReactNode } from 'react';
import { ShieldAlert, RefreshCw, AlertTriangle, Copy, Check } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  copied: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
    copied: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
      copied: false,
    };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('SENTINEL UI Error Intercepted:', error, errorInfo);
    this.setState({ error, errorInfo });
  }

  private handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      copied: false,
    });
    window.location.reload();
  };

  private handleCopy = () => {
    const { error, errorInfo } = this.state;
    const diagnosticText = `SENTINEL v2.0 UI DIAGNOSTIC REPORT\nTimestamp: ${new Date().toISOString()}\nError: ${error?.name}: ${error?.message}\nStack: ${error?.stack}\nComponent Stack: ${errorInfo?.componentStack}`;
    navigator.clipboard.writeText(diagnosticText);
    this.setState({ copied: true });
    setTimeout(() => this.setState({ copied: false }), 2500);
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen w-full flex items-center justify-center bg-gray-50 p-6 text-gray-900 font-mono animate-fade-in">
          <div className="max-w-2xl w-full bg-white border border-rose-300 rounded-xl shadow-xl p-8 backdrop-blur-md relative overflow-hidden animate-scale-in">
            {/* Ambient tactical top bar */}
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-rose-600 via-amber-500 to-rose-600 animate-pulse" />

            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 bg-rose-50 border border-rose-300 rounded-lg text-rose-600">
                <ShieldAlert className="w-8 h-8" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 text-xs font-semibold uppercase tracking-wider bg-rose-50 text-rose-600 border border-rose-300 rounded">
                    Operational Fault Intercepted
                  </span>
                  <span className="text-xs text-gray-500">SENTINEL RECOVERY CORE</span>
                </div>
                <h1 className="text-xl font-bold text-gray-900 tracking-wide mt-1">
                  UI Render Exception Intercepted
                </h1>
              </div>
            </div>

            <p className="text-sm text-gray-600 mb-4 leading-relaxed font-sans">
              The tactical operations interface caught an unhandled rendering condition.
              The application shell has been preserved. You can review the diagnostic trace,
              copy the telemetry report for engineering triage, or reload the interface.
            </p>

            {/* Error Message Box */}
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6 text-xs overflow-x-auto">
              <div className="flex items-center gap-2 text-rose-600 font-bold mb-2">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                <span>{this.state.error?.name || 'Error'}: {this.state.error?.message || 'Unknown Exception'}</span>
              </div>
              {this.state.error?.stack && (
                <pre className="text-gray-500 whitespace-pre-wrap max-h-48 overflow-y-auto leading-tight text-[11px]">
                  {this.state.error.stack}
                </pre>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-4 border-t border-gray-200">
              <button
                onClick={this.handleCopy}
                className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded-lg border border-gray-300 text-xs font-semibold transition-all duration-300"
              >
                {this.state.copied ? (
                  <>
                    <Check className="w-4 h-4 text-emerald-600" />
                    <span>Copied Diagnostic</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4 text-gray-400" />
                    <span>Copy Diagnostic</span>
                  </>
                )}
              </button>

              <button
                onClick={this.handleReset}
                className="flex items-center gap-2 px-5 py-2 bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white rounded-lg text-xs font-semibold shadow-md transition-all duration-300"
              >
                <RefreshCw className="w-4 h-4 animate-spin-slow" />
                <span>Reload Operations Center</span>
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
export default ErrorBoundary;
