import { createContext } from 'react';

export const RuleContext = createContext({
    sources: [
        { handle: 'r/programming', type: 'subreddit' },
        { handle: 'google', type: 'github' } // Example source
    ],
    governance: {
        enforceChronological: true,
        blockAds: true
    }
});
