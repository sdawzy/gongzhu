import 'dotenv/config';

// console.log('API URL:', process.env.API_URL);
// console.log('API Key:', process.env.API_KEY);

export default {
    expo: {
        name: "GongzhuGUI",
        slug: "myapp",
        entryPoint: "./App.js",
        version: "0.1.0",
        orientation: "portrait",
        platforms: ["ios", "android", "web"],
        icon: "./assets/images/animalface_buta.png",
        splash: {
            image: "./assets/splash.png",
            resizeMode: "contain",
            backgroundColor: "#ffffff"
        },
        updates: {
            fallbackToCacheTimeout: 0
        },
        extra: {
            apiUrl: process.env.API_URL || "http://localhost:1926",
            apiKey: process.env.API_KEY || null,
        },
        web: {
            "bundler": "webpack"
        }
    }
};
