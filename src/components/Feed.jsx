import { useState, useEffect, useContext } from 'react';
import { getAggregatedFeed } from '../api/aggregator';
import { RuleContext } from '../context/RuleContext';
import Post from './Post';

export default function Feed() {
    const { sources } = useContext(RuleContext);
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        let cancelled = false;
        setLoading(true);
        setError(null);

        getAggregatedFeed(sources)
            .then(data => {
                if (!cancelled) {
                    setPosts(data);
                    setError(null);
                }
            })
            .catch(err => {
                if (!cancelled) {
                    setPosts([]);
                    setError(err?.message || 'Failed to fetch feed');
                }
            })
            .finally(() => {
                if (!cancelled) setLoading(false);
            });

        return () => { cancelled = true; };
    }, [sources]);

    if (loading) {
        return (
            <section className="feed">
                <p className="feed__status feed__status--loading">Fetching feed</p>
            </section>
        );
    }

    if (error) {
        return (
            <section className="feed">
                <p className="feed__status feed__status--error">Error: {error}</p>
            </section>
        );
    }

    if (posts.length === 0) {
        return (
            <section className="feed">
                <p className="feed__status">No entries found in the registry.</p>
            </section>
        );
    }

    return (
        <section className="feed">
            {posts.map(post => <Post key={post.id} data={post} />)}
        </section>
    );
}
