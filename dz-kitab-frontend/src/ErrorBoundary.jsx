import React from 'react';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        console.error('ErrorBoundary caught an error:', error, errorInfo);
        this.setState({
            error: error,
            errorInfo: errorInfo
        });
    }

    render() {
        if (this.state.hasError) {
            return (
                <div style={{
                    padding: '50px',
                    textAlign: 'center',
                    fontFamily: 'Poppins, sans-serif'
                }}>
                    <h1 style={{ color: '#e53e3e', fontSize: '32px', marginBottom: '20px' }}>
                        Something went wrong
                    </h1>
                    <p style={{ fontSize: '18px', marginBottom: '20px', color: '#333' }}>
                        The application encountered an error. Please check the console for more details.
                    </p>
                    <details style={{
                        whiteSpace: 'pre-wrap',
                        textAlign: 'left',
                        backgroundColor: '#f7fafc',
                        padding: '20px',
                        borderRadius: '8px',
                        maxWidth: '800px',
                        margin: '0 auto'
                    }}>
                        <summary style={{ cursor: 'pointer', fontWeight: 'bold', marginBottom: '10px' }}>
                            Error Details
                        </summary>
                        <p style={{ color: '#e53e3e', marginBottom: '10px' }}>
                            {this.state.error && this.state.error.toString()}
                        </p>
                        <p style={{ fontSize: '14px', color: '#666' }}>
                            {this.state.errorInfo && this.state.errorInfo.componentStack}
                        </p>
                    </details>
                    <button
                        onClick={() => window.location.reload()}
                        style={{
                            marginTop: '30px',
                            padding: '12px 24px',
                            backgroundColor: '#1314d7',
                            color: 'white',
                            border: 'none',
                            borderRadius: '5px',
                            cursor: 'pointer',
                            fontSize: '16px',
                            fontWeight: '500'
                        }}
                    >
                        Reload Page
                    </button>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
