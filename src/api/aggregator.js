import { fetchGitHubActivity } from './github';
import { fetchRedditNew } from './reddit';

/**
 * Orchestrates the data ingestion.
 * @param {Array} config - List of sources to track
 */
export const getAggregatedFeed = async (sources) => {
    const fetchPromises = sources.map(src => {
        if (src.type === 'github') return fetchGitHubActivity(src.handle);
        if (src.type === 'subreddit') return fetchRedditNew(src.handle);
        return [];
    });

    const results = await Promise.all(fetchPromises);
    
    // Merge all arrays into one and enforce Chronological Order
    return results.flat().sort((a, b) => b.timestamp - a.timestamp);
};
