import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 300000, // 5分
});

// リクエストインターセプター
apiClient.interceptors.request.use(
  (config) => {
    // 必要に応じて認証トークンを追加
    // const token = localStorage.getItem('token')
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// レスポンスインターセプター
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // サーバーからエラーレスポンスが返ってきた場合
      console.error("API Error:", error.response.data);
    } else if (error.request) {
      // リクエストは送信されたがレスポンスがない場合
      console.error("Network Error:", error.request);
    } else {
      // リクエスト設定中にエラーが発生した場合
      console.error("Error:", error.message);
    }
    return Promise.reject(error);
  }
);

export default apiClient;
