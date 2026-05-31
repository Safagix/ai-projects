
import { loadData, saveData } from './storage';

// --- Types ---
export interface Article {
    title: string;
    description: string;
    content: string;
    url: string;
    image: string;
    publishedAt: string;
    source: {
        name: string;
        url: string;
    };
}

export type NewsCategory = 'general' | 'world' | 'nation' | 'business' | 'technology' | 'entertainment' | 'sports' | 'science' | 'health';

interface NewsCache {
    timestamp: number;
    articles: Article[];
}

// --- Configuration ---
// TODO: Move to a secure config file or environment variable
const API_KEY = "f0846061386766453916962f3f898308"; // Defines a public GNews Key for testing (Free Tier)
const BASE_URL = "https://gnews.io/api/v4";
const CACHE_DURATION = 1000 * 60 * 60; // 1 hour

// --- Service ---

// --- Mock Data (Fallback) ---
const MOCK_ARTICLES: Article[] = [
    {
        title: "La IA Generativa alcanza un nuevo hito en razonamiento lógico",
        description: "Un nuevo modelo presentado hoy demuestra capacidades de resolución de problemas matemáticos complejos que superan a los humanos expertos, marcando un antes y un después en la computación cognitiva.",
        content: "...",
        url: "https://google.com",
        image: "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?q=80&w=2000&auto=format&fit=crop",
        publishedAt: new Date().toISOString(),
        source: { name: "TechCrunch", url: "https://techcrunch.com" }
    },
    {
        title: "SpaceX confirma lanzamiento exitoso de la misión Starship V",
        description: "El cohete más grande del mundo ha logrado entrar en órbita y regresar a la plataforma de lanzamiento con una precisión milimétrica, abriendo la puerta a la colonización de Marte.",
        content: "...",
        url: "https://spacex.com",
        image: "https://images.unsplash.com/photo-1517976487492-5750f3195933?q=80&w=2000&auto=format&fit=crop",
        publishedAt: new Date().toISOString(),
        source: { name: "SpaceNews", url: "https://spacenews.com" }
    },
    {
        title: "Nvidia presenta su nueva arquitectura de GPU cuántica",
        description: "La compañía líder en semiconductores revela un chip híbrido clásico-cuántico que promete acelerar el entrenamiento de redes neuronales en un 10.000%.",
        content: "...",
        url: "https://nvidia.com",
        image: "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=2000&auto=format&fit=crop",
        publishedAt: new Date().toISOString(),
        source: { name: "The Verge", url: "https://theverge.com" }
    },
    {
        title: "El auge de la computación biológica: Organoides procesan datos",
        description: "Científicos logran conectar tejido cerebral cultivado en laboratorio a circuitos de silicio, creando el primer bioprocesador funcional.",
        content: "...",
        url: "https://nature.com",
        image: "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?q=80&w=2000&auto=format&fit=crop",
        publishedAt: new Date().toISOString(),
        source: { name: "Nature", url: "https://nature.com" }
    },
    {
        title: "Apple Vision Pro 2: Más ligero, más potente y económico",
        description: "Fugas confirman que la próxima generación de computación espacial llegará con un factor de forma similar a unas gafas de sol y batería de una semana.",
        content: "...",
        url: "https://apple.com",
        image: "https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?q=80&w=2000&auto=format&fit=crop",
        publishedAt: new Date().toISOString(),
        source: { name: "MacRumors", url: "https://macrumors.com" }
    }
];

export const fetchNews = async (category: NewsCategory = 'general', query?: string): Promise<Article[]> => {
    const cacheKey = `news_cache_${category}_${query || 'top'}.json`;

    // 1. Try Load from Cache
    const cached = await loadData<NewsCache | null>(cacheKey, null);
    if (cached) {
        const age = Date.now() - cached.timestamp;
        if (age < CACHE_DURATION) {
            console.log(`[News] Serving cached ${category} news (${Math.round(age / 1000 / 60)}m old)`);
            return cached.articles;
        }
    }

    // 2. Fetch from API
    try {
        console.log(`[News] Fetching fresh ${category} news...`);
        let url = `${BASE_URL}/top-headlines?category=${category}&lang=es&country=mx&max=10&apikey=${API_KEY}`;

        if (query) {
            url = `${BASE_URL}/search?q=${encodeURIComponent(query)}&lang=es&max=10&apikey=${API_KEY}`;
        }

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`News API Error: ${response.statusText}`);
        }

        const data = await response.json();

        if (!data.articles) {
            console.warn('[News] No articles found', data);
            return MOCK_ARTICLES; // Fallback directly if API returns weird structure
        }

        const articles: Article[] = data.articles;

        // 3. Save to Cache
        const newCache: NewsCache = {
            timestamp: Date.now(),
            articles
        };
        await saveData(cacheKey, newCache);

        return articles;

    } catch (error) {
        console.error("[News] Fetch failed", error);
        // Fallback to cache even if expired
        if (cached) return cached.articles;

        // Critical Fallback: Return Mock Data so UI is never empty
        return MOCK_ARTICLES.map(a => ({ ...a, title: `[DEMO] ${a.title}` }));
    }
};

export const NEWS_CATEGORIES: { id: NewsCategory; label: string; icon: string }[] = [
    { id: 'general', label: 'General', icon: '🌍' },
    { id: 'technology', label: 'Tecnología', icon: '💻' },
    { id: 'science', label: 'Ciencia', icon: '🔬' },
    { id: 'business', label: 'Negocios', icon: '💼' },
    { id: 'entertainment', label: 'Cultura', icon: '🎨' },
    { id: 'health', label: 'Salud', icon: '❤️' }
];
