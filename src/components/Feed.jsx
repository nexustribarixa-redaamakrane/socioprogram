import { useState, useEffect, useContext } from 'react';
import { getAggregatedFeed } from '../api/aggregator';
import { RuleContext } from '../context/RuleContext';
import Post from './Post';

export default function Feed() {
    const { sources } = useContext(RuleContext);
    const [posts, setPosts] = useState([]);

    useEffect(() => {
        getAggregatedFeed(sources).then(setPosts);
    }, [sources]);

    return (
        <section className="max-w-2xl mx-auto">
            {posts.map(post => <Post key={post.id} data={post} />)}
        </section>
    );
}
