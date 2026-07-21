import { createContext } from 'react';

export const RuleContext = createContext({
    sources: [
        { handle: 'programming', type: 'subreddit' },
        { handle: 'google', type: 'github' }
    ],
    governance: {
        enforceChronological: true,
        blockAds: true
    }
});
