export default function SourceTag({ type }) {
    const modifier = {
        subreddit: 'source-tag--subreddit',
        github: 'source-tag--github',
    };

    return (
        <span className={`source-tag ${modifier[type] || 'source-tag--default'}`}>
            {type}
        </span>
    );
}
