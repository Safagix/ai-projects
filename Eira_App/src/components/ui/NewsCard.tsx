
import React from 'react';
import { Article } from '../../services/news';

interface NewsCardProps {
    article: Article;
}

export const NewsCard: React.FC<NewsCardProps> = ({ article }) => {
    return (
        <div className="news-card" onClick={() => window.open(article.url, '_blank')}>
            <div className="news-image-container">
                <img
                    src={article.image || 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=2070&auto=format&fit=crop'}
                    alt={article.title}
                    className="news-image"
                    onError={(e) => { e.currentTarget.src = 'https://images.unsplash.com/photo-1585829365295-ab7cd400c167?q=80&w=2070&auto=format&fit=crop'; }}
                />
                <div className="news-overlay" />
                <span className="news-source-tag">{article.source.name}</span>
            </div>

            <div className="news-content">
                <div className="news-meta">
                    <span className="news-date">
                        {new Date(article.publishedAt).toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })}
                    </span>
                    <span className="news-time">
                        {new Date(article.publishedAt).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}
                    </span>
                </div>

                <h3 className="news-title">{article.title}</h3>
                <p className="news-desc">
                    {article.description?.length > 100
                        ? article.description.substring(0, 100) + '...'
                        : article.description}
                </p>

                <div className="news-footer">
                    <span className="read-more">Leer informe &rarr;</span>
                </div>
            </div>
        </div>
    );
};
