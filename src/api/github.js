// GitHub Activity Parser
export const fetchGitHubActivity = async (username) => {
    try {
        const response = await fetch(`https://api.github.com/users/${username}/events/public`);
        if (!response.ok) return [];

        const data = await response.json();
        if (!Array.isArray(data)) return [];

        return data.map(event => ({
            id: event.id,
            source: 'github',
            author: event.actor?.display_login ?? username,
            title: `[${event.type}] in ${event.repo?.name ?? 'unknown'}`,
            content: event.payload?.commits?.[0]?.message ?? 'Interaction event.',
            link: event.repo?.name ? `https://github.com/${event.repo.name}` : '#',
            timestamp: new Date(event.created_at),
            type: 'tooling'
        }));
    } catch (e) {
        console.error("GitHub Fetch Failed:", e);
        return [];
    }
};

