// const YMAPS_SCRIPT_ID = 'yandex-maps-api-v3';

// declare global {
//   interface Window {
//     ymaps3?: typeof ymaps3;
//   }
// }

// export function loadYmaps3(): Promise<typeof ymaps3> {
//   return new Promise((resolve, reject) => {
//     if (window.ymaps3) {
//       window.ymaps3.ready.then(() => resolve(window.ymaps3!));
//       return;
//     }

//     const existingScript = document.getElementById(YMAPS_SCRIPT_ID);

//     if (existingScript) {
//       existingScript.addEventListener('load', () => {
//         if (!window.ymaps3) {
//           reject(new Error('Yandex Maps script loaded, but window.ymaps3 is missing'));
//           return;
//         }

//         window.ymaps3.ready.then(() => resolve(window.ymaps3!));
//       });

//       existingScript.addEventListener('error', () => {
//         reject(new Error('Failed to load Yandex Maps script'));
//       });

//       return;
//     }

//     const apiKey = import.meta.env.VITE_YANDEX_MAPS_API_KEY;

//     if (!apiKey) {
//       reject(new Error('Missing VITE_YANDEX_MAPS_API_KEY'));
//       return;
//     }

//     const script = document.createElement('script');
//     script.id = YMAPS_SCRIPT_ID;
//     script.type = 'text/javascript';
//     script.src = `https://api-maps.yandex.ru/v3/?apikey=${apiKey}&lang=en_US`;

//     script.onload = () => {
//       if (!window.ymaps3) {
//         reject(new Error('Yandex Maps script loaded, but window.ymaps3 is missing'));
//         return;
//       }

//       window.ymaps3.ready.then(() => resolve(window.ymaps3!));
//     };

//     script.onerror = () => {
//       reject(new Error('Failed to load Yandex Maps script. Check API key, Referer restrictions, ad blocker, VPN, or Network tab.'));
//     };

//     document.head.appendChild(script);
//   });
// }