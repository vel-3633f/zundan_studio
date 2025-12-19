const WS_BASE_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000";

export interface ProgressUpdate {
  task_id: string;
  status: string;
  progress: number;
  message?: string;
  result?: any;
  error?: string;
}

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private taskId: string;
  private onMessage: (data: ProgressUpdate) => void;
  private onError: (error: Event) => void;
  private onClose: () => void;

  constructor(
    taskId: string,
    onMessage: (data: ProgressUpdate) => void,
    onError?: (error: Event) => void,
    onClose?: () => void
  ) {
    this.taskId = taskId;
    this.onMessage = onMessage;
    this.onError = onError || (() => {});
    this.onClose = onClose || (() => {});
  }

  connect(): void {
    const wsUrl = `${WS_BASE_URL}/ws/progress/${this.taskId}`;
    console.log("WebSocket connecting to:", wsUrl);

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log("WebSocket connected");
    };

    this.ws.onmessage = (event) => {
      try {
        const data: ProgressUpdate = JSON.parse(event.data);
        this.onMessage(data);

        // タスクが完了または失敗した場合は自動的に切断
        if (data.status === "completed" || data.status === "failed") {
          this.disconnect();
        }
      } catch (error) {
        console.error("Failed to parse WebSocket message:", error);
      }
    };

    this.ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      this.onError(error);
    };

    this.ws.onclose = () => {
      console.log("WebSocket disconnected");
      this.onClose();
    };
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

export const createWebSocketClient = (
  taskId: string,
  onMessage: (data: ProgressUpdate) => void,
  onError?: (error: Event) => void,
  onClose?: () => void
): WebSocketClient => {
  return new WebSocketClient(taskId, onMessage, onError, onClose);
};
