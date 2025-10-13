interface RouteMetrics {
  screen: string;
  timestamp: number;
  duration?: number;
  user_action?: string;
}

class MobileAnalytics {
  private metrics: RouteMetrics[] = [];

  trackScreenView(screenName: string) {
    if (!screenName) return;
    const metric: RouteMetrics = {
      screen: screenName,
      timestamp: Date.now(),
    };

    this.metrics.push(metric);
    this.sendToBackend(metric);
  }

  trackUserAction(screen: string, action: string) {
    const metric: RouteMetrics = {
      screen,
      timestamp: Date.now(),
      user_action: action,
    };

    this.metrics.push(metric);
    this.sendToBackend(metric);
  }

  private async sendToBackend(metric: RouteMetrics) {
    try {
      await fetch('http://localhost:8000/api/mobile-metrics/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(metric),
      });
    } catch (error) {
      console.log('Metrics send failed:', error);
    }
  }
}

export const analytics = new MobileAnalytics();