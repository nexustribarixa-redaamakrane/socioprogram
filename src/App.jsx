import Layout from './components/Layout';
import Feed from './components/Feed';
import { RuleContext } from './context/RuleContext';

export default function App() {
    return (
        <RuleContext.Provider value={{ sources: [{handle: 'programming', type: 'subreddit'}] }}>
            <Layout>
                <Feed />
            </Layout>
        </RuleContext.Provider>
    );
}
