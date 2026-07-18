// Reddit JSON Parser
export const fetchRedditNew = async (subreddit) => {
    try {
        const response = await fetch(`https://www.reddit.com/r/${subreddit}/new.json`);
        const json = await response.json();

        return json.data.children
            // Enforce Governance: Filter out advertisements
            .filter(child => !child.data.is_sponsored)
            .map(child => ({
                id: child.data.id,
                source: 'subreddit',
                author: child.data.author,
                title: child.data.title,
                content: child.data.selftext || child.data.url,
                link: `https://reddit.com${child.data.permalink}`,
                timestamp: new Date(child.data.created_utc * 1000),
                type: 'sneak-peek' // Reddit posts default to sneak-peek
            }));
    } catch (e) {
        console.error("Reddit Fetch Failed:", e);
        return [];
    }
};
