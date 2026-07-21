import SourceTag from './SourceTag';

/**
 * Renders a single feed post card.
 * @param {{ data: { id: string, source: string, author: string, title: string, content: string, link: string, timestamp: Date, type: string } }} props
 */
export default function Post({ data }) {
    const timeLabel = data.timestamp instanceof Date && !isNaN(data.timestamp)
        ? data.timestamp.toLocaleString()
        : '';

    return (
        <article className="post-card">
            <div className="post-card__header">
                <SourceTag type={data.source} />
                <span className="post-card__author">{data.author}</span>
                <time className="post-card__timestamp" dateTime={data.timestamp?.toISOString?.()}>
                    {timeLabel}
                </time>
            </div>
            <h2 className="post-card__title">
                <a href={data.link} target="_blank" rel="noopener noreferrer">
                    {data.title}
                </a>
            </h2>
            {data.content && (
                <p className="post-card__content">{data.content}</p>
            )}
        </article>
    );
}
