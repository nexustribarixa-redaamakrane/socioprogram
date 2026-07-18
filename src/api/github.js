// GitHub Activity Parser
export const fetchGitHubActivity = async (username) => {
    try {
        const response = await fetch(`https://api.github.com/users/${username}/events/public`);
        const data = await response.json();

        return data.map(event => ({
            id: event.id,
            source: 'github',
            author: event.actor.display_login,
            title: `[${event.type}] in ${event.repo.name}`,
            content: event.payload.commits ? event.payload.commits[0].message : 'Interaction event.',
            link: `https://github.com/${event.repo.name}`,
            timestamp: new Date(event.created_at),
            type: 'tooling' // GitHub events default to tooling in this architecture
        }));
    } catch (e) {
        console.error("GitHub Fetch Failed:", e);
        return [];
    }
};
