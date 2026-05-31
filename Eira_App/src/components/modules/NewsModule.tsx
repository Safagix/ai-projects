
import React, { useState, useEffect } from 'react';
import { fetchNews, Article, NEWS_CATEGORIES, NewsCategory } from '../../services/news';
import { NewsCard } from '../ui/NewsCard';

export const NewsModule: React.FC = () => {
    const [articles, setArticles] = useState<Article[]>([]);
    const [activeCategory, setActiveCategory] = useState<NewsCategory>('general');
    const [loading, setLoading] = useState(true);
    const [heroArticle, setHeroArticle] = useState<Article | null>(null);

    useEffect(() => {
        loadNews(activeCategory);
    }, [activeCategory]);

    const loadNews = async (category: NewsCategory) => {
        setLoading(true);
        const data = await fetchNews(category);

        if (data.length > 0) {
            setHeroArticle(data[0]);
            setArticles(data.slice(1));
        } else {
            setArticles([]);
        }
        setLoading(false);
    };

    return (
        <div className="chat-area news-module">
            <div className="news-sidebar">
                <div className="news-sidebar-header">
                    <h3>INTEL</h3>
                    <span className="news-live-badge">LIVE</span>
                </div>
                <div className="news-categories">
                    {NEWS_CATEGORIES.map(cat => (
                        <button
                            key={cat.id}
                            className={`news-cat-btn ${activeCategory === cat.id ? 'active' : ''}`}
                            onClick={() => setActiveCategory(cat.id)}
                        >
                            <span className="cat-icon">{cat.icon}</span>
                            <span className="cat-label">{cat.label}</span>
                        </button>
                    ))}
                </div>
            </div>

            <div className="news-feed">
                {/* Hero Section - "Glassmorphism Trust Hero" inspired */}
                {heroArticle && !loading && (
                    <div className="news-hero" onClick={() => window.open(heroArticle.url, '_blank')}>
                        <div className="hero-bg" style={{ backgroundImage: `url(${heroArticle.image})` }} />
                        <div className="hero-content">
                            <span className="hero-badge">DESTACADO // {activeCategory.toUpperCase()}</span>
                            <h1 className="hero-title">{heroArticle.title}</h1>
                            <p className="hero-desc">{heroArticle.description}</p>
                            <div className="hero-meta">
                                <span>{heroArticle.source.name}</span>
                                <span>•</span>
                                <span>{new Date(heroArticle.publishedAt).toLocaleDateString('es-ES')}</span>
                            </div>
                        </div>
                    </div>
                )}

                {/* Grid */}
                <div className="news-grid">
                    {loading ? (
                        <div className="news-loading">
                            <div className="spinner"></div>
                            <p>Analizando flujo de datos...</p>
                        </div>
                    ) : (
                        articles.map((article, idx) => (
                            <NewsCard key={`${article.url}-${idx}`} article={article} />
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};
