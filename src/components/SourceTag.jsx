export default function SourceTag({ type }) {
    const colors = {
        subreddit: 'text-orange-500 border-orange-500',
        github: 'text-blue-400 border-blue-400',
    };
    return (
        <span className={`px-1 text-[10px] font-mono uppercase border ${colors[type] || 'text-gray-500 border-gray-500'}`}>
            {type}
        </span>
    );
}
