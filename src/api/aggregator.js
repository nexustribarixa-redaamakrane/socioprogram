import { fetchGitHubActivity } from './github';
import { fetchRedditNew } from './reddit';

/**
 * Orchestrates the data ingestion.
 * @param {Array} sources - List of sources to track
 * @returns {Promise<Array>} Merged, chronologically sorted feed items
 */
export const getAggregatedFeed = async (sources) => {
    if (!Array.isArray(sources) || sources.length === 0) return [];

    const fetchPromises = sources.map(src => {
        if (src.type === 'github') return fetchGitHubActivity(src.handle);
        if (src.type === 'subreddit') return fetchRedditNew(src.handle);
        return Promise.resolve([]);
    });

    const results = await Promise.all(fetchPromises);

    // Merge all arrays into one and enforce Chronological Order
    return results.flat().sort((a, b) => b.timestamp - a.timestamp);
};

