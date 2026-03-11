import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Конфигурация Vite для фронтенд приложения на React
// https://vitejs.dev/config/
export default defineConfig({
  // Подключаем React плагин для быстрой разработки и оптимизации сборки
  plugins: [react()],
  
  // Конфигурация dev сервера
  server: {
    // Порт, на котором запускается dev сервер
    port: 3000,
    
    // Настройка прокси для API запросов
    proxy: {
      // Все запросы на /api перенаправляются на backend
      "/api": {
        // Адрес backend сервера
        target: "http://localhost:8000",
        // Изменяем заголовок Origin в прокси запросах для совместимости
        changeOrigin: true,
      },
    },
  },
});
