/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'eira-cyan': '#00f2fe',
                'eira-purple': '#6633ff',
                'eira-dark': '#0a0a12',
                'eira-glass': 'rgba(255, 255, 255, 0.05)',
            },
            backgroundImage: {
                'hologram-gradient': 'linear-gradient(135deg, #00f2fe 0%, #6633ff 100%)',
            }
        },
    },
    plugins: [],
}
